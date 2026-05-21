"""
Intersectionality panel figure (race × plus-size, 2010-2024).

Reads:
  ../data/intersectionality_panel_proportions_2010_2024.csv
      Yearly observed proportions with 95% bootstrap CIs for:
        - nonwhite_share        (panel A)
        - plussize_white        (panel B)
        - plussize_nonwhite     (panel B)
        - plussize_all          (panel B)
  ../data/intersectionality_panel_yearly_2010_2024.csv
      Yearly proportion-test output: pct_plus_white, pct_plus_nonwhite,
      odds_ratio, or_ci_lower, or_ci_upper, etc. (panels C and D).

Writes:
  ../figures/intersectionality_panel.{png,pdf}
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from utils import cm, remove_spines

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

YEAR_START, YEAR_END = 2010, 2024
X_TICKS = [2011, 2014, 2017, 2020, 2023]

COLOR_WHITE = "#FF9123"
COLOR_NONWHITE = "#61C2FF"
COLOR_ALL = "#8E44AD"
COLOR_RR = "#000000"

FONTSIZE_LABEL = 7
FONTSIZE_LEGEND = 6
FONTSIZE_TICK = 5
TICK_DIRECTION = "in"
TICK_LENGTH = 2
LEGEND_BBOX = (0.0, 1.01)


def panel_a(ax, df):
    s = df[df["series"] == "nonwhite_share"].sort_values("year")
    ax.plot(s["year"], s["proportion"], color=COLOR_NONWHITE, linewidth=0.8,
            marker="o", markersize=2, label="Non-white models", zorder=3)
    ax.fill_between(s["year"], s["ci_lower"], s["ci_upper"],
                    color=COLOR_NONWHITE, alpha=0.2, zorder=1)
    ax.set_xlabel("Year", fontsize=FONTSIZE_LABEL)
    ax.set_ylabel("Non-white models (%)", fontsize=FONTSIZE_LABEL)


def panel_b(ax, df):
    for series, color, label in [
        ("plussize_white", COLOR_WHITE, "White models"),
        ("plussize_nonwhite", COLOR_NONWHITE, "Non-white models"),
        ("plussize_all", COLOR_ALL, "All models"),
    ]:
        s = df[df["series"] == series].sort_values("year")
        z = 3 if series == "plussize_all" else 2
        ax.plot(s["year"], s["proportion"], color=color, linewidth=0.8,
                marker="o", markersize=2, label=label, zorder=z, alpha=0.9)
        ax.fill_between(s["year"], s["ci_lower"], s["ci_upper"],
                        color=color, alpha=0.15, zorder=1)
    ax.set_xlabel("Year", fontsize=FONTSIZE_LABEL)
    ax.set_ylabel("Plus-size models (%)", fontsize=FONTSIZE_LABEL)


def panel_c(ax, yearly):
    v = yearly[(yearly["odds_ratio"] > 0)
               & np.isfinite(yearly["odds_ratio"])
               & np.isfinite(yearly["or_ci_lower"])
               & np.isfinite(yearly["or_ci_upper"])].copy()
    yerr = [v["odds_ratio"] - v["or_ci_lower"], v["or_ci_upper"] - v["odds_ratio"]]
    ax.errorbar(v["year"], v["odds_ratio"], yerr=yerr, fmt="o",
                color=COLOR_RR, markersize=2,
                elinewidth=0.8, capsize=1.5, capthick=0.6,
                label="Odds Ratio", zorder=3)
    ax.axhline(1, color="black", linestyle="--", linewidth=0.8, alpha=0.5, zorder=2)

    ax.set_ylim(-4, 10)
    xlo, xhi = yearly["year"].min() - 0.5, yearly["year"].max() + 0.5
    ax.fill_betweenx([1, 10], xlo, xhi, color=COLOR_NONWHITE, alpha=0.2, zorder=0)
    ax.fill_betweenx([-4, 1], xlo, xhi, color=COLOR_WHITE, alpha=0.2, zorder=0)
    ax.text(yearly["year"].min(), 7, "Non-white models over-represented",
            fontsize=FONTSIZE_TICK - 1, alpha=0.7, va="top", ha="left")
    ax.text(yearly["year"].min(), -3, "White models over-represented",
            fontsize=FONTSIZE_TICK - 1, alpha=0.7, va="bottom", ha="left")
    ax.set_yticks([9, 7, 5, 3, 1, -1, -3])
    ax.set_xlabel("Year", fontsize=FONTSIZE_LABEL)
    ax.set_ylabel("Odds Ratio (non-white vs. white)", fontsize=FONTSIZE_LABEL)


def panel_d(ax, yearly):
    diff = yearly["pct_plus_nonwhite"] - yearly["pct_plus_white"]
    ax.plot(yearly["year"], diff, color=COLOR_RR, linewidth=0.8,
            marker="o", markersize=2, label="Difference", zorder=3)
    ax.axhline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.5, zorder=2)

    ylim_hi = 2.2
    ylim_lo = -ylim_hi * 5 / 9
    ax.set_ylim(ylim_lo, ylim_hi)
    xlo, xhi = yearly["year"].min() - 0.5, yearly["year"].max() + 0.5
    ax.fill_betweenx([0, ylim_hi], xlo, xhi, color=COLOR_NONWHITE, alpha=0.2, zorder=0)
    ax.fill_betweenx([ylim_lo, 0], xlo, xhi, color=COLOR_WHITE, alpha=0.2, zorder=0)
    ax.text(yearly["year"].min(), 1.4, "Non-white models over-represented",
            fontsize=FONTSIZE_TICK - 1, alpha=0.7, va="top", ha="left")
    ax.text(yearly["year"].min(), -1, "White models over-represented",
            fontsize=FONTSIZE_TICK - 1, alpha=0.7, va="bottom", ha="left")
    ax.set_yticks([2, 1, 0, -1])
    ax.set_xlabel("Year", fontsize=FONTSIZE_LABEL)
    ax.set_ylabel("Difference in plus-size rate (pp)", fontsize=FONTSIZE_LABEL)


def _style(ax):
    remove_spines(ax)
    ax.legend(loc="upper left", fontsize=FONTSIZE_LEGEND, frameon=False,
              bbox_to_anchor=LEGEND_BBOX)
    ax.set_xlim(YEAR_START - 0.5, YEAR_END + 0.5)
    ax.set_xticks(X_TICKS)
    ax.tick_params(axis="both", which="major", labelsize=FONTSIZE_TICK,
                   direction=TICK_DIRECTION, length=TICK_LENGTH)


def main():
    props = pd.read_csv(DATA / "intersectionality_panel_proportions_2010_2024.csv")
    yearly = pd.read_csv(DATA / "intersectionality_panel_yearly_2010_2024.csv")

    fig, axes = plt.subplots(2, 2, figsize=(18 * cm / 2, 7 * cm),
                             constrained_layout=True)
    panel_a(axes[0, 0], props)
    panel_b(axes[0, 1], props)
    panel_c(axes[1, 0], yearly)
    panel_d(axes[1, 1], yearly)
    for ax in axes.flatten():
        _style(ax)

    for label, ax in zip("abcd", axes.flatten()):
        ax.text(-0.05, 1.02, label, transform=ax.transAxes,
                fontsize=FONTSIZE_LABEL, fontweight="bold", va="bottom", ha="right")

    for ext in ("png", "pdf"):
        out = FIG / f"intersectionality_panel.{ext}"
        fig.savefig(out, dpi=400, bbox_inches="tight")
        print(f"Saved: {out}")
    plt.close(fig)


if __name__ == "__main__":
    main()
