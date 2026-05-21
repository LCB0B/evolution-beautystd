"""Entropy evolution by event and variable for female models, 2000-2024.

Reads:  ../data/entropy_evolution_female.csv (event, variable, year, entropy)
Writes: ../figures/entropy_evolution_2000_2024_female.{png,pdf}
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from utils import cm, colors, remove_spines

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"; FIG.mkdir(exist_ok=True)

YEAR_START, YEAR_END = 2000, 2024
CAREER_EVENTS = ["fashion_shows", "advertisements", "magazine_covers", "editorials"]
VAR_ORDER = ["height", "bust", "waist", "hips", "rfm", "hair", "eyes", "world_region", "ethnicity"]
VAR_LABELS = {
    "height": "Height", "bust": "Bust", "waist": "Waist", "hips": "Hips",
    "rfm": "RFM", "hair": "Hair Color", "eyes": "Eye Color",
    "world_region": "World Region", "ethnicity": "Ethnicity",
}
event_colors = {
    "fashion_shows": "#07AB92", "advertisements": colors[0],
    "magazine_covers": colors[1], "editorials": colors[2],
}
event_labels = {
    "fashion_shows": "Fashion Shows", "advertisements": "Advertisements",
    "magazine_covers": "Magazine Covers", "editorials": "Editorials",
}

df = pd.read_csv(DATA / "entropy_evolution_female.csv")

fig = plt.figure(figsize=(18.3 * cm, 16 * cm), layout="constrained")
gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.05, wspace=0.03)
axes = {var: fig.add_subplot(gs[i // 3, i % 3]) for i, var in enumerate(VAR_ORDER)}

for var, ax in axes.items():
    sub = df[df["variable"] == var]
    if sub.empty:
        ax.text(0.5, 0.5, "No data", transform=ax.transAxes, ha="center", va="center",
                fontsize=10)
        remove_spines(ax)
        continue
    for event in CAREER_EVENTS:
        ed = sub[sub["event"] == event].sort_values("year")
        if ed.empty:
            continue
        ax.plot(ed["year"], ed["entropy"], color=event_colors[event],
                linewidth=1.5, label=event_labels[event], alpha=0.8)
    ax.set_xlabel("Year", fontsize=8)
    ax.set_ylabel("Entropy", fontsize=8)
    ax.set_title(VAR_LABELS[var], fontsize=9, fontweight="bold")
    ax.set_xlim(YEAR_START, YEAR_END + 1)
    remove_spines(ax)
    ax.tick_params(axis="both", which="major", direction="in", length=3, labelsize=7)

handles, labels = axes["height"].get_legend_handles_labels()
if handles:
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.05),
               ncol=4, frameon=False, fontsize=10)

base = "entropy_evolution_2000_2024_female"
for ext in ("png", "pdf"):
    fig.savefig(FIG / f"{base}.{ext}", dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"Saved {base}.{{png,pdf}}")
