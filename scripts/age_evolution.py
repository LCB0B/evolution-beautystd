"""Mean age (with 5–95 % band) of fashion records by year and event type.

Reads:  ../data/age_evolution_by_year.csv
Writes: ../figures/age_evolution.{png,pdf}
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from utils import cm, FIGURE_WIDTH_CM, save_figure, setup_panel

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"; FIG.mkdir(exist_ok=True)

EVENTS = ["Shows", "Editorials", "Advertisements", "Magazine Covers"]
event_colors = {
    "Shows": "#07AB92", "Editorials": "#8E44AD",
    "Advertisements": "#FF7DBE", "Magazine Covers": "#61C2FF",
}
YEAR_MIN, YEAR_MAX = 2000, 2024

stats = pd.read_csv(DATA / "age_evolution_by_year.csv")
stats = stats[stats["year"].between(YEAR_MIN, YEAR_MAX)]

fig, ax = plt.subplots(figsize=(FIGURE_WIDTH_CM * cm, FIGURE_WIDTH_CM * 0.45 * cm),
                        constrained_layout=True)
for label in EVENTS:
    s = stats[stats["event_type"] == label].sort_values("year")
    color = event_colors[label]
    ax.fill_between(s["year"], s["q05"], s["q95"], alpha=0.15, color=color, linewidth=0)
    ax.plot(s["year"], s["mean"], color=color, linewidth=1.2, marker="o",
            markersize=2, label=label)
setup_panel(ax, xlabel="Year", ylabel="Age (years)")
ax.legend(fontsize=5, loc="upper left", frameon=False)
ax.set_xlim(YEAR_MIN, YEAR_MAX)
save_figure(fig, "age_evolution", FIG, formats=["png", "pdf"])
plt.close(fig)
print("Saved age_evolution.{png,pdf}")
