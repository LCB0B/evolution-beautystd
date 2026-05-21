"""Forest plots of IQR / skewness / kurtosis trends.

Reads:  ../data/forest_outliers_trends_{female,male}_eu.csv
Writes: ../figures/forest_plot_{iqr,skewness,kurtosis,outliers_combined}_*_eu.{png,pdf}
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
    "fashion_shows": "#07AB92", "advertisements": "#FF7DBE",
    "magazine_covers": "#61C2FF", "editorials": "#8E44AD",
    "lookbooks": "#F1C40F", "catalogues": "#FF9123",
    "weighted_average": "#2E3B4E",
}
MEASUREMENT_LABELS = {
    "height_cm": "Height", "bust-eu_clean": "Bust", "waist-eu_clean": "Waist",
    "hips-eu_clean": "Hips", "rfm": "RFM Index",
}
METRIC_LABELS = {"iqr": "IQR (Interquartile Range)", "skewness": "Skewness", "kurtosis": "Kurtosis"}


def prepare(df, metric=None):
    df = df.copy()
    if metric:
        df = df[df["metric"] == metric].copy()
    df = df.dropna(subset=["sen_slope", "slope_ci_lower", "slope_ci_upper",
                            "measurement", "event_type"])
    df["measurement_label"] = df["measurement"].map(MEASUREMENT_LABELS).fillna(df["measurement"])
    df["event_label"] = df["event_type"].str.replace("_", " ").str.title()
    df["display_label"] = df["measurement_label"] + " - " + df["event_label"]
    df["color"] = df["event_type"].map(EVENT_COLOR_MAP).fillna("#666666")
    m_order = ["bust-eu_clean", "waist-eu_clean", "hips-eu_clean", "rfm"]
    e_order = ["fashion_shows", "advertisements", "magazine_covers", "editorials",
               "weighted_average"]
    df["m_sort"] = df["measurement"].map({m: i for i, m in enumerate(m_order)}).fillna(999)
    df["e_sort"] = df["event_type"].map({e: i for i, e in enumerate(e_order)}).fillna(999)
    return df.sort_values(["m_sort", "e_sort"]).reset_index(drop=True)


def single_forest(df, metric, gender):
    fig, ax = plt.subplots(figsize=(12, 10))
    y = np.arange(len(df))[::-1]
    for i, (_, r) in enumerate(df.iterrows()):
        yy, c = y[i], r["color"]
        ax.plot([r["slope_ci_lower"], r["slope_ci_upper"]], [yy, yy],
                color=c, linewidth=2, alpha=0.7)
        sig = bool(r.get("significant", False))
        ax.plot(r["sen_slope"], yy, "o", markersize=8 if sig else 6, color=c,
                alpha=1.0 if sig else 0.6, markeredgecolor="white", markeredgewidth=0.5)
        for x_ in (r["slope_ci_lower"], r["slope_ci_upper"]):
            ax.plot([x_, x_], [yy - 0.15, yy + 0.15], color=c, linewidth=1.5, alpha=0.7)
    ax.axvline(0, color="black", linestyle="--", alpha=0.5, linewidth=1)
    ax.set_yticks(y)
    ax.set_yticklabels(df["display_label"], fontsize=9)
    ax.set_xlabel(f"Slope Estimate ({METRIC_LABELS.get(metric, metric)} change per year)", fontsize=10)
    ax.tick_params(axis="x", labelsize=9)
    ax.grid(axis="x", alpha=0.3, linestyle="-", linewidth=0.5)
    remove_spines(ax)
    plt.subplots_adjust(left=0.4, right=0.95, top=0.9, bottom=0.1)
    return fig


def combined_forest(df, gender):
    metrics = ["iqr", "skewness", "kurtosis"]
    fig, axes = plt.subplots(1, 3, figsize=(16, 12))
    fig.suptitle(f"Distribution Property Trends ({gender.title()})", fontsize=14, fontweight="bold")
    for i, m in enumerate(metrics):
        ax = axes[i]
        sub = df[df["metric"] == m].sort_values(["m_sort", "e_sort"]).reset_index(drop=True)
        if len(sub) == 0:
            ax.text(0.5, 0.5, f"No {m} data", ha="center", va="center", transform=ax.transAxes)
            ax.set_title(METRIC_LABELS.get(m, m))
            continue
        y = np.arange(len(sub))[::-1]
        for j, (_, r) in enumerate(sub.iterrows()):
            yy, c = y[j], r["color"]
            ax.plot([r["slope_ci_lower"], r["slope_ci_upper"]], [yy, yy], color=c, linewidth=2, alpha=0.7)
            sig = bool(r.get("significant", False))
            ax.plot(r["sen_slope"], yy, "o", markersize=6 if sig else 4, color=c,
                    alpha=1.0 if sig else 0.6, markeredgecolor="white", markeredgewidth=0.5)
        ax.axvline(0, color="black", linestyle="--", alpha=0.5, linewidth=1)
        if i == 0:
            ax.set_yticks(y)
            ax.set_yticklabels(sub["display_label"], fontsize=8)
        else:
            ax.set_yticks([])
        ax.set_xlabel(METRIC_LABELS.get(m, m), fontsize=10)
        ax.grid(axis="x", alpha=0.3, linewidth=0.5)
        remove_spines(ax)
    plt.tight_layout()
    return fig


for gender, src in [("female", "forest_outliers_trends_female_eu.csv"),
                    ("male",   "forest_outliers_trends_male_eu.csv")]:
    csv = DATA / src
    if not csv.exists():
        print(f"  skip {src} (missing)")
        continue
    base = prepare(pd.read_csv(csv))
    for metric in ("iqr", "skewness", "kurtosis"):
        sub = prepare(pd.read_csv(csv), metric=metric)
        if len(sub) == 0:
            continue
        fig = single_forest(sub, metric, gender)
        for ext in ("png", "pdf"):
            fig.savefig(FIG / f"forest_plot_{metric}_trends_2000_2024_{gender}_eu.{ext}",
                        dpi=300, bbox_inches="tight")
        plt.close(fig)
    fig = combined_forest(base, gender)
    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"forest_plot_outliers_combined_2000_2024_{gender}_eu.{ext}",
                    dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved forest_plot_*_2000_2024_{gender}_eu.{{png,pdf}}")
