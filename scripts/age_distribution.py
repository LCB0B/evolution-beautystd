"""Age distribution of fashion records (overall + per event type).

Reads:
  ../data/age_distribution_records.csv (event_type, age, count)
  ../data/age_distribution_meta.csv    (event_type, n_records, n_models)
Writes: ../figures/age_distribution.{png,pdf}
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from utils import cm, FIGURE_WIDTH_CM, save_figure, setup_panel

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"; FIG.mkdir(exist_ok=True)

EVENTS = ["Shows", "Editorials", "Advertisements", "Magazine Covers"]
event_colors = {
    "Shows": "#07AB92", "Editorials": "#8E44AD",
    "Advertisements": "#FF7DBE", "Magazine Covers": "#61C2FF",
}
ALL_COLOR = "#333333"

records = pd.read_csv(DATA / "age_distribution_records.csv")
meta = pd.read_csv(DATA / "age_distribution_meta.csv").set_index("event_type")


def hist_from_counts(ax, df_event, color):
    """Bar 'histogram' from already-binned (age, count) data."""
    ax.bar(df_event["age"], df_event["count"], width=1.0, color=color,
           alpha=0.85, edgecolor="white", linewidth=0.3)


def weighted_quantile(ages, counts, q):
    order = np.argsort(ages)
    ages = ages.values[order]
    counts = counts.values[order]
    cum = counts.cumsum()
    total = cum[-1]
    idx = np.searchsorted(cum, q * total)
    return float(ages[min(idx, len(ages) - 1)])


def weighted_mean(ages, counts):
    return float((ages * counts).sum() / counts.sum())


fig = plt.figure(figsize=(FIGURE_WIDTH_CM * cm, FIGURE_WIDTH_CM * 0.55 * cm),
                 constrained_layout=True)
gs = GridSpec(2, 4, figure=fig, height_ratios=[1.2, 1])

ax_top = fig.add_subplot(gs[0, :])
all_data = records[records["event_type"] == "All"]
hist_from_counts(ax_top, all_data, ALL_COLOR)
setup_panel(ax_top, xlabel="Age (years)", ylabel="Number of records")
ax_top.set_title("All event types", loc="left")
q25 = weighted_quantile(all_data["age"], all_data["count"], 0.25)
med = weighted_quantile(all_data["age"], all_data["count"], 0.5)
q75 = weighted_quantile(all_data["age"], all_data["count"], 0.75)
for v in (q25, q75):
    ax_top.axvline(v, color="#2980B9", ls=":", lw=0.7)
ax_top.axvline(med, color="#E74C3C", ls="--", lw=0.8)
ymax = ax_top.get_ylim()[1]
ax_top.text(q25 - 1.5, ymax * 0.75, f"$P_{{25}}$ = {q25:.0f}", fontsize=5,
            color="#2980B9", ha="right")
ax_top.text(med + 0.5, ymax * 0.95, f"median = {med:.0f}", fontsize=5.5, color="#E74C3C")
ax_top.text(q75 + 1.5, ymax * 0.75, f"$P_{{75}}$ = {q75:.0f}", fontsize=5, color="#2980B9")
m_all = meta.loc["All"]
ax_top.text(0.98, 0.85, f"n = {int(m_all['n_records']):,} records\n{int(m_all['n_models']):,} models",
            transform=ax_top.transAxes, fontsize=5, ha="right", va="top", color="#555555")

for i, label in enumerate(EVENTS):
    ax = fig.add_subplot(gs[1, i])
    sub = records[records["event_type"] == label]
    hist_from_counts(ax, sub, event_colors[label])
    setup_panel(ax, xlabel="Age (years)", ylabel="Number of records" if i == 0 else "")
    ax.set_title(label, loc="left")
    med_sub = weighted_quantile(sub["age"], sub["count"], 0.5)
    ax.axvline(med_sub, color="#E74C3C", ls="--", lw=0.8)
    ax.text(med_sub + 1.5, ax.get_ylim()[1] * 0.9, f"median = {med_sub:.0f}",
            fontsize=5.5, color="#E74C3C")
    m = meta.loc[label]
    ax.text(0.98, 0.85, f"n = {int(m['n_records']):,}\n{int(m['n_models']):,} models",
            transform=ax.transAxes, fontsize=5, ha="right", va="top", color="#555555")

save_figure(fig, "age_distribution", FIG, formats=["png", "pdf"])
plt.close(fig)
print("Saved age_distribution.{png,pdf}")
