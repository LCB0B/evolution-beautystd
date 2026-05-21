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
from matplotlib.patches import Patch
from math import sqrt
from scipy.stats import chi2

# Add the script directory to the path so utils.py resolves
sys.path.insert(0, str(Path(__file__).parent))

# Import styling from utils
from utils import colors, cm

# Configuration
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

YEAR_START = 2000
YEAR_END = 2026

# One gender per execution. The bottom of the file re-invokes the script for
# the other gender via the ME_GENDER environment variable.
gender = os.environ.get("ME_GENDER", "female")
if gender == 'male':
    YEAR_START = 2010

CAREER_EVENTS = ['advertisements', 'magazine_covers', 'editorials']
MEASUREMENTS = ['height_cm', 'bust-eu_clean', 'waist-eu_clean', 'hips-eu_clean', 'rfm']

HAIR_COLOR_MAPPING = {
    'red / brown': 'auburn',
    'brown / red': 'auburn',
    'auburn': 'auburn',
    'red / blonde': 'blonde red',
    'red blonde': 'blonde red',
    'blonde / red': 'blonde red',
    'light red': 'blonde red',
}

EYE_COLOR_MAPPING = {
    'brown / green': 'brown / green',
    'green / brown': 'brown / green',
    'dark green': 'green / grey',
}

