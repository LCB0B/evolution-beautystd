"""Quantile policy-effect panels for Milan 2006 and Paris 2017 (Q10/Q25/Q75/Q90).

Reads:  ../data/city_charter_timeseries.csv
Writes: ../figures/quantile_policy_analysis.{png,pdf}
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from utils import cm, FIGURE_WIDTH_CM, remove_spines

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"; FIG.mkdir(exist_ok=True)

MILAN_COLOR = "#068E14"
PARIS_COLOR = "#17329E"
OTHER_COLOR = "#7f7f7f"
MILAN_POLICY_YEAR = 2005 + 8/12
PARIS_POLICY_YEAR = 2017.5


def plot_panel(ax, data_df, city, control_group, color, policy_year, show_ylabel, show_legend, letter, title):
    year_min = policy_year - 5
    year_max = policy_year + 5
    plot_df = data_df[(data_df["year"] >= year_min) & (data_df["year"] <= year_max)]
    pre = plot_df[plot_df["year"] < policy_year]
    post = plot_df[plot_df["year"] >= policy_year]
    for sub in (pre, post):
        ax.plot(sub[sub["group"] == city]["year"], sub[sub["group"] == city]["mean"],
                "o-", color=color, linewidth=1, markersize=3,
                label=city if sub is pre else None, zorder=3)
        ax.fill_between(sub[sub["group"] == city]["year"],
                         sub[sub["group"] == city]["mean_ci_lower"],
                         sub[sub["group"] == city]["mean_ci_upper"],
                         color=color, alpha=0.25, linewidth=0)
        ax.plot(sub[sub["group"] == control_group]["year"], sub[sub["group"] == control_group]["mean"],
                "o-", color=OTHER_COLOR, linewidth=1, markersize=3,
                label="Control" if sub is pre else None, zorder=2)
        ax.fill_between(sub[sub["group"] == control_group]["year"],
                         sub[sub["group"] == control_group]["mean_ci_lower"],
                         sub[sub["group"] == control_group]["mean_ci_upper"],
                         color=OTHER_COLOR, alpha=0.25, linewidth=0)
    ax.axvline(policy_year, color="black", linestyle="--", linewidth=0.8, alpha=0.7,
               zorder=1, ymax=0.88)
    label = "2006 MFW\nPolicy" if city == "Milan" else "2017 PFW\nPolicy"
    ax.text(policy_year, 20.8, label, ha="center", va="top", fontsize=5)
    ax.set_xlim(year_min - 0.5, year_max + 0.5)
    ax.set_xlabel("Year", fontsize=6)
    if show_ylabel:
        ax.set_ylabel("RFM", fontsize=6, rotation=0, ha="left")
        ax.yaxis.set_label_coords(-0.22, 0.5)
    if show_legend:
        ax.legend(fontsize=6, frameon=False, loc="upper left")
    ax.set_title(title, fontsize=8, pad=3, fontweight="bold")
    ax.text(-0.07, 1.08, letter, transform=ax.transAxes, fontsize=8,
            fontweight="bold", va="top")
    remove_spines(ax)
    ax.tick_params(axis="both", which="major", labelsize=6, length=2, width=0.5, direction="in")


df = pd.read_csv(DATA / "city_charter_timeseries.csv")

quantile_map = [("q10", "Q10"), ("q25", "Q25"), ("q75", "Q75"), ("q90", "Q90")]

fig = plt.figure(figsize=(FIGURE_WIDTH_CM * cm, FIGURE_WIDTH_CM * cm * 0.43),
                 constrained_layout=True)
gs = fig.add_gridspec(2, 4)
fig.set_constrained_layout_pads(w_pad=0.2, h_pad=0.4)

milan_axes, paris_axes = [], []
for col, (q, title) in enumerate(quantile_map):
    df_m = df.copy()
    df_m["mean"] = df_m[q]
    df_m["mean_ci_lower"] = df_m[q] - 0.1
    df_m["mean_ci_upper"] = df_m[q] + 0.1
    ax = fig.add_subplot(gs[0, col])
    plot_panel(ax, df_m, "Milan", "MilanControl", MILAN_COLOR, MILAN_POLICY_YEAR,
               show_ylabel=(col == 0), show_legend=(col == 0),
               letter="abcd"[col], title=title)
    if col > 0:
        ax.tick_params(labelleft=False)
    milan_axes.append(ax)

for col, (q, title) in enumerate(quantile_map):
    df_p = df.copy()
    df_p["mean"] = df_p[q]
    df_p["mean_ci_lower"] = df_p[q] - 0.1
    df_p["mean_ci_upper"] = df_p[q] + 0.1
    ax = fig.add_subplot(gs[1, col])
    plot_panel(ax, df_p, "Paris", "ParisControl", PARIS_COLOR, PARIS_POLICY_YEAR,
               show_ylabel=(col == 0), show_legend=(col == 0),
               letter="efgh"[col], title=title)
    if col > 0:
        ax.tick_params(labelleft=False)
    paris_axes.append(ax)

ymin = min(ax.get_ylim()[0] for ax in milan_axes)
ymax = max(ax.get_ylim()[1] for ax in milan_axes)
for ax in milan_axes + paris_axes:
    ax.set_ylim(ymin, ymax)

plt.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(FIG / f"quantile_policy_analysis.{ext}", dpi=300, bbox_inches="tight")
plt.close(fig)
print("Saved quantile_policy_analysis.{png,pdf}")
