"""Choropleth maps of unique models / career records per country of origin.

Reads:  ../data/choropleth_country_counts.csv
        ../data/naturalearth_110m_countries/  (or falls back to NaturalEarth URL)
Writes: ../figures/choropleth_model_count.{png,pdf}
        ../figures/choropleth_record_count.{png,pdf}
"""
from pathlib import Path
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize
from utils import cm, save_figure, FIGURE_WIDTH_CM

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"; FIG.mkdir(exist_ok=True)

counts = pd.read_csv(DATA / "choropleth_country_counts.csv")

shp_dir = DATA / "naturalearth_110m_countries"
shp_files = list(shp_dir.glob("*.shp")) if shp_dir.exists() else []
if shp_files:
    world = gpd.read_file(shp_files[0])
else:
    print("Local NaturalEarth shapefile not found, downloading...")
    world = gpd.read_file("https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip")


def plot_choropleth(col, title, filename, vmax=300000):
    data = counts[["iso_a3", col]].rename(columns={col: "count"})
    fig, ax = plt.subplots(
        figsize=(FIGURE_WIDTH_CM * cm, FIGURE_WIDTH_CM * 0.45 * cm),
        constrained_layout=True)
    w = world[world["NAME"] != "Antarctica"].copy()
    iso_col = "ISO_A3" if "ISO_A3" in w.columns else "iso_a3"
    eh_col = "ISO_A3_EH" if "ISO_A3_EH" in w.columns else None
    if eh_col:
        w["iso_key"] = w[iso_col].where(w[iso_col] != "-99", w[eh_col])
    else:
        w["iso_key"] = w[iso_col]
    merged = w.merge(data, left_on="iso_key", right_on="iso_a3", how="left")
    merged = merged.to_crs("ESRI:54030")
    merged.plot(ax=ax, color="#EEEEEE", edgecolor="white", linewidth=0.2)
    has_data = merged.dropna(subset=["count"])
    norm = LogNorm(vmin=max(1, data["count"].min()), vmax=vmax)
    has_data.plot(ax=ax, column="count", cmap="YlOrRd", norm=norm,
                   edgecolor="white", linewidth=0.2, legend=True,
                   legend_kwds={"shrink": 0.6, "label": title, "pad": 0.01})
    ax.set_axis_off(); ax.set_title(title, loc="left")
    save_figure(fig, filename, FIG, formats=["png", "pdf"])
    plt.close(fig)


plot_choropleth("model_count", "Unique models per country", "choropleth_model_count")
plot_choropleth("record_count", "Career records per country", "choropleth_record_count")
print("Saved choropleth_{model,record}_count.{png,pdf}")