def remove_spines(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

def filter_years(df: pd.DataFrame, start: int | None, end: int | None, year_col: str = "year") -> pd.DataFrame:
    if df is None or df.empty:
        return df
    out = df.copy()
    if start is not None:
        out = out[out[year_col] >= start]
    if end is not None:
        out = out[out[year_col] <= end]
    return out

# Load from slim CSVs in ../data/  (replaces the original JSON loaders)
# Module-level slim-CSV cache populated lazily per gender.
_NUM_CACHE = {}
_CAT_CACHE = {}


def _slim_numeric(gender_key):
    if gender_key not in _NUM_CACHE:
        _NUM_CACHE[gender_key] = pd.read_csv(
            DATA / f"measurement_evolution_{gender_key}_eu_numeric.csv")
    return _NUM_CACHE[gender_key]


def _slim_categorical(gender_key):
    if gender_key not in _CAT_CACHE:
        _CAT_CACHE[gender_key] = pd.read_csv(
            DATA / f"measurement_evolution_{gender_key}_eu_categorical.csv")
    return _CAT_CACHE[gender_key]


def _numeric_for_event(event_key: str, gender_key: str) -> pd.DataFrame:
    """Return DF with columns year, measurement, mean, std, n, career_event."""
    df = _slim_numeric(gender_key)
    sub = df[df["event"] == event_key][["year", "measurement", "mean", "std", "n"]].copy()
    sub["career_event"] = event_key
    return sub


def _categorical_for_event(event_key: str, gender_key: str, var_key: str,
                              value_col: str) -> pd.DataFrame:
    """Return DF with columns year, <value_col>, proportion, count, total_count,
    career_event for a given event_key, gender, and categorical variable."""
    df = _slim_categorical(gender_key)
    sub = df[(df["event"] == event_key) & (df["variable"] == var_key)].copy()
    if sub.empty:
        return pd.DataFrame()
    sub = sub.rename(columns={"value": value_col})
    sub["career_event"] = event_key
    return sub[["year", value_col, "proportion", "count", "total_count", "career_event"]]

def load_data(career_event, gender):
    """Load measurement (mean/std/n by year) for an event from the slim CSV."""
    return _numeric_for_event(career_event, gender)


def load_hair_color_data(career_event, gender):
    df = _categorical_for_event(career_event, gender, "hair", "hair_color")
    if df.empty:
        return df
    df["hair_color"] = df["hair_color"].map(HAIR_COLOR_MAPPING).fillna(df["hair_color"])
    df = df.groupby(["year", "hair_color", "career_event"], as_index=False).agg(
        proportion=("proportion", "sum"),
        count=("count", "sum"),
        total=("total_count", "first"),
    ).rename(columns={"total": "total_count"})
    return df


def load_eye_color_data(career_event, gender):
    df = _categorical_for_event(career_event, gender, "eyes", "eye_color")
    if df.empty:
        return df
    df["eye_color"] = df["eye_color"].map(EYE_COLOR_MAPPING).fillna(df["eye_color"])
    df = df.groupby(["year", "eye_color", "career_event"], as_index=False).agg(
        proportion=("proportion", "sum"),
        count=("count", "sum"),
        total=("total_count", "first"),
    ).rename(columns={"total": "total_count"})
    return df


def load_nationality_data(career_event, gender):
    return _categorical_for_event(career_event, gender, "world_region", "region")

def plot_world_region_proportions(ax, nationality_data, region_color_map, start_year=None, end_year=None, ylabel='World Region Proportion'):
    """Plot stacked proportions for 16 world regions. Returns plotted labels (lowercase) in draw order."""
    if nationality_data is None or nationality_data.empty:
        ax.text(0.5, 0.5, 'No region data', transform=ax.transAxes, ha='center', va='center', fontsize=10)
        remove_spines(ax)
        return []

    # Filter and normalize
    df = nationality_data.copy()
    if 'year' not in df.columns or 'region' not in df.columns or 'proportion' not in df.columns:
        ax.text(0.5, 0.5, 'Region data missing columns', transform=ax.transAxes, ha='center', va='center', fontsize=10)
        remove_spines(ax)
        return []

    if start_year is not None or end_year is not None:
        df = filter_years(df, start_year, end_year)

    if df.empty:
        ax.text(0.5, 0.5, 'No region data in year range', transform=ax.transAxes, ha='center', va='center', fontsize=10)
        remove_spines(ax)
        return []

    df['region'] = df['region'].astype(str).str.lower()

    # Pivot to get proportions by year
    pivot = df.pivot_table(index='year', columns='region', values='proportion', fill_value=0)
    pivot = pivot.sort_index()
    if pivot.empty:
        ax.text(0.5, 0.5, 'No region data after pivot', transform=ax.transAxes, ha='center', va='center', fontsize=10)
        remove_spines(ax)
        return []

    # Normalize color map keys to lowercase
    cmap = {str(k).lower(): v for k, v in region_color_map.items()}
    cols_ordered = [k for k in cmap.keys() if k in pivot.columns][::-1]  # reverse for stacking order

    years = pivot.index.values
    bottoms = np.zeros(len(years))
    plotted_labels = []

    for key in cols_ordered:
        heights = pivot[key].values
        color = cmap.get(key, '#CCCCCC')
        ax.bar(years, heights, width=1, bottom=bottoms, color=color, alpha=1, edgecolor='none')
        bottoms += heights
        plotted_labels.append(key)

    # Style
    ax.set_xlabel('Year')
    ax.set_ylabel(ylabel, rotation=0, labelpad=0, va='top', ha='left', x=0.1, y=1.1, fontsize=7)
    ax.set_ylim(0, 1)
    ax.set_xlim(years[0] - 0.5, years[-1] + 0.5)
    ax.tick_params(axis='both', which='major', direction='in', length=3)
    ax.tick_params(axis='both', which='minor', direction='in', length=1.5)
    remove_spines(ax)

    return plotted_labels

# --- STD CI helper -----------------------------------------------------------
def std_confidence_interval(s: float, n: int, alpha: float = 0.05):
    """
    Return (sd_lower, sd_upper) 95% CI bounds for true sigma using chi-square.
    If scipy not available or invalid n, returns (nan, nan).
    """
    if chi2 is None or n is None or n < 3 or not np.isfinite(s) or s < 0:
        return np.nan, np.nan
    df = n - 1
    # chi2 lower/upper quantiles
    chi2_lower = chi2.ppf(alpha/2, df)
    chi2_upper = chi2.ppf(1 - alpha/2, df)
    if not np.isfinite(chi2_lower) or not np.isfinite(chi2_upper) or chi2_lower <= 0 or chi2_upper <= 0:
        return np.nan, np.nan
    var_lower = (df * s**2) / chi2_upper
    var_upper = (df * s**2) / chi2_lower
    return sqrt(var_lower), sqrt(var_upper)

# Plot helpers
def plot_stacked_proportions(ax, data, color_map, ylabel='Proportion'):
    plotted_labels = []
    if data.empty:
        ax.text(0.5, 0.5, 'No data available', transform=ax.transAxes,
                ha='center', va='center', fontsize=10)
        remove_spines(ax)
        return plotted_labels

    # Determine color column
    if 'hair_color' in data.columns:
        color_column = 'hair_color'
    elif 'eye_color' in data.columns:
        color_column = 'eye_color'
    else:
        color_column = 'region'

    # Pivot to proportions by year
    try:
        pivot_data = data.pivot_table(index='year', columns=color_column,
                                      values='proportion', fill_value=0)
        pivot_data = pivot_data.sort_index()  # ensure chronological
    except Exception as e:
        print(f"Error pivoting color data: {e}")
        ax.text(0.5, 0.5, 'Error processing data', transform=ax.transAxes,
                ha='center', va='center', fontsize=10)
        remove_spines(ax)
        return plotted_labels

    if pivot_data.empty:
        ax.text(0.5, 0.5, 'No pivot data', transform=ax.transAxes,
                ha='center', va='center', fontsize=10)
        remove_spines(ax)
        return plotted_labels

    pivot_data.columns = [str(c).lower() for c in pivot_data.columns]
    color_map_norm = {str(k).lower(): v for k, v in color_map.items()}

    years = pivot_data.index
    bottoms = np.zeros(len(years))

    # Order by color map and reverse for stack draw order
    ordered = [c for c in color_map.keys() if c in pivot_data.columns][::-1]
    for cat in ordered:
        color = color_map.get(cat, '#CCCCCC')
        heights = pivot_data[cat].values
        ax.bar(years, heights, width=1, bottom=bottoms, color=color, alpha=1, edgecolor='none',linewidth=0)
        bottoms += heights
        plotted_labels.append(cat)

    ax.set_xlabel('Year')
    ax.set_ylabel(ylabel, rotation=0, labelpad=0, va='top', ha='left', x=0.1, y=1.1, fontsize=7)
    ax.set_ylim(0, 1)
    ax.set_xlim(years[0] - 0.5, years[-1] + 0.5)
    ax.tick_params(axis='both', which='major', direction='in', length=3)
    ax.tick_params(axis='both', which='minor', direction='in', length=1.5)
    remove_spines(ax)
    return plotted_labels

def save_plot(fig, filename):
    fig.savefig(OUTPUT_DIR / f"{filename}.png", dpi=300, bbox_inches='tight')
    fig.savefig(OUTPUT_DIR / f"{filename}.pdf", bbox_inches='tight')
    print(f"Saved plot: {OUTPUT_DIR}/{filename}")
# MAIN PLOTTING SCRIPT
print(f"Creating measurement evolution plot for {gender}...")

print(f"Loading data for gender: {gender}...")
all_data = []

fs_data = load_data('fashion_shows', gender)
if not fs_data.empty:
    print(f"  Fashion shows: {len(fs_data)} data points")
    all_data.append(fs_data)
else:
    print(f"  Fashion shows: No data for {gender}")

for event in CAREER_EVENTS:
    ev_df = load_data(event, gender)
    if not ev_df.empty:
        print(f"  {event}: {len(ev_df)} data points")
        all_data.append(ev_df)
    else:
        print(f"  {event}: No data for {gender}")

if not all_data:
    print(f"No data found for gender: {gender}!")
    sys.exit(0)

data = pd.concat(all_data, ignore_index=True)
data = filter_years(data, YEAR_START, YEAR_END)
measurements = MEASUREMENTS

if gender == 'male': #add 12 to RFM
    data.loc[data['measurement'] == 'rfm', 'mean'] += 12

print(f"Loading hair, eye color, and nationality data for {gender}...")
hair_data = load_hair_color_data('fashion_shows', gender)
eye_data = load_eye_color_data('fashion_shows', gender)
nationality_data = load_nationality_data('fashion_shows', gender)

hair_data = filter_years(hair_data, YEAR_START, YEAR_END)
eye_data = filter_years(eye_data, YEAR_START, YEAR_END)
nationality_data = filter_years(nationality_data, YEAR_START, YEAR_END)

# Define color maps
hair_color_map = {
    'black': '#2F2F2F',
    'dark brown': '#654321',
    'brown': '#8B4513',
    'chestnut': '#954535',
    'auburn': '#A0522D',
    'red': "#CF7302",
    'grey': '#808080',
    'light brown': "#C39C39",
    'dark blonde': "#D5AB50",
    'blonde red': '#CD853F',
    'blonde': '#F4E28C',
    'light blonde': '#FFF8DC',
    'bald': '#E6E6FA',
    'white': '#F5F5F5',
}

eye_color_map = {
    'black': '#2F2F2F',
    'dark brown': '#654321',
    'blue / brown': '#483D8B',
    'brown': '#8B4513',
    'brown / hazel': '#8B7355',
    'light brown': '#D2B48C',
    'hazel': '#8E7618',
    'green / grey': '#2F4F4F',
    'green / brown': '#556B2F',
    'brown / green': '#556B2F',
    'green / hazel': '#6B8E23',
    'green': '#228B22',
    'blue / green': '#008B8B',
    'blue': '#4169E1',
    'blue / grey': '#6495ED',
    'grey': '#708090',
}

# Region and Global maps
region_color_map = {
    'Southeast Asia': '#FF7DBE',
    'South Asia': '#F1C40F',
    'Middle East': '#8E44AD',
    'North Africa': '#E67E22',
    'Sub-Saharan Africa': "#840202",
    'Oceania': '#3498DB',
    'Central Asia': '#9B59B6',
    'East Asia': "#91F378",
    'Caribbean': "#F0F338",
    'Central America': "#C12ECC",
    'South America': '#07AB92',
     'Northern Europe': "#3FACEF",
    'Southern Europe': "#EF970A",
    'North America': "#D81F1F",
    'Western Europe': "#0512A3",
    'Eastern Europe': "#22B2F5",
}

# Figure and grids
fig = plt.figure(figsize=(18*cm, 16*cm),layout='constrained')
gs = gridspec.GridSpec(2, 5, figure=fig, hspace=0.4, wspace=0.1, bottom=0.5, top=0.95, left=0, right=1)
gs2 = gridspec.GridSpec(1, 3, figure=fig, hspace=0.4, wspace=0.65, bottom=0.1, top=0.4, left=0, right=0.86)

# Subplots
ax1 = fig.add_subplot(gs[0,0])  # height
ax2 = fig.add_subplot(gs[0,1])  # bust
ax3 = fig.add_subplot(gs[0,2])  # waist
ax4 = fig.add_subplot(gs[0,3])  # hips
ax5 = fig.add_subplot(gs[0,4])  # RFM 

ax1_std = fig.add_subplot(gs[1,0])
ax2_std = fig.add_subplot(gs[1,1])
ax3_std = fig.add_subplot(gs[1,2])
ax4_std = fig.add_subplot(gs[1,3])
ax5_std = fig.add_subplot(gs[1,4])

ax_hair   = fig.add_subplot(gs2[0,0])
ax_eye    = fig.add_subplot(gs2[0,1])
ax_global = fig.add_subplot(gs2[0,2])

axes = [ax1, ax2, ax3, ax4, ax5]
std_axes = [ax1_std, ax2_std, ax3_std, ax4_std, ax5_std]

# Share y for std axes
for ax in std_axes:
    ax.sharey(ax1_std)

measurement_labels = ['Height (cm)', 'Bust (cm)', 'Waist (cm)', 'Hips (cm)', 'RFM index']

# Adjust y-limits based on gender
if gender == 'female':
    height_ylim = (174.7, 181)
    bust_ylim   = (78.5, 88)
    waist_ylim  = (58.5, 63)
    hips_ylim   = (85.5, 91)
    rfm_ylim    = (14.5, 20)
else:  # 'male'
    height_ylim = (175, 190)
    bust_ylim   = (77, 95)
    waist_ylim  = (57, 77)
    hips_ylim   = (82, 95)
    rfm_ylim    = (14, 30)

y_lims = [height_ylim, bust_ylim, waist_ylim, hips_ylim, rfm_ylim]

# Plot each measurement - SAME PLOTTING CODE BUT NOW WITH GENDER-SPECIFIC DATA
for i, (measurement, label, ax, ax_std) in enumerate(zip(measurements, measurement_labels, axes, std_axes)):
    mdf = data[data['measurement'] == measurement]
    events_in_data = mdf['career_event'].unique()

    # fashion shows first
    if 'fashion_shows' in events_in_data:
        fs = mdf[mdf['career_event'] == 'fashion_shows'].sort_values('year')
        if not fs.empty:
            # Interpolate mean/std only (avoid n interpolation)
            if fs['mean'].isna().any():
                fs['mean'] = fs['mean'].replace([-np.inf, np.inf], np.nan).interpolate()
            if fs['std'].isna().any():
                fs['std'] = fs['std'].replace([-np.inf, np.inf], np.nan).interpolate()

            ax.plot(fs['year'], fs['mean'], color='#07AB92', linewidth=1.0, linestyle='-', label='Fashion Shows', alpha=1)
            ax_std.plot(fs['year'], fs['std'],  color='#07AB92', linewidth=1.0, linestyle='-', label='Fashion Shows', alpha=1.0)

            # --- Mean uncertainty band (± standard error) ---
            if 'n' in fs.columns:
                sem = fs.apply(lambda r: r['std']/sqrt(r['n']) if (pd.notna(r['std']) and r.get('n') and r['n'] > 1) else np.nan, axis=1)
                mean_lower = fs['mean'] - sem
                mean_upper = fs['mean'] + sem
                ax.fill_between(fs['year'], mean_lower, mean_upper,
                                color='#07AB92', alpha=0.18, linewidth=0)

            # --- Std deviation CI (chi-square) as asymmetric uncertainty bands
            if 'n' in fs.columns:
                sd_lower_bounds = []
                sd_upper_bounds = []
                for s_val, n_val in zip(fs['std'], fs['n']):
                    lo, hi = std_confidence_interval(s_val, n_val, alpha=0.05)
                    sd_lower_bounds.append(lo)
                    sd_upper_bounds.append(hi)
                sd_lower_bounds = np.array(sd_lower_bounds)
                sd_upper_bounds = np.array(sd_upper_bounds)
                lower_err =  sd_lower_bounds
                upper_err = sd_upper_bounds 
                lower_err[~np.isfinite(lower_err) | (lower_err < 0)] = np.nan
                upper_err[~np.isfinite(upper_err) | (upper_err < 0)] = np.nan
                ax_std.fill_between(fs['year'], lower_err, upper_err,
                                    color='#07AB92', alpha=0.18, linewidth=0)

    # other events
    color_idx = 0
    for event in CAREER_EVENTS:
        if event in events_in_data:
            edf = mdf[mdf['career_event'] == event].sort_values('year')
            if edf.empty:
                continue
            if edf['mean'].isna().any():
                edf['mean'] = edf['mean'].replace([-np.inf, np.inf], np.nan).interpolate()
            if edf['std'].isna().any():
                edf['std'] = edf['std'].replace([-np.inf, np.inf], np.nan).interpolate()

            display_name = event.replace('_', ' ').title()
            c = colors[color_idx % len(colors)]
            ax.plot(edf['year'], edf['mean'], color=c, linewidth=1, linestyle='-', alpha=1, label=display_name)
            ax_std.plot(edf['year'], edf['std'],  color=c, linewidth=1, linestyle='-', alpha=1, label=display_name)

            # Mean uncertainty band
            if 'n' in edf.columns:
                sem = edf.apply(lambda r: r['std']/sqrt(r['n']) if (pd.notna(r['std']) and r.get('n') and r['n'] > 1) else np.nan, axis=1)
                mean_lower = edf['mean'] - sem
                mean_upper = edf['mean'] + sem
                ax.fill_between(edf['year'], mean_lower, mean_upper,
                                color=c, alpha=0.18, linewidth=0)

            # Std CI uncertainty band
            if 'n' in edf.columns:
                sd_lower_bounds = []
                sd_upper_bounds = []
                for s_val, n_val in zip(edf['std'], edf['n']):
                    lo, hi = std_confidence_interval(s_val, n_val, alpha=0.05)
                    sd_lower_bounds.append(lo)
                    sd_upper_bounds.append(hi)
                sd_lower_bounds = np.array(sd_lower_bounds)
                sd_upper_bounds = np.array(sd_upper_bounds)
                lower_err = sd_lower_bounds
                upper_err = sd_upper_bounds 
                lower_err[~np.isfinite(lower_err) | (lower_err < 0)] = np.nan
                upper_err[~np.isfinite(upper_err) | (upper_err < 0)] = np.nan
                ax_std.fill_between(edf['year'], lower_err, upper_err,
                                    color=c, alpha=0.18, linewidth=0)

            color_idx += 1

    # Styling numeric panels
    ax.set_ylim(y_lims[i])
    remove_spines(ax)
    ax.set_ylabel(f'{label}', rotation=0, labelpad=0, va='top', ha='left', x=0.1, y=1.15, fontsize=7)
    ax.tick_params(axis='both', which='major', direction='in', length=3)
    ax.tick_params(axis='both', which='minor', direction='in', length=1.5)

    # X limits
    mdf = data[data['measurement'] == measurement]
    if not mdf.empty:
        year_min = mdf['year'].min()
        year_max = mdf['year'].max()
        ax.set_xlim(year_min - 1, year_max + 1)
        ax_std.set_xlim(year_min - 1, year_max + 1)

    # Std panels
    remove_spines(ax_std)
    ax_std.set_xlabel('Year', labelpad=0, va='top', ha='center')
    ax_std.set_ylabel(f'{label} Std. Dev.', rotation=0, labelpad=0, va='top', ha='left', x=0.1, y=1.15, fontsize=7)
    ax_std.set_facecolor("#f5f5f5")
    ax_std.tick_params(axis='both', which='major', direction='in', length=3)
    ax_std.tick_params(axis='both', which='minor', direction='in', length=1.5)

ax1_std.set_ylim(1.3, 5.8)
if gender == 'male':
    ax1_std.set_ylim(0, 13)
# Stacked proportions: hair, eyes, global N/S - NOW GENDER-SPECIFIC
hair_labels = plot_stacked_proportions(ax_hair, hair_data, hair_color_map, ylabel='Hair Color Proportion')
eye_labels = plot_stacked_proportions(ax_eye, eye_data, eye_color_map, ylabel='Eye Color Proportion')

# World region proportions (16 regions) - NOW GENDER-SPECIFIC
if not nationality_data.empty:
    region_labels = plot_world_region_proportions(ax_global, nationality_data, region_color_map, YEAR_START, YEAR_END)
else:
    ax_global.text(0.5, 0.5, 'No world region data available', transform=ax_global.transAxes,
                   ha='center', va='center', fontsize=10)
    region_labels = []

# Figure-level legend (numeric panels)
handles, labels = ax1.get_legend_handles_labels()
if handles:
    for ax in axes + std_axes:
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

# Single-column legends for hair/eye/global
if hair_labels:
    hair_handles = [Patch(facecolor=hair_color_map[l], edgecolor='none') for l in hair_labels]
    ax_hair.legend(hair_handles[::-1], hair_labels[::-1],
                   loc='center left', bbox_to_anchor=(1.01, 0.5),
                   frameon=False, ncol=1, fontsize=6, borderaxespad=0.0,facecolor="#eaeaea",edgecolor="none",
                   labelspacing=0.5, handlelength=1.4, handleheight=1.4, handletextpad=0.4, borderpad=0.2)

if eye_labels:
    eye_handles = [Patch(facecolor=eye_color_map[l], edgecolor='none') for l in eye_labels]
    ax_eye.legend(eye_handles[::-1], eye_labels[::-1],
                  loc='center left', bbox_to_anchor=(1.01, 0.5),
                  frameon=False, ncol=1, fontsize=6, borderaxespad=0.0,facecolor="#eaeaea",edgecolor="none",
                  labelspacing=0.38, handlelength=1.4, handleheight=1.4, handletextpad=0.4, borderpad=0.2)

if region_labels:
    norm_region_map = {k.lower(): v for k, v in region_color_map.items()}
    region_handles = [Patch(facecolor=norm_region_map.get(l, '#CCCCCC'), edgecolor='none') for l in region_labels]
    ax_global.legend(region_handles[::-1], [l.title() for l in region_labels[::-1]],
                    loc='center left', bbox_to_anchor=(1.01, 0.5),
                    frameon=False, ncol=1, fontsize=6, borderaxespad=0.0,facecolor="#eaeaea",edgecolor="none",
                    labelspacing=0.27, handlelength=1.4, handleheight=1.4, handletextpad=0.4, borderpad=0.2)

filename = f"measurements_evolution_with_std_{YEAR_START}_{gender}_eu"

gs.tight_layout(fig, pad=0.1)
gs.update(hspace=0.3, wspace=0.15, bottom=0.5, top=0.92, left=0, right=1)

gs2.tight_layout(fig, pad=0.1)
gs2.update(hspace=0.4, wspace=0.65, bottom=0.1, top=0.4, left=0, right=0.86)

plt.tight_layout()
save_plot(fig, filename)
plt.close()
print("Done!")

# Regenerate the other gender automatically (no-op if already running for male).
if os.environ.get("ME_GENDER") is None and gender == "female":
    import subprocess
    env = {**os.environ, "ME_GENDER": "male"}
    subprocess.run([sys.executable, __file__], env=env, check=False)