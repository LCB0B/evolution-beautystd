"""
Measurement evolution plotting for fashion industry data.
Script-based approach with minimal functions for clean, transparent code.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
import sys
import numpy as np
import json
import pickle
from matplotlib.patches import Patch
from scipy.signal import savgol_filter as _savgol

# Add the script directory so utils.py resolves
sys.path.insert(0, str(Path(__file__).parent))

# Import styling from utils
from utils import colors, cm

# Configuration
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

YEAR_START = 2000
YEAR_END = 2024

# Settings — one gender per run; the bottom of the file re-invokes the script
# for the other gender via the OC_GENDER environment variable.
gender = os.environ.get("OC_GENDER", "female")
if gender == "male":
    YEAR_START = 2010

CAREER_EVENTS = ['advertisements', 'magazine_covers', 'editorials']
MEASUREMENTS = ['bust-eu_clean', 'waist-eu_clean', 'hips-eu_clean', 'rfm']


def remove_spines(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

def add_trend_line(ax, x_data, y_data, color, alpha=0.3, degree=1,label=True):
    if len(x_data) < 3:
        return
    coeffs = np.polyfit(x_data, y_data, degree)
    poly_func = np.poly1d(coeffs)
    x_smooth = np.linspace(x_data.min(), x_data.max(), 100)
    y_smooth = poly_func(x_smooth)
    if label:
        #get the fit param
        fit_params = coeffs
        ax.plot(x_smooth, y_smooth, color=color, alpha=alpha, linewidth=1, linestyle='--', label=f'Trend: {fit_params[0]:.2f} per year')
    else:
        ax.plot(x_smooth, y_smooth, color=color, alpha=alpha, linewidth=1, linestyle='--')

def filter_years(df: pd.DataFrame, start: int | None, end: int | None, year_col: str = "year") -> pd.DataFrame:
    if df is None or df.empty:
        return df
    out = df.copy()
    if start is not None:
        out = out[out[year_col] >= start]
    if end is not None:
        out = out[out[year_col] <= end]
    return out

_MOMENTS_CACHE = {}


def _slim_moments(gender_key: str) -> pd.DataFrame:
    if gender_key not in _MOMENTS_CACHE:
        df = pd.read_csv(DATA / f"outliers_{gender_key}_eu_moments.csv")
        # Provide both an `iqr` column and `mean` (from the measurement-evolution
        # numeric CSV) so the main plotting block has everything in one frame.
        num_path = DATA / f"measurement_evolution_{gender_key}_eu_numeric.csv"
        num = pd.read_csv(num_path)[["event", "measurement", "year", "mean", "std"]]
        df = df.merge(num, on=["event", "measurement", "year"], how="left")
        _MOMENTS_CACHE[gender_key] = df
    return _MOMENTS_CACHE[gender_key]


def load_moments_data(career_event: str, gender: str) -> pd.DataFrame:
    """Return DF with columns year, measurement, mean, std, iqr, skewness,
    kurtosis, n, career_event for the requested event from the slim CSV."""
    df = _slim_moments(gender)
    sub = df[df["event"] == career_event].copy()
    sub = sub.rename(columns={"event": "career_event"})
    return sub[["year", "measurement", "mean", "std", "iqr", "skewness",
                 "kurtosis", "n", "career_event"]]

def shade_vertical(ax, y,color:list =['#dddddd', '#6baed6'], alpha: float = 0.08):
    #get the ylim
    ylim = ax.get_ylim()
    ax.axhspan(ylim[0], y, facecolor=color[0], alpha=alpha, zorder=0, linewidth=0)
    ax.axhspan(y, ylim[1], facecolor=color[1], alpha=alpha, zorder=0, linewidth=0)

def save_plot(fig, filename):
    fig.savefig(OUTPUT_DIR / f"{filename}.png", dpi=500, bbox_inches='tight')
    fig.savefig(OUTPUT_DIR / f"{filename}.pdf", bbox_inches='tight')
    print(f"Saved plot: {OUTPUT_DIR}/{filename}")


# Smoothing config
SMOOTH_ENABLED =True
SMOOTH_METHOD = "rolling"   # 'savgol' | 'rolling'
SMOOTH_WINDOW = 3        # odd, >= poly+2 (years)
SMOOTH_POLY = 1
SMOOTH_MIN_POINTS = 5
SMOOTH_ALPHA = 0.9
SMOOTH_LINESTYLE = '-'
SMOOTH_LINEWIDTH = 1.1

def smooth_series(x_vals, y_vals,
                  method=SMOOTH_METHOD,
                  window=SMOOTH_WINDOW,
                  poly=SMOOTH_POLY,
                  min_points=SMOOTH_MIN_POINTS):
    """
    Return (x_sorted, y_smoothed) or (None, None) if cannot smooth.
    """
    if x_vals is None or y_vals is None:
        return None, None
    x = np.asarray(x_vals, dtype=float)
    y = np.asarray(y_vals, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x = x[mask]
    y = y[mask]
    if x.size < min_points:
        return None, None
    # sort by x
    order = np.argsort(x)
    x = x[order]
    y = y[order]
    if method == "savgol" and _savgol is not None:
        # adjust window if larger than data
        w = min(window, x.size if x.size % 2 == 1 else x.size - 1)
        if w < 3:
            return None, None
        if w <= poly:
            poly = max(1, min(poly, w - 2))
        try:
            y_s = _savgol(y, window_length=w, polyorder=poly, mode='interp')
            return x, y_s
        except Exception:
            pass
    # fallback rolling mean
    if method in ("rolling", "savgol"):
        w = min(window, x.size)
        if w < 2:
            return None, None
        # uniform rolling with center alignment
        y_s = pd.Series(y).rolling(w, center=True, min_periods=max(2, w//2)).mean().to_numpy()
        # simple forward/backward fill of edge NaNs
        if np.isnan(y_s[0]):  # forward fill
            first_valid = np.nanmin(np.where(~np.isnan(y_s)))
            y_s[:first_valid] = y_s[first_valid]
        if np.isnan(y_s[-1]):  # backward fill
            last_valid = np.nanmax(np.where(~np.isnan(y_s)))
            y_s[last_valid+1:] = y_s[last_valid]
        return x, y_s
    return None, None



# Load and process NHANES and fashion model data for RFM comparison
def _load_nhanes_filtered(gender='female'):
    """Load NHANES data with age >= 17 and excluding pregnant women."""
    df = pd.read_csv(DATA / f"nhanes_rfm_{gender}_filtered.csv")
    df = df[df['Age'] >= 17]
    df = df[df['Pregnancy_Status'] != 1.0]
    return df

def load_nhanes_data(gender='female'):
    """Load NHANES RFM data for specified gender."""
    df = _load_nhanes_filtered(gender)
    print(f"NHANES data rows ({gender}): {len(df)}")
    return df['RFM'].dropna()

def load_nhanes_rfm_evolution(gender='female'):
    """Load NHANES RFM evolution data for specified gender."""
    df = _load_nhanes_filtered(gender)
    evolution = df.groupby('Year')['RFM'].agg(
        rfm_mean='mean', rfm_median='median', rfm_std='std', n='count'
    ).reset_index()
    return evolution


def load_fashion_model_rfm(gender='female'):
    """Load fashion model data and calculate RFM for specified gender.

    Args:
        gender: 'female' or 'male'

    RFM formulas:
        Female: RFM = 76 - 20 * (height_m / waist_m)
        Male: RFM = 64 - 20 * (height_m / waist_m)
    """
    try:
        # Slim shipped CSV already filtered to American models with valid RFM.
        models = pd.read_csv(DATA / f"models_rfm_{gender}.csv")
        return models['RFM'].dropna()
    except Exception:
        return None
# MAIN PLOTTING SCRIPT
print(f"Creating measurement evolution plot for {gender}...")

print("Loading data...")
all_data = []

fs_data = load_moments_data('fashion_shows', gender)
if not fs_data.empty:
    all_data.append(fs_data)

for event in CAREER_EVENTS:
    ev_df = load_moments_data(event, gender)
    if not ev_df.empty:
        all_data.append(ev_df)

if not all_data:
    print("No data found!")
    sys.exit(0)


data = pd.concat(all_data, ignore_index=True)
data = filter_years(data, YEAR_START, YEAR_END)
measurements = MEASUREMENTS


# Figure and grids
fig = plt.figure(figsize=(18*cm, 21*cm), layout='constrained')
gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.4, wspace=0.12, bottom=0.52, top=0.95, left=0, right=1,
                       width_ratios=[1, 1, 1, 1])
gs2 = gridspec.GridSpec(2, 1, figure=fig, hspace=0.4, wspace=0.35, bottom=0.1, top=0.4, left=0, right=0.48)

gs3 = gridspec.GridSpec(1, 1, figure=fig, hspace=0.4, wspace=0.35, bottom=0.25, top=0.4, left=0.48, right=1)

gs4 = gridspec.GridSpec(1, 4, figure=fig, hspace=0.4, wspace=0.35, bottom=0.1, top=0.24, left=0.48, right=1)

# Subplots
# Row 0: IQR (p75 - p25)
ax_iqr_1 = fig.add_subplot(gs[0,0])
ax_iqr_2 = fig.add_subplot(gs[0,1])
ax_iqr_3 = fig.add_subplot(gs[0,2])
ax_iqr_4 = fig.add_subplot(gs[0,3])

# Row 1: skewness
ax_sk_1 = fig.add_subplot(gs[1,0])
ax_sk_2 = fig.add_subplot(gs[1,1])
ax_sk_3 = fig.add_subplot(gs[1,2])
ax_sk_4 = fig.add_subplot(gs[1,3])

# Row 2: kurtosis
ax_ku_1 = fig.add_subplot(gs[2,0])
ax_ku_2 = fig.add_subplot(gs[2,1])
ax_ku_3 = fig.add_subplot(gs[2,2])
ax_ku_4 = fig.add_subplot(gs[2,3])

# NHANES
ax_small_1 = fig.add_subplot(gs2[0,0])
ax_small_2 = fig.add_subplot(gs2[1,0])

# PCA gs3
ax_pca = fig.add_subplot(gs3[0,0])

#gs4
ax_pca1 = fig.add_subplot(gs4[0,0])
ax_pca2 = fig.add_subplot(gs4[0,1])
ax_pca3 = fig.add_subplot(gs4[0,2])
ax_pca4 = fig.add_subplot(gs4[0,3])



iqr_axes  = [ax_iqr_1, ax_iqr_2, ax_iqr_3, ax_iqr_4]
skew_axes = [ax_sk_1,  ax_sk_2,  ax_sk_3,  ax_sk_4]
kurt_axes = [ax_ku_1,  ax_ku_2,  ax_ku_3,  ax_ku_4]

#set the

measurement_labels = ['Bust (cm)', 'Waist (cm)', 'Hips (cm)', 'RFM index']

# for ax in iqr_axes + skew_axes + kurt_axes:
#     shade_period(ax, 1995, 2018, color="#6baed6", alpha=0.2)
#     shade_period(ax, 2018, 2024, color="#f7b6d2", alpha=0.2)

# Plot each measurement: IQR (row 0), Skewness (row 1), Kurtosis (row 2)
for i, (measurement, label, ax_iqr, ax_sk, ax_ku) in enumerate(zip(measurements, measurement_labels, iqr_axes, skew_axes, kurt_axes)):
    mdf = data[data['measurement'] == measurement].copy()
    events_in_data = mdf['career_event'].unique()


        # Plot all events (fashion shows + career events)
    all_events = ['fashion_shows'] + CAREER_EVENTS
    color_idx = 0

    for event in all_events:
        if event not in events_in_data:
            continue
            
        # Get event data and styling
        edf = mdf[mdf['career_event'] == event].sort_values('year')
        if event == 'fashion_shows':
            color = '#07AB92'
            display_name = 'Fashion Shows'
        else:
            color = colors[color_idx % len(colors)]
            display_name = event.replace('_', ' ').title()
            color_idx += 1
        
        # Plot all three metrics with unified logic
        metrics_axes = [
            ('iqr', ax_iqr),
            ('skewness', ax_sk), 
            ('kurtosis', ax_ku)
        ]
        
        for metric, ax in metrics_axes:
            # Filter data for this metric
            metric_data = edf.dropna(subset=[metric])
            if metric_data.empty:
                continue
                
            # Plot raw data (if smoothing disabled)
            if not SMOOTH_ENABLED:
                ax.plot(metric_data['year'], metric_data[metric], 
                    color=color, linewidth=1.0, linestyle='-', 
                    alpha=1, label=display_name)
            
            # Plot smoothed data (if smoothing enabled)
            if SMOOTH_ENABLED:
                sx, sy = smooth_series(metric_data['year'], metric_data[metric])
                if sx is not None:
                    ax.plot(sx, sy, color=color, linestyle=SMOOTH_LINESTYLE,
                        linewidth=SMOOTH_LINEWIDTH, alpha=SMOOTH_ALPHA, 
                        label=display_name)

    # Styling helpers
    def _pad(l, u):
        if l is None or u is None or not np.isfinite([l, u]).all():
            return (0, 1)
        if np.isclose(l, u):
            d = max(0.05 * (abs(u) + 1), 0.05)
            return (l - d, u + d)
        pad = (u - l) * 0.15
        return (l - pad, u + pad)

    # Axis limits and labels
    for a, yl in ((ax_iqr, "IQR (p75 - p25)"), (ax_sk, "Skewness"), (ax_ku, "Kurtosis")):
        remove_spines(a)
        a.set_ylabel(f"{label} {yl}", rotation=0, labelpad=0, va='top', ha='left', x=0.0, y=1.10, fontsize=7)
        a.tick_params(axis='both', which='major', direction='in', length=3)
        a.tick_params(axis='both', which='minor', direction='in', length=1.5)
        if not mdf.empty:
            year_min, year_max = int(mdf['year'].min()), int(mdf['year'].max())
            a.set_xlim(year_min - 1, year_max + 1)

    # Dynamic y-lims per row
    if not mdf['iqr'].dropna().empty:
        l, u = float(mdf['iqr'].min()), float(mdf['iqr'].max())
        ax_iqr.set_ylim(*_pad(l, u))
        #ax_iqr.set_ylim(-0.1, 1.1)  # IQR is normalized to [0, 1]
    if not mdf['skewness'].dropna().empty:
        l, u = float(mdf['skewness'].min()), float(mdf['skewness'].max())
        ax_sk.set_ylim(*_pad(l, u))
    if not mdf['kurtosis'].dropna().empty:
        l, u = float(mdf['kurtosis'].min()), float(mdf['kurtosis'].max())
        ax_ku.set_ylim(*_pad(l, u))

# Add this after the dynamic y-lims section
ax_iqr_1.set_ylim(0, 7)    # Bust IQR
ax_iqr_2.set_ylim(0, 7)    # Waist IQR  
ax_iqr_3.set_ylim(0, 7)    # Hips IQR
ax_iqr_4.set_ylim(0, 7)    # RFM IQR

# Figure-level legend (remove duplicates)
handles, labels = ax_sk_1.get_legend_handles_labels()
if handles:
    for ax in iqr_axes + skew_axes + kurt_axes:
        lg = ax.get_legend()
        if lg:
            lg.remove()
    legend = fig.legend(handles, labels,
                        loc='upper center',
                        bbox_to_anchor=(0.5, 1.0),
                        ncol=min(6, len(labels)),
                        frameon=False,
                        columnspacing=4,
                        fontsize=7)
    for line in legend.get_lines():
        line.set_linewidth(2.0)

#set the kurt and skew ylim
ax_sk_1.set_ylim(-2, 7)
ax_sk_2.set_ylim(-2, 7)
ax_sk_3.set_ylim(-2, 7)   
ax_sk_4.set_ylim(-2, 7)

ax_ku_1.set_ylim(-5, 18)
ax_ku_2.set_ylim(-5, 45)
ax_ku_3.set_ylim(-5, 65)
ax_ku_4.set_ylim(-5, 21)

#  NHANES
nhanes_rfm = load_nhanes_data(gender)
models_rfm = load_fashion_model_rfm(gender)

if nhanes_rfm is not None and models_rfm is not None and len(nhanes_rfm) > 0 and len(models_rfm) > 0:
    ax_small_1.clear()
    
    # Create histograms
    bins = np.linspace(
        min(nhanes_rfm.min(), models_rfm.min()) - 2,
        max(nhanes_rfm.max(), models_rfm.max()) + 2,
        50
    )
    
    ax_small_1.hist(models_rfm, bins=bins, alpha=0.6, density=True,
                    label=f'US Model', 
                    color='lightcoral', edgecolor='darkred', linewidth=0.5)

    ax_small_1.hist(nhanes_rfm, bins=bins, alpha=0.6, density=True, 
                    label=f'US Population ', 
                    color='lightblue', edgecolor='darkblue', linewidth=0.5)
    
    
    
    # Add mean lines
    nhanes_mean = nhanes_rfm.mean()
    models_mean = models_rfm.mean()
    ax_small_1.axvline(nhanes_mean,ymax=1, color='darkblue', linestyle='--', linewidth=1, alpha=0.8)
    ax_small_1.axvline(models_mean,ymax=1, color='darkred', linestyle='--', linewidth=1, alpha=0.8)
    
    # Statistical test
    try:
        from scipy.stats import ttest_ind
        t_stat, p_value = ttest_ind(nhanes_rfm, models_rfm)
        stats_text = f'Δ={models_mean - nhanes_mean:.1f}\np={p_value:.2e}'
    except:
        stats_text = f'Δ={models_mean - nhanes_mean:.1f}'
    
    # Add text box with statistics
    # ax_small_1.text(0.02, 0.98, stats_text, transform=ax_small_1.transAxes, 
    #                 verticalalignment='top', fontsize=6, 
    #                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # ax_small_1.set_title('RFM Distribution (Females)', fontsize=8,)
    ax_small_1.set_xlabel('RFM (%)', fontsize=7)
    ax_small_1.set_ylabel('Density Relative Fat Mass Index (RFM)', fontsize=7,  rotation=0, labelpad=0, va='top', ha='left', x=0.0, y=1.10,)
    remove_spines(ax_small_1)
    ax_small_1.tick_params(axis='both', which='major', direction='in', length=3)
    ax_small_1.tick_params(axis='both', which='minor', direction='in', length=1.5)
    #xlim
    ax_small_1.set_xlim(7, 55)

else:
    ax_small_1.text(0.5, 0.5, "RFM data\nnot available", ha="center", va="center", fontsize=8)
    ax_small_1.set_title("RFM Comparison", fontsize=8)
    remove_spines(ax_small_1)

rfm_nhanes = load_nhanes_rfm_evolution(gender)
x_nhanes = rfm_nhanes['Year'].to_numpy()
y_nhanes = rfm_nhanes['rfm_mean'].to_numpy()

rfm_model = data[data['measurement'] == 'rfm'].copy()
#sort by year
rfm_model = rfm_model.sort_values('year')
#keep only the mean
rfm_model = rfm_model[['year', 'mean']].dropna().drop_duplicates(subset=['year'])
x_model = rfm_model['year'].to_numpy()
y_model = rfm_model['mean'].to_numpy()

y_nhanes_interp = np.interp(x_model, x_nhanes, y_nhanes)

plot_diff=True
if plot_diff:
    y_diff = y_nhanes_interp - y_model
    ax_small_2.plot(x_model, y_diff,  '.',color='k', linewidth=1, alpha=0.8,label=r'$\Delta(RFM_{\text{NHANES}}-RFM_{\text{Models}})$',markersize=3)
    #add trend
    add_trend_line(ax_small_2, x_model, y_diff, 'k', alpha=0.5)
    y_0 = np.min(y_diff)-0.5
    #ax_small_2.fill_between(x_model, y_0, y_diff, where=(y_diff > 0), color="lightgrey", alpha=0.25)
    ax_small_2.set_xlabel('Year', fontsize=7)
    ax_small_2.set_ylabel(r'$\Delta(RFM)$', fontsize=7, rotation=0, labelpad=0, va='top', ha='left', x=0.0, y=1.10)
    ax_small_2.tick_params(axis='both', which='major', direction='in', length=3)
    ax_small_2.tick_params(axis='both', which='minor', direction='in', length=1.5)
    ax_small_2.set_xlim(2000, 2024.5)
    y_lim = ax_small_2.get_ylim()

    ax_small_2.set_ylim([y_0, y_lim[1]])
    #get legend and handle
    #add trend line to handle and legend
    ax_small_2.legend(loc='upper left', fontsize=7, frameon=False,bbox_to_anchor=(0.02, 1.1))
else:
    ax_small_2.plot(x_model, y_model, color='lightcoral', linestyle='-', linewidth=1.5, alpha=0.8)
    ax_small_2.plot(x_model, y_nhanes_interp, color='lightblue', linestyle='-', linewidth=1.5, alpha=0.8)
    #fill between in light beige
    # interpolate y_nhanes to the values of x
    ax_small_2.fill_between(x_model, y_model, y_nhanes_interp, where=(y_model < y_nhanes_interp), color="#ffe7c3", alpha=0.25)
    ax_small_2.set_xlabel('Year', fontsize=7)
    ax_small_2.set_ylabel(r'RFM index', fontsize=7, rotation=0, labelpad=0, va='top', ha='left', x=0.0, y=1.10)
    ax_small_2.tick_params(axis='both', which='major', direction='in', length=3)
    ax_small_2.tick_params(axis='both', which='minor', direction='in', length=1.5)
    ax_small_2.set_xlim(2000, 2024) 

#legend 
handles, labels = ax_small_1.get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.41, 0.49), ncol=min(1, len(labels)), frameon=False,fontsize=7)
fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.93, 0.49), ncol=min(1, len(labels)), frameon=False,fontsize=7)

remove_spines(ax_small_1)
remove_spines(ax_small_2)

handles, labels = ax_iqr.get_legend_handles_labels()
if handles:
    for ax in iqr_axes:
        lg = ax.get_legend()
        if lg:
            lg.remove()
    legend = fig.legend(handles, labels,
                        loc='upper center',
                        bbox_to_anchor=(0.5, 1),
                        ncol=min(6, len(labels)),
                        frameon=False,
                        columnspacing=4,  
                        fontsize=7)
    for line in legend.get_lines():
        line.set_linewidth(2.0)


#print the mean and std for model and nhanes
if nhanes_rfm is not None and models_rfm is not None and len(nhanes_rfm) > 0 and len(models_rfm) > 0:
    print(f"NHANES RFM Mean: {nhanes_rfm.mean():.2f}, Std: {nhanes_rfm.std():.2f}")
    print(f"Models RFM Mean: {models_rfm.mean():.2f}, Std: {models_rfm.std():.2f}") 
        

#######    PCA — load from slim CSVs / JSON shipped in ../data/

with open(DATA / f"pca_{gender}_loadings.json", "r") as f:
    pca_bundle = json.load(f)
evr = pca_bundle["explained_variance_ratios"]
pc1_var, pc2_var, pc3_var, pc4_var = float(evr[0]), float(evr[1]), float(evr[2]), float(evr[3])
loadings = pca_bundle["loadings"]
variables = ["height-metric", "bust-eu", "waist-eu", "hips-eu"]
loading_pca1234 = {v: (float(loadings[v]["PC1"]), float(loadings[v]["PC2"]),
                         float(loadings[v]["PC3"]), float(loadings[v]["PC4"]))
                   for v in variables}

# Downsampled model PCA coords (PC1, PC2 only)
df = pd.read_csv(DATA / f"pca_{gender}_coords_sample.csv")
df.columns = [c.strip().lower() for c in df.columns]
for col in ("pc1", "pc2"):
    df[col] = pd.to_numeric(df[col], errors="coerce")
df = df.dropna(subset=["pc1", "pc2"])

# NHANES PCA projection
nhanes_pca = pd.read_csv(DATA / f"pca_nhanes_projection_{gender}.csv").dropna(subset=["PC1", "PC2"])

n_min = min(len(df), 20000)
indexes = np.random.randint(0, len(df), size=min(n_min, len(df)))
ax_pca.scatter(
    df["pc1"].values[indexes],
    df["pc2"].values[indexes],
    s=1, alpha=0.5, edgecolors="none", facecolors='lightcoral',
)
indexes_nhanes = np.random.randint(0, len(nhanes_pca), size=min(n_min, len(nhanes_pca)))
ax_pca.scatter(
    nhanes_pca["PC1"].values[indexes_nhanes],
    nhanes_pca["PC2"].values[indexes_nhanes],
    s=1, alpha=0.5, edgecolors="none", facecolors='lightblue',
)

# --- Build loadings in your order ---
feature_order = ['height-metric', 'bust-eu', 'waist-eu', 'hips-eu']
V = np.asarray([[loading_pca1234[f][k] for f in feature_order] for k in range(4)], dtype=float)

# Indices for RFM
idx_height = feature_order.index('height-metric')
idx_waist  = feature_order.index('waist-eu')

# Scaler means/scales loaded from JSON (replaces the .pkl scaler reads)
feature_means = np.asarray(pca_bundle["scaler_means"], dtype=float)
feature_scales = np.asarray(pca_bundle["scaler_scales"], dtype=float)

# Safety check
assert V.shape == (4, 4)
assert feature_means.shape == (4,) and feature_scales.shape == (4,)

def _scores_to_features(S, V, means, scales):
    means  = np.asarray(means,  dtype=float)
    if scales is None:
        Z = np.tensordot(S, V, axes=([S.ndim-1], [0]))         # (...,4)
        X = means + Z
    else:
        scales = np.asarray(scales, dtype=float)
        Z = np.tensordot(S, V, axes=([S.ndim-1], [0]))         # standardized features
        X = means + Z * scales
    return X

def add_rfm_contours_on_pc12(ax, V, means, scales=None, levels=None, n=250, pc3=0.0, pc4=0.0, manual_locations=None):
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    xx = np.linspace(x0, x1, n); yy = np.linspace(y0, y1, n)
    S1, S2 = np.meshgrid(xx, yy)
    S = np.stack([S1, S2, np.full_like(S1, pc3), np.full_like(S1, pc4)], axis=-1)  # (n,n,4)

    X = _scores_to_features(S, V, means, scales)
    H = X[..., idx_height]; W = X[..., idx_waist]

    with np.errstate(divide='ignore', invalid='ignore'):
        RFM = np.where(W > 0, 76.0 - 20.0 * (H / W), np.nan)

    if levels is None:
        finite = np.isfinite(RFM)
        if np.any(finite):
            rmin, rmax = np.nanpercentile(RFM[finite], [10, 90]); step = 2.5
            levels = np.arange(np.floor(rmin/step)*step, np.ceil(rmax/step)*step + 1e-9, step)
        else:
            levels = [20, 25, 30,35]

    grey = '0.35'  # grayscale string: 0=black, 1=white
    CS = ax.contour(S1, S2, RFM, levels=levels, linewidths=0.5, colors=grey, alpha=0.75)

    ax.clabel(CS, inline=True,  manual=manual_locations,fmt=lambda v: f"RFM={v:.0f}%", fontsize=5, colors=grey,inline_spacing=0.4)
    return CS


manual_locations = [
    (-5,-15),(3,-16),(15,-17),(43,-15)
]
# ---- Call AFTER your scatter + limits are set ----
_ = add_rfm_contours_on_pc12(
    ax=ax_pca,
    V=V,
    means=feature_means,
    scales=feature_scales,       # you used StandardScaler
    levels=[20, 30,40,50],     # or None to auto-pick
    n=300,
    pc3=0.0, pc4=0.0,
    manual_locations=manual_locations
)


# Indices for RFM
idx_height = feature_order.index('height-metric')
idx_waist  = feature_order.index('waist-eu')
ax_pca.set_xlabel(f"PC1")
ax_pca.set_ylabel(f"PC2")
ax_pca.set_aspect("equal", adjustable="box")
ax_pca.set_xlim(-8,55)
ax_pca.set_ylim(-21,7)


remove_spines(ax_pca)

#bar plot with CPS compoents.
color_bar = 'lightgrey'
x_ylabel = 0.25
y_ylabel = 1.12

ax_pca1.bar(variables, [loading_pca1234[v][0] for v in variables], color=color_bar, alpha=0.8)
ax_pca1.set_ylabel('PCA 1', rotation=0, labelpad=0, va='top', ha='left', x=x_ylabel, y=y_ylabel, fontsize=7)
ax_pca2.bar(variables, [loading_pca1234[v][1] for v in variables], color=color_bar, alpha=0.8)
ax_pca2.set_ylabel('PCA 2', rotation=0, labelpad=0, va='top', ha='left', x=x_ylabel, y=y_ylabel, fontsize=7)
ax_pca3.bar(variables, [loading_pca1234[v][2] for v in variables], color=color_bar, alpha=0.8)
ax_pca3.set_ylabel('PCA 3', rotation=0, labelpad=0, va='top', ha='left', x=x_ylabel, y=y_ylabel, fontsize=7)
ax_pca4.bar(variables, [loading_pca1234[v][3] for v in variables], color=color_bar, alpha=0.8)
ax_pca4.set_ylabel('PCA 4', rotation=0, labelpad=0, va='top', ha='left', x=x_ylabel, y=y_ylabel, fontsize=7)

#rename the labels to 'height', 'bust', 'waist', 'hips'
labels = ['Height', 'Bust', 'Waist', 'Hips']
for ax in (ax_pca1, ax_pca2, ax_pca3, ax_pca4):
    ax.axhline(0, color='k', linestyle='--', linewidth=0.8)
    #rotate the x-axis labels
    ax.set_xticklabels(labels, rotation=45, ha="right")
    remove_spines(ax)
    ax.set_ylim(-0.75,1)
    #inside ticks
    ax.tick_params(axis='y', direction='in', length=4)
    ax.tick_params(axis='x', direction='in', length=4)

#remove the y-labels tick for ax_pca2,ax_pca3,4
for ax in (ax_pca2, ax_pca3, ax_pca4):
    #ax.tick_params(axis='y', which='both', left=False, right=False)
    ax.set_yticklabels([])
filename = f"iqr_skew_kurtosis_{gender}_eu"

shade_color = ["#FFFFFF", "#C6C6C6"]
for ax in skew_axes:
    shade_vertical(ax, 0, color=shade_color, alpha=0.2)
for ax in kurt_axes:
    shade_vertical(ax, 0, color=shade_color, alpha=0.2)

plt.tight_layout()
gs.tight_layout(fig, pad=0.1)
gs.update(hspace=0.3, wspace=0.23, bottom=0.55, top=0.95, left=0, right=1)

gs2.tight_layout(fig, pad=0.1)
gs2.update(hspace=0.4, wspace=0.15, bottom=0.1, top=0.48, left=0, right=0.48)

gs3.tight_layout(fig, pad=0.1)
gs3.update(hspace=0, wspace=0.15, bottom=0.22, top=0.6, left=0.53, right=1)

gs4.tight_layout(fig, pad=0.1)
gs4.update(hspace=0, wspace=0.15, bottom=0.12, top=0.25, left=0.53, right=1)


plt.tight_layout()


#add the lettering to the subplots but place them globally
letters= ['a', 'b', 'c', 'd','e','f','g']

x_pos = [-0.028,0.505]
y_pos = [0.96,0.82,0.68,0.51,0.28]
font_panel_size = 10
#put a in x[0]. y[0], b x[0], y[1], c x[0], y[2], d x[0], y[3], e x[0], y[4], f x[1], y[3], g x[1], y[4]
fig.text(x_pos[0], y_pos[0], letters[0], fontsize=font_panel_size, fontweight='bold')
fig.text(x_pos[0], y_pos[1], letters[1], fontsize=font_panel_size, fontweight='bold')
fig.text(x_pos[0], y_pos[2], letters[2], fontsize=font_panel_size, fontweight='bold')
fig.text(x_pos  [0], y_pos[3], letters[3], fontsize=font_panel_size, fontweight='bold')
fig.text(x_pos[0], y_pos[4], letters[4], fontsize=font_panel_size, fontweight='bold')
fig.text(x_pos[1], y_pos[3], letters[5], fontsize=font_panel_size, fontweight='bold')
fig.text(x_pos[1], y_pos[4], letters[6], fontsize=font_panel_size, fontweight='bold')

save_plot(fig, filename)
plt.show()
plt.close()
print("Done!")

# Regenerate the male variant when the script is run for the default female case
if os.environ.get("OC_GENDER") is None and gender == "female":
    import subprocess
    env = {**os.environ, "OC_GENDER": "male"}
    subprocess.run([sys.executable, __file__], env=env, check=False)

