"""RFM by age group: fashion models vs NHANES women (raw + age-matched).

Reads:
  ../data/rfm_by_age_group_models_hist.csv     (age_int, rfm_bin_left, rfm_bin_right, count)
  ../data/rfm_by_age_group_models_medians.csv  (age_group, age_low, age_high, median_rfm, n)
  ../data/nhanes_female_17_40.csv              (Age, RFM, age_int)
Writes:
  ../figures/rfm_by_age_group.{png,pdf}
  ../figures/rfm_by_age_group_matched.{png,pdf}

The model side is shipped as a pre-binned histogram (per integer age × per RFM
bin) plus the per-age-group exact median, so no individual model records are
distributed. NHANES is public NHANES survey data.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from utils import cm, FIGURE_WIDTH_CM, setup_panel, save_figure

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"; FIG.mkdir(exist_ok=True)

AGE_GROUPS = [(17, 20), (21, 25), (26, 30), (31, 40)]
AGE_LABELS = ["17-20", "21-25", "26-30", "31-40"]
MODEL_COLOR, NHANES_COLOR = "#E74C3C", "#61C2FF"
RFM_EDGES = np.linspace(10, 55, 50)
RFM_CENTERS = 0.5 * (RFM_EDGES[:-1] + RFM_EDGES[1:])
RFM_WIDTH = float(RFM_EDGES[1] - RFM_EDGES[0])
rng = np.random.default_rng(42)

hist = pd.read_csv(DATA / "rfm_by_age_group_models_hist.csv")
medians = pd.read_csv(DATA / "rfm_by_age_group_models_medians.csv").set_index("age_group")
nhanes = pd.read_csv(DATA / "nhanes_female_17_40.csv")


def model_rfm_density(lo, hi):
    """Return (densities, total_n) for the RFM histogram of models in [lo, hi]."""
    sub = hist[(hist["age_int"] >= lo) & (hist["age_int"] <= hi)]
    counts = np.zeros(len(RFM_CENTERS), dtype=float)
    for _, row in sub.iterrows():
        idx = int(np.searchsorted(RFM_EDGES, row["rfm_bin_left"], side="right") - 1)
        if 0 <= idx < len(counts):
            counts[idx] += row["count"]
    total = counts.sum()
    if total == 0:
        return counts, 0
    return counts / (total * RFM_WIDTH), int(total)


def model_age_counts(lo, hi):
    """Return per-integer-age count of model records in [lo, hi]."""
    sub = hist[(hist["age_int"] >= lo) & (hist["age_int"] <= hi)]
    return sub.groupby("age_int")["count"].sum()


def resample_nhanes(nh_group, mod_age_counts):
    total = mod_age_counts.sum()
    if total == 0:
        return pd.DataFrame()
    props = mod_age_counts / total
    ratios = {}
    for age, prop in props.items():
        nh_at_age = nh_group[nh_group["age_int"] == age]
        if len(nh_at_age) == 0 or prop == 0:
            continue
        ratios[age] = len(nh_at_age) / prop
    if not ratios:
        return pd.DataFrame()
    scale = min(ratios.values())
    resampled = []
    for age, prop in props.items():
        nh_at_age = nh_group[nh_group["age_int"] == age]
        if len(nh_at_age) == 0:
            continue
        n_keep = min(len(nh_at_age), max(1, int(round(prop * scale))))
        resampled.append(nh_at_age.sample(n=n_keep, random_state=rng.integers(1e9)))
    return pd.concat(resampled, ignore_index=True) if resampled else pd.DataFrame()


def make_figure(match, filename):
    fig = plt.figure(figsize=(FIGURE_WIDTH_CM * cm, FIGURE_WIDTH_CM * 0.4 * cm),
                      constrained_layout=True)
    gs = GridSpec(2, 4, figure=fig, hspace=0.1, wspace=0.15)
    age_axes, rfm_axes = [], []
    for i, ((lo, hi), label) in enumerate(zip(AGE_GROUPS, AGE_LABELS)):
        age_counts = model_age_counts(lo, hi)
        nh_raw = nhanes[(nhanes["age_int"] >= lo) & (nhanes["age_int"] <= hi)]
        nh_sub = resample_nhanes(nh_raw, age_counts) if match else nh_raw

        # Top row: age distribution.
        ax_age = fig.add_subplot(gs[0, i], sharey=age_axes[0] if age_axes else None)
        age_axes.append(ax_age)
        age_bins = np.arange(lo, hi + 2, 1)
        model_total = int(age_counts.sum())
        mod_age_arr = np.repeat(age_counts.index.values, age_counts.values.astype(int))
        ax_age.hist(mod_age_arr, bins=age_bins, density=True, alpha=0.6,
                    color=MODEL_COLOR, edgecolor="white", linewidth=0.3, label="Models")
        ax_age.hist(nh_sub["age_int"], bins=age_bins, density=True, alpha=0.5,
                    color=NHANES_COLOR, edgecolor="white", linewidth=0.3, label="NHANES")
        setup_panel(ax_age, xlabel="Age" if i == 0 else "",
                    ylabel="Density" if i == 0 else "")
        if i > 0:
            ax_age.tick_params(labelleft=False)
        ax_age.set_title(label, loc="left")
        ax_age.text(0.97, 0.92, f"Models: {model_total:,}\nNHANES: {len(nh_sub):,}",
                    transform=ax_age.transAxes, fontsize=4.5, ha="right", va="top",
                    color="#555555")
        if i == 0:
            ax_age.legend(fontsize=4.5, frameon=False, loc="upper left")

        # Bottom row: RFM distribution.
        ax_rfm = fig.add_subplot(gs[1, i], sharey=rfm_axes[0] if rfm_axes else None)
        rfm_axes.append(ax_rfm)
        mod_dens, mod_n = model_rfm_density(lo, hi)
        ax_rfm.bar(RFM_CENTERS, mod_dens, width=RFM_WIDTH, align="center",
                   alpha=0.6, color=MODEL_COLOR, edgecolor="white", linewidth=0.3)
        ax_rfm.hist(nh_sub["RFM"], bins=RFM_EDGES, density=True, alpha=0.5,
                    color=NHANES_COLOR, edgecolor="white", linewidth=0.3)
        setup_panel(ax_rfm, xlabel="RFM (%)" if i == 0 else "",
                    ylabel="Density" if i == 0 else "")
        if i > 0:
            ax_rfm.tick_params(labelleft=False)
        if mod_n > 0 and len(nh_sub) > 0:
            mod_med = float(medians.loc[label, "median_rfm"])
            nh_med = float(nh_sub["RFM"].median())
            ax_rfm.axvline(mod_med, color=MODEL_COLOR, ls="--", lw=0.7, alpha=0.8)
            ax_rfm.axvline(nh_med, color="#2980B9", ls="--", lw=0.7, alpha=0.8)
            ax_rfm.text(0.97, 0.92, f"$\\Delta$median = {nh_med - mod_med:.1f}",
                         transform=ax_rfm.transAxes, fontsize=5, ha="right", va="top",
                         color="#555555")
    age_axes[0].set_ylim(0, age_axes[0].get_ylim()[1] * 1.35)
    save_figure(fig, filename, FIG, formats=["png", "pdf"])
    plt.close(fig)


make_figure(match=False, filename="rfm_by_age_group")
make_figure(match=True, filename="rfm_by_age_group_matched")
print("Saved rfm_by_age_group{,_matched}.{png,pdf}")
