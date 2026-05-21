"""PCA temporal evolution panel (female).

Reads:
  ../data/pca_female_yearly_means.csv
  ../data/pca_female_career_event_means.csv
  ../data/pca_female_loadings.json
Writes: ../figures/pca_temporal_evolution_female.{png,pdf}
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
from utils import cm, FIGURE_WIDTH_CM, remove_spines, colors

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"; FIG.mkdir(exist_ok=True)

GENDER = "female"
RFM_LEVELS = [17, 17.2, 17.4, 17.6, 17.8, 18]
RFM_ALPHA = 0.75
ARROW_COLOR = "#444444"
ARROW_ALPHA = 0.6
CAREER_EVENT_COLORS = {
    "fashion_shows": "#07AB92", "advertisements": colors[0],
    "magazine_covers": colors[1], "editorials": colors[2],
    "lookbooks": colors[3], "catalogues": colors[4],
}

yearly = pd.read_csv(DATA / f"pca_{GENDER}_yearly_means.csv")
event_means = pd.read_csv(DATA / f"pca_{GENDER}_career_event_means.csv") \
    if (DATA / f"pca_{GENDER}_career_event_means.csv").exists() else None
with open(DATA / f"pca_{GENDER}_loadings.json") as f:
    pca_bundle = json.load(f)
evr = pca_bundle["explained_variance_ratios"]
feature_order = pca_bundle["feature_order"]
loadings = pca_bundle["loadings"]
feature_means = np.array(pca_bundle["scaler_means"])
feature_scales = np.array(pca_bundle["scaler_scales"])
V = np.array([[loadings[f][f"PC{k+1}"] for f in feature_order] for k in range(4)])
idx_height = feature_order.index("height-metric")
idx_waist = feature_order.index("waist-eu")


def add_rfm_contours(ax, V, means, scales, idx_h, idx_w, levels):
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    xx = np.linspace(x0, x1, 250); yy = np.linspace(y0, y1, 250)
    S1, S2 = np.meshgrid(xx, yy)
    S = np.stack([S1, S2, np.zeros_like(S1), np.zeros_like(S1)], axis=-1)
    X = means + np.tensordot(S, V, axes=([S.ndim - 1], [0])) * scales
    H = X[..., idx_h]; W = X[..., idx_w]
    rfm_const = 76.0 if GENDER == "female" else 64.0
    with np.errstate(divide="ignore", invalid="ignore"):
        RFM = np.where(W > 0, rfm_const - 20.0 * (H / W), np.nan)
    cmap = mcolors.LinearSegmentedColormap.from_list("rfm", ["darkred", "forestgreen"])
    CS = ax.contour(S1, S2, RFM, levels=levels, linewidths=0.7, cmap=cmap, alpha=RFM_ALPHA)
    manual = [(-0.3, -0.1), (-0.25, -0.25), (-0.1, -0.25), (0, -0.25),
              (0.15, -0.25), (0.33, -0.17)]
    ax.clabel(CS, inline=True, manual=manual, fmt=lambda v: f" RFM={v:.1f}% ",
              fontsize=5, colors=cmap(np.linspace(0, 1, len(levels))), inline_spacing=1)


def plot_traj(ax, pc_x, pc_y, big=False):
    x = yearly[pc_x].values; y = yearly[pc_y].values; years = yearly["year"].values
    s = ax.scatter(x, y, c=years, cmap="cool", s=40 if big else 8,
                   alpha=0.8 if big else 0.7,
                   edgecolors="black", linewidths=0.75 if big else 0.3, zorder=3)
    if big:
        for i in range(len(x) - 1):
            ax.annotate("", xy=(x[i+1], y[i+1]), xytext=(x[i], y[i]),
                        arrowprops=dict(arrowstyle="->", color=ARROW_COLOR,
                                         lw=0.5, alpha=ARROW_ALPHA, mutation_scale=8),
                        zorder=2)
    else:
        ax.plot(x, y, color=ARROW_COLOR, lw=0.3, alpha=0.3, zorder=1)
    return s


def plot_loading(ax, pc_num):
    vals = [loadings[f][f"PC{pc_num}"] for f in feature_order]
    ax.bar(range(len(feature_order)), vals, color="lightgrey", alpha=0.8,
           edgecolor="black", linewidth=0.5)
    ax.axhline(0, color="k", linestyle="--", linewidth=0.8)
    ax.set_xticks(range(len(feature_order)))
    ax.set_xticklabels(["Height", "Bust", "Waist", "Hips"], rotation=45, ha="right", fontsize=6)
    ax.set_ylabel(f"PC{pc_num}", rotation=0, labelpad=0, va="top", ha="left", fontsize=6)
    ax.yaxis.set_label_coords(0.01, 1.1)
    ax.set_ylim(-0.75, 0.99)
    remove_spines(ax)
    ax.tick_params(axis="y", direction="in", length=4, labelsize=4)
    ax.tick_params(axis="x", direction="in", length=4)


def plot_events(ax):
    if event_means is None:
        ax.text(0.5, 0.5, "No career event data", transform=ax.transAxes,
                ha="center", va="center"); return
    for _, row in event_means.iterrows():
        event = row["career_event"]
        if event not in ["shows", "advertisements", "magazine_covers", "editorials"]:
            continue
        key = "fashion_shows" if event == "shows" else event
        color = CAREER_EVENT_COLORS.get(key, "#07AB92")
        ax.scatter(row["pc1"], row["pc2"], s=80, color=color, alpha=0.8,
                   edgecolors="black", linewidths=0.8, zorder=3)
        lbl = event.replace("_", " ").title()
        offset = (0, 0.08) if event in ("magazine_covers", "shows") else (-0.04, 0.1)
        ax.text(row["pc1"] + offset[0], row["pc2"] + offset[1], lbl,
                fontsize=4, ha="center" if event in ("magazine_covers", "shows") else "left",
                va="bottom")
    ax.set_xlabel("PC1", fontsize=5); ax.set_ylabel("PC2", fontsize=5)
    remove_spines(ax)
    ax.tick_params(axis="both", which="major", labelsize=4, length=2, width=0.5, direction="in")
    ax.grid(True, alpha=0.2, linewidth=0.3)
    ax.set_xlim(-0.5, 0.5); ax.set_ylim(-0.6, 0.4)


def plot_explained(ax):
    x = np.arange(1, len(evr) + 1)
    ax.bar(x, evr, color="lightgrey", alpha=0.7, edgecolor="black", linewidth=0.5)
    ax.set_xlabel("Principal Component", fontsize=6)
    ax.set_ylabel("Explained Variance", fontsize=6)
    ax.set_xticks(x); ax.set_xticklabels([f"PC{i}" for i in x])
    ax.set_ylim(0, max(evr) * 1.15)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y*100:.0f}%"))
    remove_spines(ax)
    ax.tick_params(axis="both", which="major", labelsize=5, length=2, width=0.5, direction="in")
    ax.grid(True, alpha=0.2, linewidth=0.3, axis="y")


fig = plt.figure(figsize=(FIGURE_WIDTH_CM * cm, FIGURE_WIDTH_CM * cm))
gs = gridspec.GridSpec(5, 5, figure=fig, hspace=0.5, wspace=0.27,
                        left=0, right=1, top=0.95, bottom=0)

ax_main = fig.add_subplot(gs[0:3, 0:3])
scatter_main = plot_traj(ax_main, "pc1", "pc2", big=True)
ax_main.set_xlabel("PC1", fontsize=7); ax_main.set_ylabel("PC2", fontsize=7)
remove_spines(ax_main)
ax_main.tick_params(axis="both", which="major", labelsize=6, length=3, width=0.5, direction="in")
ax_main.grid(True, alpha=0.2, linewidth=0.3)
add_rfm_contours(ax_main, V, feature_means, feature_scales, idx_height, idx_waist, RFM_LEVELS)
cbar = plt.colorbar(scatter_main, ax=ax_main, pad=0.05, fraction=0.13)
cbar.ax.set_title("Year", fontsize=6, pad=4); cbar.ax.tick_params(labelsize=6)

for pos, (x_pc, y_pc) in [
    ((0, 3), ("pc2", "pc3")), ((1, 3), ("pc2", "pc4")),
    ((3, 0), ("pc1", "pc3")), ((3, 1), ("pc1", "pc4")),
    ((3, 2), ("pc3", "pc4")),
]:
    ax = fig.add_subplot(gs[pos[0], pos[1]])
    plot_traj(ax, x_pc, y_pc, big=False)
    pcx_n = int(x_pc[2:]); pcy_n = int(y_pc[2:])
    ax.set_xlabel(f"PC{pcx_n}", fontsize=5); ax.set_ylabel(f"PC{pcy_n}", fontsize=5)
    remove_spines(ax)
    ax.tick_params(axis="both", which="major", labelsize=4, length=2, width=0.5, direction="in")
    ax.grid(True, alpha=0.2, linewidth=0.3)

ax_career = fig.add_subplot(gs[2, 3]); plot_events(ax_career)
ax_var = fig.add_subplot(gs[3, 3]); plot_explained(ax_var)
for i, pc in enumerate(range(1, 5)):
    plot_loading(fig.add_subplot(gs[i, 4]), pc)

for ext in ("png", "pdf"):
    fig.savefig(FIG / f"pca_temporal_evolution_{GENDER}.{ext}", dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"Saved pca_temporal_evolution_{GENDER}.{{png,pdf}}")
