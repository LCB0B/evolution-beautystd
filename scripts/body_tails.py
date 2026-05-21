"""Weighted-average evolution of body-measurement quantiles (female, 2000-2024).

Reads:  ../data/body_tails_female_2000_2024.csv
Writes: ../figures/body_tails_female_2000_2024.{png,pdf}
        + ../figures/body_tails_female_2000_2024.csv (regression details)
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats as sp_stats
from utils import cm, FIGURE_WIDTH_CM, remove_spines

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"; FIG.mkdir(exist_ok=True)

YEAR_START, YEAR_END = 2000, 2024
MEASUREMENTS = {"bust-eu": "Bust (cm)", "waist-eu": "Waist (cm)",
                "hips-eu": "Hips (cm)", "rfm": "RFM"}
UPPER_QUANTILES = ["p99", "p95", "p90", "p75"]
LOWER_QUANTILES = ["p50", "p25", "p10"]

df = pd.read_csv(DATA / "body_tails_female_2000_2024.csv")


def weighted_avg(measurement, quantile):
    sub = df[df["measurement"] == measurement].copy()
    sub = sub.dropna(subset=[quantile])
    sub = sub[sub["count"] > 0]
    agg = (sub.groupby("year").apply(
        lambda g: (g[quantile] * g["count"]).sum() / g["count"].sum())
        .reset_index(name="value"))
    return agg


def plot_evolution(ax, measurement, quantile):
    data = weighted_avg(measurement, quantile)
    if len(data) < 3:
        return None
    color = "#2E3B4E"
    ax.plot(data["year"], data["value"], color=color, linewidth=1.2, alpha=0.9)
    y_min, y_max = ax.get_ylim()
    if (y_max - y_min) < 3:
        ax.set_ylim(y_min - 1, y_max + 1)
    x, y = data["year"].values, data["value"].values
    slope, intercept, r, p, se = sp_stats.linregress(x, y)
    x_range = np.array([x.min(), x.max()])
    if slope > 0.05:
        c = "forestgreen"
    elif slope < -0.05:
        c = "firebrick"
    else:
        c = "gray"
    ax.plot(x_range, slope * x_range + intercept, color=c, linestyle="--",
            linewidth=1.0, alpha=0.7, zorder=1)
    ax.text(0.25, 0.95, f"R²={r**2:.2f}, slope={slope:.2f}",
            transform=ax.transAxes, fontsize=6, va="top", ha="left", color="black")
    return {"measurement": measurement, "quantile": quantile,
            "slope": slope, "intercept": intercept, "r_squared": r**2,
            "p_value": p, "data": data}


def format_ax(ax, label, quantile, bottom, first_col, row_idx):
    if bottom:
        ax.set_xlabel("Year", fontsize=7)
    if first_col:
        ax.set_ylabel(f"Quantile {quantile[1:]}", fontsize=7, rotation=0,
                      labelpad=30, va="center", ha="right", fontweight="bold")
        ax.yaxis.set_label_coords(-0.17, 0.5)
    else:
        ax.set_ylabel("")
    remove_spines(ax)
    ax.tick_params(axis="both", which="major", direction="in", length=3, labelsize=6)
    ax.set_xlim(YEAR_START - 1, YEAR_END + 1)
    ax.grid(True, alpha=0.2, linewidth=0.3)
    if row_idx % 2 == 1:
        ylim = ax.get_ylim()
        ax.axhspan(ylim[0], ylim[1], facecolor="lightgray", alpha=0.15, zorder=0)


fig = plt.figure(figsize=(FIGURE_WIDTH_CM * cm, FIGURE_WIDTH_CM * cm))
n_upper = len(UPPER_QUANTILES); n_lower = len(LOWER_QUANTILES)
gs = gridspec.GridSpec(n_upper + n_lower, len(MEASUREMENTS), figure=fig,
                        hspace=0.3, wspace=0.2, left=0.1, right=1.0,
                        top=0.95, bottom=0.02)

records = []
for q_idx, q in enumerate(UPPER_QUANTILES):
    for m_idx, (m, lbl) in enumerate(MEASUREMENTS.items()):
        ax = fig.add_subplot(gs[q_idx, m_idx])
        res = plot_evolution(ax, m, q)
        if res:
            records.append(res)
        bottom = (q_idx == n_upper - 1) and n_lower == 0
        format_ax(ax, lbl, q, bottom, m_idx == 0, q_idx)
        if q_idx == 0:
            ax.set_title(lbl, fontsize=8, fontweight="bold", pad=8)

for q_idx, q in enumerate(LOWER_QUANTILES):
    row = n_upper + q_idx
    for m_idx, (m, lbl) in enumerate(MEASUREMENTS.items()):
        ax = fig.add_subplot(gs[row, m_idx])
        res = plot_evolution(ax, m, q)
        if res:
            records.append(res)
        format_ax(ax, lbl, q, q_idx == n_lower - 1, m_idx == 0, row)

base = "body_tails_female_2000_2024"
for ext in ("png", "pdf"):
    fig.savefig(FIG / f"{base}.{ext}", dpi=300, bbox_inches="tight")
plt.close(fig)

if records:
    expanded = []
    for r in records:
        d = r["data"].copy()
        d["measurement"] = r["measurement"]
        d["quantile"] = r["quantile"]
        d["slope"] = r["slope"]
        d["intercept"] = r["intercept"]
        d["r_squared"] = r["r_squared"]
        d["p_value"] = r["p_value"]
        expanded.append(d)
    pd.concat(expanded, ignore_index=True).to_csv(FIG / f"{base}.csv", index=False,
                                                    float_format="%.6f")

print(f"Saved {base}.{{png,pdf,csv}}")
