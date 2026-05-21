"""Sensitivity of top/bottom-10 % RFM rates across hierarchy-tier counts (6, 8, 10).

Reads:  ../data/rfm_tiers_sensitivity.csv
Writes: ../figures/rfm_tiers_sensitivity.{png,pdf}
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils import cm, FIGURE_WIDTH_CM, remove_spines, save_figure

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"; FIG.mkdir(exist_ok=True)

df = pd.read_csv(DATA / "rfm_tiers_sensitivity.csv")
TIER_CONFIGS = sorted(df["n_tiers"].unique())


def tier_colors(n):
    cmap = plt.colormaps.get_cmap("RdYlBu_r")
    return [cmap(i / max(n - 1, 1)) for i in range(n)]


fig, axes = plt.subplots(len(TIER_CONFIGS), 2,
    figsize=(FIGURE_WIDTH_CM * cm * 0.55,
              FIGURE_WIDTH_CM * 0.32 * cm * len(TIER_CONFIGS)),
    constrained_layout=True)

ylim_top = df["ci_upper"].max() * 1.15
left_letters = ["a", "c", "e"]
right_letters = ["b", "d", "f"]

for row, n_tiers in enumerate(TIER_CONFIGS):
    sub = df[df["n_tiers"] == n_tiers]
    tier_names = sorted(sub["tier"].unique(), key=lambda s: int(s[1:]))
    colors = tier_colors(n_tiers)
    for col, panel in enumerate(["bottom", "top"]):
        ax = axes[row, col]
        pd_data = sub[sub["panel"] == panel].set_index("tier").loc[tier_names]
        x = np.arange(len(tier_names))
        rates = pd_data["rate"].values
        yerr = [rates - pd_data["ci_lower"].values,
                pd_data["ci_upper"].values - rates]
        ax.bar(x, rates, color=colors, alpha=0.9)
        ax.errorbar(x, rates, yerr=yerr, fmt="none", ecolor="black",
                    capsize=2, linewidth=0.5)
        weights = pd_data["n"].values / pd_data["n"].values.sum()
        ax.axhline(np.average(rates, weights=weights), color="black", ls="--", lw=0.5, alpha=0.7)
        ax.set_xticks(x); ax.set_xticklabels(tier_names, fontsize=5)
        ax.set_ylim(0, ylim_top)
        remove_spines(ax)
        ax.tick_params(axis="both", labelsize=5, length=2, width=0.5, direction="in")
        lbl = (left_letters if col == 0 else right_letters)[row]
        ax.text(-0.05, 1.08, lbl, transform=ax.transAxes, fontsize=8, fontweight="bold", va="top")
        if row == len(TIER_CONFIGS) - 1:
            ax.set_xlabel("Hierarchy Tier", fontsize=6)
        if row == 0:
            label = "Bottom 10% RFM Rate (%)" if col == 0 else "Top 10% RFM Rate (%)"
            ax.set_ylabel(label, fontsize=6, rotation=0, ha="left")
            ax.yaxis.set_label_coords(0.02, 0.94)
        ax.text(0.97, 0.92, f"{n_tiers} tiers", transform=ax.transAxes,
                fontsize=5, ha="right", va="top", color="#555555")
    axes[row, 1].sharey(axes[row, 0])
    axes[row, 1].tick_params(labelleft=False)

save_figure(fig, "rfm_tiers_sensitivity", FIG, formats=["png", "pdf"])
plt.close(fig)
print("Saved rfm_tiers_sensitivity.{png,pdf}")
