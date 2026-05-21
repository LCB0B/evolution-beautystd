"""Comprehensive network-analysis multi-panel figure.

Reads:
  ../data/network_node_coords.csv
  ../data/network_model_prestige.csv
  ../data/network_brand_prestige.csv
  ../data/network_brand_tier_top10.json
Writes: ../figures/network_analysis_comprehensive.{png,pdf}
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy import stats
from utils import cm, FIGURE_WIDTH_CM, remove_spines

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"; FIG.mkdir(exist_ok=True)

NODE_COLORS = {"model": "#FF7DBE", "brand": "#61C2FF", "magazine": "#8E44AD"}
TIER_COLORS = {"Elite": "#EC6C63", "High": "#D8A499", "Mid": "#C6CDF7", "Low": "#7294D4"}
METHOD = "t-SNE"


def prestige_to_size(values, min_size=0.1, max_size=2):
    log_p = np.log10(np.array(values) + 1e-6)
    norm = (log_p - log_p.min()) / (log_p.max() - log_p.min())
    return min_size + norm * (max_size - min_size)


def plot_all_nodes(ax, df):
    for nt, color in NODE_COLORS.items():
        sub = df[df["node_type"] == nt]
        if sub.empty:
            continue
        sizes = prestige_to_size(sub["centrality"].values, 0.1, 2)
        marker = "^" if nt == "model" else ("o" if nt == "brand" else "s")
        ax.scatter(sub["x"], sub["y"], s=sizes, c=color, marker=marker,
                    alpha=0.6, edgecolors="black", linewidths=0,
                    label=nt.title() + "s", zorder=2)
    ax.set_xlabel(f"{METHOD} Dimension 1", fontsize=6)
    ax.set_ylabel(f"{METHOD} Dimension 2", fontsize=6)
    ax.legend(fontsize=5, loc="upper right", frameon=True, markerscale=3)
    remove_spines(ax)
    ax.tick_params(axis="both", which="major", labelsize=5, length=2, width=0.5, direction="in")
    ax.grid(True, alpha=0.2, linewidth=0.3)
    ax.set_title("Network of Media and Fashion", fontsize=7, fontweight="bold")
    ax.set_aspect("equal")


def plot_brands(ax, df):
    bm = df[df["node_type"].isin(["brand", "magazine"])]
    sizes = prestige_to_size(bm["centrality"].values, 1, 1.5)
    sc = ax.scatter(bm["x"], bm["y"], s=sizes, c=np.log(bm["centrality"]),
                     cmap="viridis", marker="o", alpha=0.8,
                     edgecolors="black", linewidths=0, zorder=2)
    cbar = plt.colorbar(sc, ax=ax, pad=0.02, fraction=0.046)
    cbar.set_label("Prestige (Centrality)", fontsize=6, rotation=90, va="bottom")
    cbar.ax.tick_params(labelsize=5)
    ax.set_title("Brands & Magazines", fontsize=7, fontweight="bold")
    remove_spines(ax)
    ax.tick_params(axis="both", which="major", labelsize=5, length=2, width=0.5, direction="in")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.2, linewidth=0.3)


def plot_models_gender(ax, df, mp, gender, min_size=2, max_size=4):
    mods = df[df["node_type"] == "model"].merge(mp[["name", "rfm", "gender"]],
                                                   left_on="node", right_on="name", how="left")
    sub = mods[(mods["rfm"].notna()) & (mods["gender"] == gender)]
    if sub.empty:
        ax.text(0.5, 0.5, f"No {gender} model RFM", ha="center", va="center"); return
    sizes = prestige_to_size(sub["centrality"].values, min_size, max_size)
    sc = ax.scatter(sub["x"], sub["y"], s=sizes, c=sub["rfm"], cmap="RdYlBu_r",
                     marker="^", alpha=0.7, edgecolors="black", linewidths=0,
                     vmin=sub["rfm"].quantile(0.05), vmax=sub["rfm"].quantile(0.95))
    cbar = plt.colorbar(sc, ax=ax, pad=0.02, fraction=0.046)
    cbar.set_label("RFM", fontsize=6, rotation=0, ha="left")
    cbar.ax.tick_params(labelsize=5)
    ax.set_title(f"{gender.title()} Models", fontsize=7, fontweight="bold")
    remove_spines(ax)
    ax.tick_params(axis="both", which="major", labelsize=5, length=2, width=0.5, direction="in")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.2, linewidth=0.3)


def plot_table(ax, tier_top10):
    ax.axis("off")
    y0, dy = 0.92, 0.034
    ax.text(0.5, y0, "10 Brands/Magazines\nper Tier",
             fontsize=6, fontweight="bold", ha="center", va="top")
    y = y0 - dy * 2
    for tier in ["Elite", "High", "Mid", "Low"]:
        brands = tier_top10.get(tier, [])[:10]
        if not brands:
            continue
        ax.text(0.04, y, tier, fontsize=7, fontweight="bold",
                 color=TIER_COLORS[tier], ha="left", va="top")
        for i, brand in enumerate(brands):
            ax.text(0.16, y - (i + 1) * dy * 0.7, f"{i+1}. {brand}",
                    fontsize=5, ha="left", va="top")
        y -= (len(brands) + 1.5) * dy * 0.7


def scatter_log(ax, df, xcol, ycol, ccol, xlabel, ylabel, cmap="viridis", clabel=None):
    df = df[(df[xcol].notna()) & (df[ycol].notna())
            & (df[xcol] > 0) & (df[ycol] > 0)]
    sc = ax.scatter(df[xcol], df[ycol], s=1, c=df[ccol], cmap=cmap, alpha=0.6,
                     edgecolors="none")
    if cmap == "viridis":
        sc.set_norm(LogNorm())
    corr, _ = stats.pearsonr(np.log10(df[xcol]), np.log10(df[ycol]))
    ax.text(0.05, 0.99, f"Pearson correlation: {corr:.2f}",
             transform=ax.transAxes, fontsize=5, va="top")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(xlabel, fontsize=6); ax.set_ylabel(ylabel, fontsize=6)
    remove_spines(ax)
    ax.tick_params(axis="both", which="major", labelsize=5, length=2, width=0.5, direction="in")
    ax.grid(True, alpha=0.2, linewidth=0.3, which="both")
    if clabel:
        cbar = plt.colorbar(sc, ax=ax, pad=0.02, fraction=0.046)
        cbar.set_label(clabel, fontsize=5, rotation=90, va="bottom")
        cbar.ax.tick_params(labelsize=5)


def plot_brand_vs_records(ax, df):
    df = df[(df["prestige_raw"] > 0) & (df["record_count"] > 0)]
    for tier in ["Elite", "High", "Mid", "Low"]:
        td = df[df["tier"] == tier]
        if td.empty:
            continue
        ax.scatter(td["prestige_raw"], td["record_count"], s=1,
                    c=TIER_COLORS[tier], alpha=0.6, edgecolors="none", label=tier)
    corr, _ = stats.pearsonr(np.log10(df["prestige_raw"]), np.log10(df["record_count"]))
    ax.text(0.05, 0.98, f"Pearson correlation: {corr:.2f}", transform=ax.transAxes,
             fontsize=5, va="top")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_ylim(bottom=3)
    ax.set_xlabel("Prestige Score", fontsize=6); ax.set_ylabel("Number of Records", fontsize=6)
    remove_spines(ax)
    ax.tick_params(axis="both", which="major", labelsize=5, length=2, width=0.5, direction="in")
    ax.grid(True, alpha=0.2, linewidth=0.3, which="both")


def plot_prestige_vs_rfm(ax, mp, gender="female"):
    df = mp[(mp["gender"] == gender) & mp["prestige_raw"].notna() & mp["rfm"].notna()]
    if df.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center"); return
    sc = ax.scatter(df["prestige_raw"], df["rfm"], s=2, c=df["rfm"],
                     cmap="viridis", alpha=0.7, edgecolors="none")
    _, _, r, _, _ = stats.linregress(df["prestige_raw"], df["rfm"])
    ax.text(0.05, 0.98, f"Pearson correlation: {r:.2f}", transform=ax.transAxes,
             fontsize=5, va="top")
    ax.set_xscale("log")
    ax.set_xlabel("Prestige Score", fontsize=6)
    ax.set_ylabel("Relative Fat Mass (RFM)", fontsize=6)
    remove_spines(ax)
    ax.tick_params(axis="both", which="major", labelsize=5, length=2, width=0.5, direction="in")
    ax.grid(True, alpha=0.2, linewidth=0.3)


network_df = pd.read_csv(DATA / "network_node_coords.csv")
mp = pd.read_csv(DATA / "network_model_prestige.csv")
bp = pd.read_csv(DATA / "network_brand_prestige.csv")
with open(DATA / "network_brand_tier_top10.json") as f:
    tier_top10 = json.load(f)

fig = plt.figure(figsize=(FIGURE_WIDTH_CM * cm, FIGURE_WIDTH_CM * cm))
gs = fig.add_gridspec(5, 5, hspace=0.5, wspace=0.7, left=0, right=1, top=1, bottom=0)
ax_a = fig.add_subplot(gs[0:2, 0:2]); plot_all_nodes(ax_a, network_df)
ax_b = fig.add_subplot(gs[0:2, 2:4], sharex=ax_a, sharey=ax_a); plot_brands(ax_b, network_df)
ax_d = fig.add_subplot(gs[0:4, 4]); plot_table(ax_d, tier_top10)
ax_e = fig.add_subplot(gs[2:4, 0:2]); plot_models_gender(ax_e, network_df, mp, "female")
ax_f = fig.add_subplot(gs[2:4, 2:4], sharex=ax_e, sharey=ax_e); plot_models_gender(ax_f, network_df, mp, "male")
ax_g = fig.add_subplot(gs[4, 0])
scatter_log(ax_g, mp.rename(columns={}), "prestige_raw", "instagram_followers",
            "appearance_count", "Prestige Score", "Instagram Followers", clabel="Appearances")
ax_g.set_ylim(bottom=100)
ax_h = fig.add_subplot(gs[4, 1])
scatter_log(ax_h, mp, "prestige_raw", "appearance_count", "prestige_percentile",
             "Prestige Score", "Appearance Count", cmap="plasma", clabel="Prestige %ile")
ax_h.set_ylim(bottom=3)
ax_k = fig.add_subplot(gs[4, 2]); plot_prestige_vs_rfm(ax_k, mp, "female")
ax_i = fig.add_subplot(gs[4, 3]); plot_brand_vs_records(ax_i, bp)

panel_positions = [
    (-0.04, 1.03, "a"), (0.4, 1.03, "b"), (0.85, 1.03, "c"),
    (-0.04, 0.6, "d"), (0.4, 0.6, "e"),
    (-0.04, 0.16, "f"), (0.195, 0.16, "g"),
    (0.4, 0.16, "h"), (0.6, 0.16, "i"),
]
for x, y, label in panel_positions:
    fig.text(x, y, label, fontsize=10, fontweight="bold", va="top")

for ext in ("png", "pdf"):
    fig.savefig(FIG / f"network_analysis_comprehensive.{ext}", dpi=300, bbox_inches="tight")
plt.close(fig)
print("Saved network_analysis_comprehensive.{png,pdf}")
