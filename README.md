# Cultural evolution of beauty standards

[![PNAS](https://img.shields.io/badge/PNAS-10.1073%2Fpnas.2602380123-1a78c2)](https://www.pnas.org/doi/10.1073/pnas.2602380123)
[![arXiv](https://img.shields.io/badge/arXiv-2512.08861-B31B1B.svg)](https://arxiv.org/abs/2512.08861)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.11990046-blue)](https://zenodo.org/records/17638160)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


This folder contains the data slices and Python scripts needed to reproduce
its figures. It is self-contained: running any script from `scripts/` reads
inputs from `data/` and writes outputs to `figures/`. No data outside this
folder is required.

## Layout

```
data_sharing/
├── data/             plot-ready CSV / JSON inputs
├── scripts/          one Python script per figure
├── figures/          PDF outputs (the scripts also write PNGs when re-run)
├── requirements.txt  Python dependencies
└── README.md
```

## Reproducing a figure

```bash
cd data_sharing
pip install -r requirements.txt
cd scripts
python <script_name>.py
```

Outputs land in `../figures/` as PNG and PDF (and, in a few cases, a companion
CSV / `.tex` table).

To regenerate every figure in one go:

```bash
cd data_sharing/scripts
for f in *.py; do
  [ "$f" = "utils.py" ] && continue
  python "$f"
done
```

`utils.py` is a helper module (fonts, colours, figure sizes) and is not meant
to be run on its own. Two scripts (`outliers_comparison.py`,
`measurement_evolution_plots.py`) regenerate both the female and male variants
when called once, via an internal `subprocess` re-invocation; you do not need
to run them twice.

## External data sources

Two of the shipped inputs come from public datasets:

- **NHANES** (National Health and Nutrition Examination Survey, US CDC) —
  source of `data/nhanes_female_17_40.csv`, `data/nhanes_rfm_{female,male}_filtered.csv`,
  and `data/pca_nhanes_projection_{female,male}.csv`. Public-use data, distributed
  by the US Centers for Disease Control and Prevention. The `SEQN` column is the
  NHANES respondent sequence number (not personally identifying).
  Homepage: <https://www.cdc.gov/nchs/nhanes/index.htm>;
  data downloads: <https://wwwn.cdc.gov/nchs/nhanes/Default.aspx>.

- **Natural Earth** — source of the country shapefile at
  `data/naturalearth_110m_countries/` used by `choropleth_models.py`. Public-domain
  cartographic data.
  Homepage: <https://www.naturalearthdata.com/>;
  the bundled file is the 110 m Cultural "Admin 0 – Countries" shapefile:
  <https://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-admin-0-countries/>.

---

## Plot index

### age_distribution.py
- **Figure**: `figures/age_distribution.{png,pdf}`
- **Shows**: age distribution of fashion-event records, overall and per event
  type (Shows, Editorials, Advertisements, Magazine Covers), with overall
  P25 / median / P75 vertical lines.
- **Shipped inputs**: `data/age_distribution_records.csv` (1-year-bin counts
  per `event_type × age`), `data/age_distribution_meta.csv` (total records
  and unique-model counts per event).
- **Original raw inputs**: `data/models_nationality.csv` joined with
  `data/career_{shows,editorials,advertisements,magazine_covers}_merged.csv`;
  ages restricted to 12–65 and years > 1950.

### age_evolution.py
- **Figure**: `figures/age_evolution.{png,pdf}`
- **Shows**: mean age (with 5th–95th-percentile band) of fashion-event
  records over 2000–2024, per event type.
- **Shipped inputs**: `data/age_evolution_by_year.csv`
  (`event_type, year, mean, q05, q95, n`).
- **Original raw inputs**: same as `age_distribution.py`.

### body_tails.py
- **Figure**: `figures/body_tails_female_2000_2024.{png,pdf}` plus a
  regression-statistics CSV with the same base name.
- **Shows**: weighted-average evolution of body-measurement tail quantiles
  (P10…P99) for female models, 2000–2024, with per-quantile linear-regression
  slope annotations.
- **Shipped inputs**: `data/body_tails_female_2000_2024.csv` (per
  `event × measurement × year` quantile values plus the per-cell sample count).
- **Original raw inputs**:
  `data/event_models_by_year_{shows,advertisements,magazine_covers,editorials}_female_stats.json`.

### career_evolution.py
- **Figures**:
  `figures/career_records_by_category_per_year.{png,pdf}`,
  `figures/records_by_gender_per_year.{png,pdf}`,
  `figures/career_records_stacked_area.png`.
- **Shows**: volume of fashion-event records per year, broken down by
  category, by gender, and stacked.
- **Shipped inputs**: `data/career_records_by_year.csv`
  (`year, category, gender, count`).
- **Original raw inputs**:
  `data/career_{shows,editorials,advertisements,magazine_covers,lookbooks,catalogues}_merged.csv`
  joined with `data/models_measure_with_gender_metrics_quality_enhanced.csv`
  for gender.

### choropleth_models.py
- **Figures**: `figures/choropleth_model_count.{png,pdf}`,
  `figures/choropleth_record_count.{png,pdf}`.
- **Shows**: world maps of unique models and total records by country of origin.
- **Shipped inputs**: `data/choropleth_country_counts.csv` plus the bundled
  NaturalEarth 110 m countries shapefile in `data/naturalearth_110m_countries/`.
  If the shapefile is removed, the script falls back to downloading it from
  the public NaturalEarth CDN.
- **Original raw inputs**: `data/models_nationality.csv` joined with the
  career-event CSVs; the nationality → ISO mapping was applied upstream.

### entropy_evolution.py
- **Figure**: `figures/entropy_evolution_2000_2024_female.{png,pdf}`
- **Shows**: year-by-year entropy of categorical (hair, eyes, world region,
  ethnicity) and numerical (height, bust, waist, hips, RFM) attributes for
  female models, per event.
- **Shipped inputs**: `data/entropy_evolution_female.csv`
  (`year, event, variable, entropy`).
- **Original raw inputs**: `data/event_models_by_year_*_female_stats.json`,
  `data/model_info_from_profilepic.csv`, `data/career_*_merged.csv`,
  `data/models_shows_all.json`.

### event_study_panel.py
- **Figure**: `figures/event_study_panel.{png,pdf}`
- **Shows**: event-study coefficients (mean RFM, P10, P25) around the 2006
  Milan charter and the 2017 Paris regulation.
- **Shipped inputs**: `data/event_study_milan_2006.csv`,
  `data/event_study_paris_2017.csv`.
- **Original raw inputs**:
  `policy/figures/did_{milan_2006,paris_2017}_event_study_results.csv`.

### forest_plot_outliers_trends.py
- **Figures**:
  `figures/forest_plot_{iqr,skewness,kurtosis,outliers_combined}_trends_2000_2024_{female,male}_eu.{png,pdf}`
- **Shows**: Mann-Kendall / Sen-slope trend estimates of IQR, skewness, and
  kurtosis for body measurements over 2000–2024 (female and male).
- **Shipped inputs**: `data/forest_outliers_trends_{female,male}_eu.csv`.
- **Original raw inputs**:
  `plots/output/outliers_trend_analysis_2000_2024_{female,male}_eu.csv`.

### forest_plot_std_trends.py
- **Figures**: `figures/forest_plot_std_trends_{female,male}_eu.{png,pdf}`
- **Shows**: Mann-Kendall / Sen-slope trend estimates of measurement standard
  deviation per event type and measurement.
- **Shipped inputs**: `data/forest_std_trends_{female,male}_eu.csv`.
- **Original raw inputs**:
  `plots/output/std_trend_analysis_2000_2024_female_eu.csv` and
  `std_trend_analysis_2010_2024_male_eu.csv`.

### heterogeneous_policy.py
- **Figure**: `figures/heterogeneous_policy_analysis.{png,pdf}`
- **Shows**: heterogeneous policy effects across hierarchy tiers (top and
  bottom 10 % RFM rates) and across the Milan / Paris cities (mean and
  25th-percentile DiD).
- **Shipped inputs**: `data/heterogeneous_policy_tiers.csv`,
  `data/city_charter_timeseries.csv` (aggregated to 4 groups:
  `Milan`, `Paris`, `MilanControl`, `ParisControl`, where each control is the
  `n_records`-weighted aggregate of New York, London, "Other", and the opposite
  policy city, with pooled-variance SE).
- **Original raw inputs**:
  `hierarchy/figures/rfm_{bottom10pct,top10pct}_stats_centrality_*.csv`,
  per-city RFM time series from the upstream policy pipeline.

### hierarchy_table.py
- **Outputs** (table, no figure image): `figures/hierarchy_top30.csv`,
  `figures/hierarchy_top30.tex`.
- **Shows**: top-30 brands ranked by network prestige with their tier, record
  count, model count, % Elite overlap, and model-prestige summary statistics.
- **Shipped inputs**: `data/hierarchy_top30.csv`.
- **Original raw inputs**:
  `hierarchy/figures/{brand_prestige,brand_hierarchy,model_prestige}_centrality_shows_advertisements_editorials_magazine_covers.csv`
  joined with `data/career_*_merged.csv`.

### intersectionality_panel.py
- **Figure**: `figures/intersectionality_panel.{png,pdf}`
- **Shows**: a 2 × 2 panel for the race × plus-size analysis on 2010–2024.
  (a) Yearly share of non-white models with 95 % bootstrap CI.
  (b) Yearly plus-size proportion (`dress_us_final >= 12`) for white,
  non-white, and all models, with 95 % bootstrap CIs.
  (c) Yearly odds ratio of being plus-size (non-white vs white) with 95 % CI.
  (d) Yearly absolute difference in plus-size rate (non-white − white,
  percentage points).
- **Shipped inputs**:
  `data/intersectionality_panel_proportions_2010_2024.csv`
  (long-format yearly proportions with bootstrap CIs for the four series
  plotted in panels a and b: `nonwhite_share`, `plussize_white`,
  `plussize_nonwhite`, `plussize_all`);
  `data/intersectionality_panel_yearly_2010_2024.csv`
  (yearly two-sample proportion test for white vs non-white plus-size rates,
  with risk ratio, odds ratio, CIs, z-statistic and p-value — drives
  panels c and d).
- **Original raw inputs**:
  `intersectionality/data/work_master.csv` (work-level table with
  `race_consolidated` and `plus_sized`), aggregated upstream by
  `intersectionality/create_panel_figure.py`;
  `intersectionality/results/tables/proportion_test_yearly_2010_2024.csv`.

### measurement_evolution_plots.py
- **Figures**:
  `figures/measurements_evolution_with_std_2000_female_eu.{png,pdf}`,
  `figures/measurements_evolution_with_std_2010_male_eu.{png,pdf}`.
  Running the script once produces both gender variants.
- **Shows**: mean (with ±SEM band) and standard-deviation (with chi-square
  95 % CI band) evolution of body measurements (height, bust, waist, hips,
  RFM) per event type, plus stacked composition bars for hair colour, eye
  colour, and world region.
- **Shipped inputs**:
  `data/measurement_evolution_{female,male}_eu_numeric.csv` (mean / std / n),
  `data/measurement_evolution_{female,male}_eu_categorical.csv` (hair / eyes /
  world_region proportions).
- **Original raw inputs**: `data/event_models_by_year_*_{female,male}_stats.json`.

### network_analysis_panel.py
- **Figure**: `figures/network_analysis_comprehensive.{png,pdf}`
- **Shows**: multi-panel summary of the brand–model bipartite network: 2-D
  t-SNE embeddings, models coloured by RFM (per gender), top brands per tier
  table, prestige vs Instagram followers / appearance count / record count
  scatters, and model prestige vs RFM.
- **Shipped inputs**: `data/network_node_coords.csv`,
  `data/network_model_prestige.csv`, `data/network_brand_prestige.csv`,
  `data/network_brand_tier_top10.json`.
- **Original raw inputs**: `hierarchy/results/network_embedding_tsne.json`,
  `hierarchy/figures/{model,brand}_prestige_centrality_*.csv`,
  `hierarchy/results/hierarchy_centrality_*_2000_2024.json`,
  `data/models_measure_with_gender_metrics_quality_enhanced.csv`.

### outliers_comparison.py
- **Figure**: `figures/iqr_skew_kurtosis_female_eu.{png,pdf}`.
  Running this script also re-invokes itself to produce the male variant
  via `outliers_comparison_male.py` (which simply sets `OC_GENDER=male` and
  calls this script).
- **Shows**: multi-panel comparison for female models, 2000–2024. Top: 3 × 4
  grid of IQR / skewness / kurtosis trends per event for Bust / Waist / Hips /
  RFM. Bottom-left: NHANES vs models RFM histogram (density) and a
  year-by-year delta-RFM scatter with linear trend. Bottom-right:
  model–NHANES PCA scatter with RFM iso-lines reconstructed from the shipped
  scaler statistics, alongside four PCA loading bar plots.
- **Shipped inputs**: `data/outliers_female_eu_moments.csv`,
  `data/measurement_evolution_female_eu_numeric.csv` (per-year model RFM
  mean), `data/nhanes_rfm_female_filtered.csv`, `data/models_rfm_female.csv`,
  `data/pca_female_coords_sample.csv`, `data/pca_nhanes_projection_female.csv`,
  `data/pca_female_loadings.json`.
- **Original raw inputs**: `data/event_models_by_year_*_female_stats.json`,
  `data/nhanes/nhanes_filtered_rfm_female.csv`,
  `data/models_measure_with_gender_metrics_quality_enhanced.csv`,
  `data/pca_results/career_pca_female_2000-2025_*`,
  `data/pca_results/nhanes_pca_projection_female.csv`.

### outliers_comparison_male.py
- **Figure**: `figures/iqr_skew_kurtosis_male_eu.{png,pdf}`
- **Shows**: male counterpart of `outliers_comparison.py`, covering 2010–2024.
- **Shipped inputs**: `data/outliers_male_eu_moments.csv`,
  `data/measurement_evolution_male_eu_numeric.csv`,
  `data/nhanes_rfm_male_filtered.csv`, `data/models_rfm_male.csv`,
  `data/pca_male_coords_sample.csv`, `data/pca_nhanes_projection_male.csv`,
  `data/pca_male_loadings.json`.
- **Original raw inputs**: male equivalents of the female files above.

### pca_temporal_plot.py
- **Figure**: `figures/pca_temporal_evolution_female.{png,pdf}`
- **Shows**: yearly trajectory of female-model body composition projected on
  the first PCA components, with RFM contour lines, explained-variance and
  loading annotations, and per-career-event averages.
- **Shipped inputs**: `data/pca_female_yearly_means.csv`,
  `data/pca_female_career_event_means.csv`, `data/pca_female_loadings.json`
  (explained-variance ratios, loadings, and scaler mean / scale to
  reconstruct the RFM contours without shipping the original pickle).
- **Original raw inputs**:
  `data/pca_results/career_pca_female_2000-2025_{coordinates.csv,summary.json,models.pkl}`.

### quantile_policy_analysis.py
- **Figure**: `figures/quantile_policy_analysis.{png,pdf}`
- **Shows**: RFM-quantile evolution (Q10 / Q25 / Q75 / Q90) for Milan vs the
  Control group around 2006, and Paris vs Control around 2017.
- **Shipped inputs**: `data/city_charter_timeseries.csv` (same aggregated
  4-group file used by `heterogeneous_policy.py`; the Milan panels use
  `MilanControl`, the Paris panels use `ParisControl`).
- **Original raw inputs**: per-city RFM time series from the upstream policy
  pipeline.

### rfm_by_age_group.py
- **Figures**: `figures/rfm_by_age_group.{png,pdf}`,
  `figures/rfm_by_age_group_matched.{png,pdf}`
- **Shows**: density of RFM for fashion models vs NHANES women aged 17–40,
  in 17–20, 21–25, 26–30, 31–40 age bins; raw and age-matched
  (NHANES sub-sampled to match the model age distribution).
- **Shipped inputs**:
  `data/rfm_by_age_group_models_hist.csv` — per-integer-age × per-RFM-bin
  count table for models (`age_int, rfm_bin_left, rfm_bin_right, count`,
  RFM bin edges = `np.linspace(10, 55, 50)`). The age-matching resampler
  derives the model age distribution from this table by summing counts per
  `age_int`;
  `data/rfm_by_age_group_models_medians.csv` — exact per-age-group median
  RFM and `n` for the dashed median lines in the bottom panels;
  `data/nhanes_female_17_40.csv` — NHANES female non-pregnant 17–40 with
  `Age, RFM, age_int` (NHANES is public).
- **Original raw inputs**: `data/nhanes/nhanes.csv`,
  `data/models_measure_with_gender_metrics_quality_enhanced.csv`,
  `data/models_nationality.csv`, `data/career_*_merged.csv`.

### rfm_tiers_sensitivity.py
- **Figure**: `figures/rfm_tiers_sensitivity.{png,pdf}`
- **Shows**: sensitivity of top / bottom-10 % RFM rates across hierarchy-tier
  counts (6, 8, 10) with Wilson 95 % CI bars.
- **Shipped inputs**: `data/rfm_tiers_sensitivity.csv`
  (`n_tiers, tier, panel, rate, ci_lower, ci_upper, n`).
- **Original raw inputs**:
  `hierarchy/figures/brand_prestige_centrality_*.csv`,
  `data/career_*_merged.csv`,
  `data/models_measure_with_gender_metrics_quality_enhanced.csv`.

---
