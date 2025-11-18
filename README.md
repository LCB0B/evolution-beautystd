# Representation Diversity Analysis

[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.11990046-blue)](https://zenodo.org/records/17638160)
[![arXiv](https://img.shields.io/badge/arXiv-2405.08746-B31B1B.svg)](https://arxiv.org/pdf/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)

A comprehensive research project analyzing diversity trends in the fashion modeling industry through body measurements, demographics, and hierarchical positioning across multiple fashion contexts (2000-2024).

## Overview

This project examines diversity evolution in fashion modeling using data from the Fashion Model Directory (FMD) and Models.com, covering 15,183 models and almost 800 thousands career events spanning over two decades. The analysis integrates multiple methodologies—network analysis, causal inference, intersectional statistics—to understand how body measurement standards, demographic representation, and fashion hierarchy interact to shape industry diversity.

### Key Findings

- **Hierarchy Heterogeneity**: Diversity evolution varies significantly across fashion hierarchy tiers, with 20% of pairwise tier comparisons meeting conservative significance criteria
- **Policy Impact**: The 2017 French Fashion Regulations show measurable effects on model body measurements (RFM) for French brands and charter signatories
- **Intersectional Patterns**: Plus-size representation exhibits complex interactions with race/ethnicity and geographic origin, with temporal trends varying by intersectional group

## Research Questions

1. **Temporal Evolution**: How have body measurement standards (height, bust, waist, hips, RFM) evolved in fashion modeling from 2000-2024?
2. **Hierarchy Effects**: Does diversity evolution vary across fashion hierarchy tiers (elite vs. mainstream brands)?
3. **Policy Impact**: What was the causal effect of the 2017 French Fashion Regulations on model body measurements?
4. **Intersectionality**: How does plus-size representation vary at the intersection of race/ethnicity and geography (Global North vs. South)?

## Key Features

- **Multi-Source Data Integration**: Merges Fashion Model Directory (FMD) and Models.com datasets with automated deduplication
- **Advanced Gender Detection**: 4-method consensus system (gender-guesser, US Census, WGND, FairFace image analysis)
- **Fashion Hierarchy Analysis**: Two complementary methods (centrality-based HITS algorithm, violation-based minimum ranking)
- **Causal Policy Evaluation**: Difference-in-Differences and Event Study designs with robustness checks
- **Intersectionality Framework**: 4 complete analyses examining plus-size × race × geography interactions

## Installation

### Requirements

- Python 3.8+


### Setup

```bash
# Clone the repository
git clone [repository-url]
cd diversity

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import pandas, sklearn, matplotlib, networkx; print('Setup complete!')"
```

## Quick Start

### 1. Data Processing

```bash
# Process data and detect gender
python src/get_gender.py
python src/make_master_data.py
```

### 2. Fashion Hierarchy Analysis

```bash
python hierarchy/flexible_hierarchy_analysis.py
```

### 3. Policy Impact Analysis (2017 French Regulations)

```bash
python policy/run_policy_analysis.py
python policy/event_study.py
```

### 4. Intersectionality Analysis

```bash
cd intersectionality
python run_all_combinations.py --combo plussize_race
python run_all_combinations.py --combo rfm5_race
```

## Project Architecture

```
diversity/
├── data/                           # Raw and processed datasets
│   ├── models_measure_*.csv        # Core measurement datasets
│   └── career_*_merged.csv         # Career events (FMD + Models.com)
├── src/                            # Core data processing pipeline
│   ├── get_gender.py               # Multi-method gender detection
│   ├── make_master_data.py         # Master dataset creation
│   └── analysis.py                 # Statistical analysis
├── hierarchy/                      # Fashion hierarchy analysis
│   ├── flexible_hierarchy_analysis.py
│   ├── figures/
│   └── results/
├── policy/                         # 2017 French policy impact
│   └── did_paris_2017.py
├── intersectionality/              # Plus-size × race × geography
│   ├── run_all_combinations.py
│   └── results/
├── dotcom/                         # Models.com data collection
│   └── run.sh
└── results/                        # Analysis outputs
```

## Data Pipeline Workflow

```
1. RAW DATA COLLECTION
   ├── FMD data (models_measure.csv, models_shows_all.json, models_nationality.csv)
   └── Models.com scraping (dotcom/run.sh)

2. GENDER DETECTION
   └── Multi-method consensus (src/get_gender.py)

3. MASTER DATA CREATION
   ├── Merge all sources (src/make_master_data.py)
   ├── Compute body metrics (RFM, WHR, WHtR)
   └── Add nationality mappings

4. CAREER DATA MERGING
   └── Parse and merge career events across sources

5. ANALYSIS EXECUTION
   ├── Hierarchy analysis (hierarchy/)
   ├── Policy analysis (policy/)
   └── Intersectionality analysis (intersectionality/)
```

## Main Analyses

### 1. Gender Detection System

Multi-method consensus system (`src/get_gender.py`) using gender-guesser, US Census data, WGND, and FairFace image analysis. Achieves 96%+ coverage with confidence scoring.

### 2. Fashion Hierarchy Analysis

Examines diversity evolution across fashion hierarchy tiers using bipartite network analysis. Two methods: centrality-based (HITS algorithm) and violation-based ranking (Clauset et al. 2015). Analyzes 1,084 brands with 1.47M observations (2000-2024), using Sen slope estimation for trend analysis.

**Key Finding**: 20% of pairwise tier comparisons show significant differences in diversity evolution patterns.

### 3. Policy Impact Analysis

Evaluates the causal effect of 2017 French Fashion Regulations on model body measurements (RFM) using Difference-in-Differences and Event Study designs. Treatment groups: French brands and LVMH/Kering charter signatories. Event window: -3 to +3 years with robustness checks.

### 4. Intersectionality Analysis

Examines plus-size representation at the intersection of race/ethnicity and geography. Four analyses: Plus-size × Race, Plus-size × Global North, High RFM × Race, High RFM × Global North. Uses logistic regression with bootstrap confidence intervals.

## Key Output Files

### Main Pipeline Outputs

```
data/
├── models_measure_with_gender_metrics_quality_enhanced.csv  # Final enhanced dataset
├── models_gender_complete.csv                                # Gender classifications
├── gender_consensus_rule_report.csv                          # Gender detection performance
├── career_shows_merged.csv                                   # Fashion shows (51M)
├── career_editorials_merged.csv                              # Editorials (23M)
├── career_advertisements_merged.csv                          # Ads (14M)
└── career_magazine_covers_merged.csv                         # Magazine covers (14M)
```


### Hierarchy Analysis Outputs

```
hierarchy/
├── figures/
│   ├── tier_diversity_trends_centrality_shows.png          # Main figures
│   ├── tier_diversity_trends_centrality_shows.csv          # Sen slopes + p-values
│   └── brand_hierarchy_centrality_shows.csv                # Brand tier classifications
└── results/
    └── hierarchy_centrality_shows_2000_2024.json           # Complete hierarchy with metadata

results/final_hierarchy_analysis/
├── tier_diversity_results.csv                              # 40 tier-measurement slopes
├── brand_hierarchy_positions.csv                           # 1,084 brand classifications
├── brand_hierarchy_summary.csv                             # Brand activity summary
├── final_analysis_report.txt                               # Executive summary
└── final_hierarchy_analysis.png                            # 6-panel visualization

results/slope_significance_testing/
├── tier_slope_significance_tests.csv                       # 60 pairwise comparisons
├── significance_assessment_report.txt                      # Conservative testing report
└── significance_assessment.png                             # Statistical visualization
```

### Policy Analysis Outputs

```
results/policy_analysis/
├── analysis_dataset.csv                        # Complete policy dataset
├── did_results.csv                             # DiD estimates
├── event_study_results.csv                     # -3 to +3 year coefficients
├── placebo_tests.csv                           # Pre-treatment robustness
├── control_group_tests.csv                     # Control group comparisons
└── time_window_tests.csv                       # Alternative windows

results/policy_plots/
├── event_study_french_brands.png               # Event study visualizations
├── event_study_charter_signatories.png
└── treatment_effects_did.png                   # DiD visualizations
```

### Intersectionality Outputs

```
intersectionality/results/
├── plussize_race/
│   ├── tables/
│   │   ├── sample_descriptives.csv             # Sample sizes by group-year
│   │   ├── logistic_regression_results.csv     # Regression coefficients
│   │   ├── predicted_probabilities.csv         # Model predictions
│   │   └── odds_ratios_by_year.csv             # Annual odds ratios
│   ├── figures/
│   │   ├── plussize_race_3panel.png            # Publication figure (PNG)
│   │   └── plussize_race_3panel.pdf            # Publication figure (PDF)
│   └── reports/
│       ├── model_summary.txt                   # Regression diagnostics
│       └── convergence_report.txt              # Bootstrap convergence
├── plussize_globalnorth/
├── rfm5_race/
└── rfm5_globalnorth/
```

## Methodologies

- **Sen Slope Analysis**: Non-parametric trend estimation (hierarchy analysis)
- **Difference-in-Differences**: Causal policy impact estimation
- **Event Study**: Dynamic treatment effects over time
- **Logistic Regression**: Binary outcome modeling with interactions
- **Bootstrap Resampling**: Uncertainty quantification (N=50-1000)
- **Bipartite Networks**: Model-brand collaboration networks
- **HITS Algorithm**: Centrality-based hierarchy ranking


## Dataset Coverage

### Models Dataset
- **Total models**: 15,183
- **Gender classification**: 96%+ coverage
- **Race/ethnicity (FairFace)**: 99% coverage
- **Race/ethnicity (Models.com)**: 30% coverage
- **Body measurements**: 96-99% per measurement
- **Nationality**: 85%+ coverage


### Analysis Periods
- **Hierarchy analysis**: 2000-2024 (data collection), 2015 (brand classification year)
- **Policy analysis**: 2013-2022 (2017 policy intervention)
- **Intersectionality**: 2011-2024
- **Temporal trends**: 2000-2024



## Documentation

- [`intersectionality/README.md`](intersectionality/README.md): Comprehensive intersectionality analysis guide
- [`INTERSECTIONALITY_RESULTS_SUMMARY.md`](INTERSECTIONALITY_RESULTS_SUMMARY.md): Complete intersectionality results
- [`PANEL_UPDATE_SUMMARY.md`](PANEL_UPDATE_SUMMARY.md): Panel figure updates

## Citation

If you use this codebase or dataset in your research, please cite:

```bibtex
@article{diversity2024,
  title={Fashion Industry Diversity Analysis: Body Measurements, Demographics, and Hierarchy},
  author={[Authors]},
  journal={[Journal]},
  year={2024},https://zenodo.org/records/17638160
  doi={10.5281/zenodo.17638160},
  url={https://arxiv.org/abs/}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Contact

For questions or collaborations, please open an issue on the GitHub repository.

---

**Note**: This is an active research project. Analysis scripts and methodologies are continuously updated. Please check the git history and documentation for the most recent changes.
