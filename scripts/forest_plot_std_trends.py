"""Forest plot of standard-deviation trend Sen-slope estimates.

Reads:  ../data/forest_std_trends_{female,male}_eu.csv
Writes: ../figures/forest_plot_std_trends_{female,male}_eu.{png,pdf}
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from utils import remove_spines, cm

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"; FIG.mkdir(exist_ok=True)

EVENT_COLOR_MAP = {
    "fashion_shows": "#07AB92",
    "advertisements": "#FF7DBE",
    "magazine_covers": "#61C2FF",
    "editorials": "#8E44AD",
    "lookbooks": "#F1C40F",
    "catalogues": "#FF9123",
    "weighted_average": "#2E3B4E",
}
MEASUREMENT_LABELS = {
    "height_cm": "Height",
    "bust-eu_clean": "Bust",
    "waist-eu_clean": "Waist",
    "hips-eu_clean": "Hips",
    "rfm": "RFM Index",
}


def prepare(df):
    df = df.copy()
    df["measurement_label"] = df["measurement"].map(MEASUREMENT_LABELS)
    df["event_label"] = df["event_type"].str.replace("_", " ").str.title()
    df["combined_label"] = df["measurement_label"] + " - " + df["event_label"]
    m_order = ["height_cm", "bust-eu_clean", "waist-eu_clean", "hips-eu_clean", "rfm"]
    e_order = ["fashion_shows", "advertisements", "magazine_covers", "editorials",
               "weighted_average"]
    df["measurement_order"] = df["measurement"].map({m: i for i, m in enumerate(m_order)})
    df["event_order"] = df["event_type"].map({e: i for i, e in enumerate(e_order)})
    df = df.sort_values(["measurement_order", "event_order"], ascending=[False, True])
    return df


def forest_plot(df, title):
    fig, ax = plt.subplots(figsize=(18 * cm, 11 * cm))
    y_positions = np.arange(len(df))
    slopes = df["sen_slope"].values
    lower = slopes - df["slope_ci_lower"].values
    upper = df["slope_ci_upper"].values - slopes
    point_colors = [EVENT_COLOR_MAP.get(e, "#CCCCCC") for e in df["event_type"]]

    for i, (slope, lo, hi, color, sig) in enumerate(zip(slopes, lower, upper,
                                                         point_colors, df["significant"])):
        ax.plot([slope - lo, slope + hi], [y_positions[i]] * 2,
                color=color, linewidth=2, alpha=0.7)
        marker, ms, alpha = ("o", 8, 1.0) if sig else ("^", 6, 0.6)
        ax.plot(slope, y_positions[i], marker=marker, color=color, markersize=ms,
                alpha=alpha, markeredgecolor="white", markeredgewidth=0.5)

    ax.axvline(0, color="black", linestyle="--", alpha=0.5, linewidth=1)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(df["combined_label"].values)
    ax.set_xlabel("Slope Estimate (Standard Deviation Change per Year)")
    ax.grid(True, axis="x", alpha=0.3)
    ax.set_axisbelow(True)
    remove_spines(ax, ["top", "right"])

    legend_elements = []
    for event, color in EVENT_COLOR_MAP.items():
        if event in df["event_type"].values:
            legend_elements.append(plt.Line2D([0], [0], marker="o", color="w",
                                              markerfacecolor=color, markersize=8,
                                              label=event.replace("_", " ").title()))
    legend_elements += [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="gray",
                   markersize=8, label="Significant (p < 0.05)"),
        plt.Line2D([0], [0], marker="^", color="w", markerfacecolor="gray",
                   markersize=6, label="Not significant"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", frameon=True, fancybox=True)
    plt.tight_layout()
    return fig


for gender, src, out in [
    ("female", "forest_std_trends_female_eu.csv", "forest_plot_std_trends_female_eu"),
    ("male",   "forest_std_trends_male_eu.csv",   "forest_plot_std_trends_male_eu"),
]:
    csv = DATA / src
    if not csv.exists():
        print(f"  skip {src} (missing)")
        continue
    df = prepare(pd.read_csv(csv))
    fig = forest_plot(df, gender)
    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"{out}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out}.{{png,pdf}}")
