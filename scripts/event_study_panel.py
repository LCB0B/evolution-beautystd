"""Event-study panel: Milan 2006 vs Paris 2017 (mean, Q10, Q25).

Reads:  ../data/event_study_{milan_2006,paris_2017}.csv
Writes: ../figures/event_study_panel.{png,pdf}
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
MILAN_POLICY_YEAR = 2005 + 8/12
PARIS_POLICY_YEAR = 2017.5
OUTCOMES = ["mean", "q10", "q25"]
OUTCOME_TITLES = {"mean": "Mean", "q10": "Q10", "q25": "Q25"}


def plot_panel(ax, df, city, color, policy_year, show_ylabel, show_legend, letter, title):
    pre = df[df["year"] < policy_year]
    post = df[df["year"] >= policy_year]
    for sub in (pre, post):
        yerr = [sub["coef"] - sub["ci_lower"], sub["ci_upper"] - sub["coef"]]
        label = city if sub is pre else None
        ax.errorbar(sub["year"], sub["coef"], yerr=yerr, fmt="o-", color=color,
                    ecolor=color, linewidth=1.0, markersize=3, capsize=3,
                    capthick=0.8, label=label, zorder=3)
    ax.axhline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.7, zorder=1)
    ax.axvline(policy_year, color="black", linestyle="--", linewidth=0.8,
               alpha=0.7, zorder=1, ymax=0.83)
    if city == "Milan":
        ax.set_ylim(-0.7, 1.9)
    else:
        ax.set_ylim(-0.7, 0.7)
    ylim = ax.get_ylim()
    label = "2006 MFW\nPolicy" if city == "Milan" else "2017 PFW\nPolicy"
    ax.text(policy_year, ylim[1], label, ha="center", va="top", fontsize=5)
    ax.set_xlim(df["year"].min() - 0.5, df["year"].max() + 0.5)
    ax.set_xlabel("Year", fontsize=6)
    if show_ylabel:
        ax.set_ylabel("Difference vs. Control (RFM)", fontsize=6)
    if show_legend:
        ax.legend(fontsize=6, frameon=False, loc="upper left")
    ax.set_title(title, fontsize=8, pad=3, fontweight="bold")
    ax.text(-0.07, 1.08, letter, transform=ax.transAxes, fontsize=8,
            fontweight="bold", va="top")
    remove_spines(ax)
    ax.tick_params(axis="both", which="major", labelsize=6, length=2, width=0.5,
                   direction="in")


milan = pd.read_csv(DATA / "event_study_milan_2006.csv")
paris = pd.read_csv(DATA / "event_study_paris_2017.csv")

fig = plt.figure(figsize=(FIGURE_WIDTH_CM * cm, FIGURE_WIDTH_CM * cm * 0.43),
                 constrained_layout=True)
gs = fig.add_gridspec(2, 3)
fig.set_constrained_layout_pads(w_pad=0.2, h_pad=0.4)

for row, (df, city, color, policy, letters) in enumerate([
    (milan, "Milan", MILAN_COLOR, MILAN_POLICY_YEAR, "abc"),
    (paris, "Paris", PARIS_COLOR, PARIS_POLICY_YEAR, "def"),
]):
    row_axes = []
    for col, outcome in enumerate(OUTCOMES):
        ax = fig.add_subplot(gs[row, col])
        row_axes.append(ax)
        plot_panel(ax, df[df["outcome"] == outcome], city, color, policy,
                   show_ylabel=(col == 0), show_legend=(col == 0),
                   letter=letters[col], title=OUTCOME_TITLES[outcome])
        if col > 0:
            ax.tick_params(labelleft=False)
    ymin = min(ax.get_ylim()[0] for ax in row_axes)
    ymax = max(ax.get_ylim()[1] for ax in row_axes)
    for ax in row_axes:
        ax.set_ylim(ymin, ymax)

plt.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(FIG / f"event_study_panel.{ext}", dpi=300, bbox_inches="tight")
plt.close(fig)
print("Saved event_study_panel.{png,pdf}")
