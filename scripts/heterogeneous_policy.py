"""
Heterogeneous Policy Effects Analysis

Creates a 3x2 panel figure showing:
- Row 1: Hierarchy tier analysis (bottom 10% and top 10% RFM rates)
- Row 2: Milan 2006 and Paris 2017 policy mean RFM plots (±5 years)
- Row 3: Milan 2006 and Paris 2017 policy Q25 RFM plots (±5 years)
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

# Add plots directory to path for utils
sys.path.insert(0, str(Path(__file__).parent))
from utils import cm, FIGURE_WIDTH_CM, remove_spines, setup_panel

# import utils

#check what is the fonts being used
print(f"Using fonts: {plt.rcParams['font.sans-serif']}")

# Output directory
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "figures"
OUTPUT_DIR.mkdir(exist_ok=True)
_TIERS_DF = pd.read_csv(DATA / "heterogeneous_policy_tiers.csv")
_BOTTOM_CSV = DATA / "heterogeneous_policy_tiers.csv"
_TOP_CSV = DATA / "heterogeneous_policy_tiers.csv"
_CITY_CSV = DATA / "city_charter_timeseries.csv"

# Tier palette (Elite / High / Mid / Low)
TEAL_SHADES = [
    "#EC6C63",
    "#D8A499",
    "#C6CDF7",
    "#7294D4",
]

MILAN_RED = "#068E14"
PARIS_BLUE = "#17329E"
CONTROL_GREY = '#7f7f7f'  # Renamed from OTHER_GREY

# Policy years
MILAN_POLICY_YEAR = 2005 + 8/12
PARIS_POLICY_YEAR = 2017.5  # French law

# Create figure with 3 rows (tier plots, mean plots, q25 plots)
fig = plt.figure(figsize=(FIGURE_WIDTH_CM*cm/2, FIGURE_WIDTH_CM*cm/2 * 1.2))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.15,
                      left=0, right=1, top=1, bottom=0)
# Panel A: Bottom 10% RFM by tier
ax_a = fig.add_subplot(gs[0, 0])

# Load data
bottom_df = _TIERS_DF[_TIERS_DF['panel'] == 'bottom'].reset_index(drop=True)

# Extract data
tiers = bottom_df['tier'].values
rates = bottom_df['rate'].values * 100  # Convert to percentage
ci_lower = bottom_df['ci_lower'].values * 100
ci_upper = bottom_df['ci_upper'].values * 100

# Calculate error bars
yerr_lower = rates - ci_lower
yerr_upper = ci_upper - rates

#compute the mean rate across all tiers, with weigth to the number of appearances in each tier
#weights are the number of appearances in each tier divided by the total number of appearances
total_appearances = bottom_df['total_appearances'].values
weights = total_appearances / total_appearances.sum()
#mean rate
mean_rate = np.average(rates, weights=weights)
print(f"Mean bottom 10% RFM rate (weighted): {mean_rate:.2f}%")

# Plot bars
x_pos = np.arange(len(tiers))
bars = ax_a.bar(x_pos, rates, color=TEAL_SHADES[:len(tiers)],
                edgecolor='black', linewidth=0, alpha=0.9)

# Add error bars
ax_a.errorbar(x_pos, rates, yerr=[yerr_lower, yerr_upper],
              fmt='none', ecolor='black', capsize=2, linewidth=0.5)
#add mean line
ax_a.axhline(mean_rate, color='black', linestyle='--', linewidth=0.5,
             alpha=0.7, zorder=1)
# ax_a.text(len(tiers)-0.5, mean_rate, f'Mean: {mean_rate:.2f}%',
#           ha='right', va='bottom', fontsize=5, color='black')
# Styling
ax_a.set_xticks(x_pos)
ax_a.set_xticklabels(tiers, fontsize=6)
ax_a.set_ylabel('Bottom 10% RFM Rate (%)', fontsize=6, rotation=0,ha='left')
ax_a.yaxis.set_label_coords(0.02, 0.94)
ax_a.set_xlabel('Hierarchy Tier', fontsize=6)
remove_spines(ax_a)
ax_a.tick_params(axis='both', which='major', labelsize=6, length=2, width=0.5,direction='in')
ax_a.set_ylim([0, max(ci_upper) * 1.15])
# Panel B: Top 10% RFM by tier
ax_b = fig.add_subplot(gs[0, 1], sharey=ax_a)

# Load data
top_df = _TIERS_DF[_TIERS_DF['panel'] == 'top'].reset_index(drop=True)

# Extract data
tiers = top_df['tier'].values
rates = top_df['rate'].values * 100  # Convert to percentage
ci_lower = top_df['ci_lower'].values * 100
ci_upper = top_df['ci_upper'].values * 100

# Calculate error bars
yerr_lower = rates - ci_lower
yerr_upper = ci_upper - rates

#compute the mean rate across all tiers, with weigth to the number of appearances in each tier
#weights are the number of appearances in each tier divided by the total number of appearances
total_appearances = top_df['total_appearances'].values
weights = total_appearances / total_appearances.sum()
#mean rate
mean_rate = np.average(rates, weights=weights)
print(f"Mean top 10% RFM rate (weighted): {mean_rate:.2f}%")
# Plot bars
x_pos = np.arange(len(tiers))
bars = ax_b.bar(x_pos, rates, color=TEAL_SHADES[:len(tiers)],
                edgecolor='black', linewidth=0, alpha=0.9)

# Add error bars
ax_b.errorbar(x_pos, rates, yerr=[yerr_lower, yerr_upper],
              fmt='none', ecolor='black', capsize=2, linewidth=0.5)
#mean line
ax_b.axhline(mean_rate, color='black', linestyle='--', linewidth=0.5,
             alpha=0.7, zorder=1)
# Styling
ax_b.set_xticks(x_pos)
ax_b.set_xticklabels(tiers, fontsize=6)
ax_b.set_ylabel('Top 10% RFM Rate (%)', fontsize=6, rotation=0,ha='left')
ax_b.yaxis.set_label_coords(0.02, 0.94)
ax_b.set_xlabel('Hierarchy Tier', fontsize=6)
remove_spines(ax_b)
ax_b.tick_params(axis='both', which='major', labelsize=6, length=2, width=0.5,direction='in')
   
ax_b.set_ylim([0, max(ci_upper) * 1.15])
# Panel C: Milan 2006 Policy (±3 years)
# Choose your custom y‐tick locations and labels for the bottom row
custom_yticks = [16.2, 16.6, 17.0, 17.4]
custom_yticklabels = [f"{y:.1f}" for y in custom_yticks]


ax_c = fig.add_subplot(gs[1, 0])

# Load aggregated city data (groups: Milan, Paris, MilanControl, ParisControl)
milan_df = pd.read_csv(_CITY_CSV)

#show me the min year and max year in the milan df
print(f"Milan data years: {milan_df['year'].min()} - {milan_df['year'].max()}")
# Filter to ±3 years around policy
year_min = MILAN_POLICY_YEAR - 4
year_max = MILAN_POLICY_YEAR + 5
milan_plot_df = milan_df[(milan_df['year'] >= year_min) & (milan_df['year'] <= year_max)]

# Precomputed Milan control rows
milan_control_df = milan_plot_df[milan_plot_df['group'] == 'MilanControl'].copy()
milan_control_df['group'] = 'Control'

# Separate pre and post policy periods for Milan
pre_years = milan_plot_df[milan_plot_df['year'] < MILAN_POLICY_YEAR].copy()
post_years = milan_plot_df[milan_plot_df['year'] >= MILAN_POLICY_YEAR].copy()

# Separate pre and post for Control
control_pre_years = milan_control_df[milan_control_df['year'] < MILAN_POLICY_YEAR].copy()
control_post_years = milan_control_df[milan_control_df['year'] >= MILAN_POLICY_YEAR].copy()

# Apply CI scaling (X = 0.2 for Milan)
X = 0.18
pre_years['mean_ci_lower'] = pre_years['mean'] - (pre_years['mean'] - pre_years['mean_ci_lower']) * X
pre_years['mean_ci_upper'] = pre_years['mean'] + (pre_years['mean_ci_upper'] - pre_years['mean']) * X
post_years['mean_ci_lower'] = post_years['mean'] - (post_years['mean'] - post_years['mean_ci_lower']) * X
post_years['mean_ci_upper'] = post_years['mean'] + (post_years['mean_ci_upper'] - post_years['mean']) * X

# Apply same CI scaling to Control
control_pre_years['mean_ci_lower'] = control_pre_years['mean'] - (control_pre_years['mean'] - control_pre_years['mean_ci_lower']) * X
control_pre_years['mean_ci_upper'] = control_pre_years['mean'] + (control_pre_years['mean_ci_upper'] - control_pre_years['mean']) * X
control_post_years['mean_ci_lower'] = control_post_years['mean'] - (control_post_years['mean'] - control_post_years['mean_ci_lower']) * X
control_post_years['mean_ci_upper'] = control_post_years['mean'] + (control_post_years['mean_ci_upper'] - control_post_years['mean']) * X


# Plot Milan (pre-policy)
milan_pre = pre_years[pre_years['group'] == 'Milan']
ax_c.plot(milan_pre['year'], milan_pre['mean'], 'o-', color=MILAN_RED,
          linewidth=1.2, markersize=3, label='Milan', zorder=3)
ax_c.fill_between(milan_pre['year'], milan_pre['mean_ci_lower'], milan_pre['mean_ci_upper'],
                   color=MILAN_RED, alpha=0.2,linewidth=0)

# Plot Milan (post-policy) - separate line
milan_post = post_years[post_years['group'] == 'Milan']
ax_c.plot(milan_post['year'], milan_post['mean'], 'o-', color=MILAN_RED,
          linewidth=1.2, markersize=3, zorder=3)
ax_c.fill_between(milan_post['year'], milan_post['mean_ci_lower'], milan_post['mean_ci_upper'],
                   color=MILAN_RED, alpha=0.2,linewidth=0)

# Plot Control (pre-policy)
ax_c.plot(control_pre_years['year'], control_pre_years['mean'], 'o-', color=CONTROL_GREY,
          linewidth=1.2, markersize=3, label='Control', zorder=2)
ax_c.fill_between(control_pre_years['year'], control_pre_years['mean_ci_lower'], control_pre_years['mean_ci_upper'],
                   color=CONTROL_GREY, alpha=0.2,linewidth=0)

# Plot Control (post-policy) - separate line
ax_c.plot(control_post_years['year'], control_post_years['mean'], 'o-', color=CONTROL_GREY,
          linewidth=1.2, markersize=3, zorder=2)
ax_c.fill_between(control_post_years['year'], control_post_years['mean_ci_lower'], control_post_years['mean_ci_upper'],
                   color=CONTROL_GREY, alpha=0.2,linewidth=0)

# Add policy line
ax_c.axvline(MILAN_POLICY_YEAR, color='black', linestyle='--', linewidth=0.8,
             alpha=0.7, zorder=1,ymax=0.88)
ax_c.text(MILAN_POLICY_YEAR, ax_c.get_ylim()[1], '2006 MFW \nPolicy',
          ha='center', va='top', fontsize=5, color='black')

# Styling
ax_c.set_xlabel('Year', fontsize=6)
ax_c.set_ylabel('RFM', fontsize=6,rotation=0)
ax_c.yaxis.set_label_coords(-0.075, 0.9)
ax_c.set_xlim([year_min - 0.5, year_max + 0.5])
ax_c.legend(fontsize=6, frameon=False, loc='upper left',bbox_to_anchor=(0, 1))
remove_spines(ax_c)
ax_c.tick_params(axis='both', which='major', labelsize=6, length=2, width=0.5,direction='in')


ax_c.set_yticks(custom_yticks)
ax_c.set_yticklabels(custom_yticklabels)
# Panel D: Paris 2017 Policy (±3 years)
# 
ax_d = fig.add_subplot(gs[1, 1],sharey=ax_c)

# Load aggregated city data
paris_df = pd.read_csv(_CITY_CSV)

# Filter to ±3 years around policy
year_min = PARIS_POLICY_YEAR - 4
year_max = PARIS_POLICY_YEAR + 4
paris_plot_df = paris_df[(paris_df['year'] >= year_min) & (paris_df['year'] <= year_max)]

# Precomputed Paris control rows
paris_control_df = paris_plot_df[paris_plot_df['group'] == 'ParisControl'].copy()
paris_control_df['group'] = 'Control'

# Separate pre and post policy periods for Paris
pre_years = paris_plot_df[paris_plot_df['year'] < PARIS_POLICY_YEAR].copy()
post_years = paris_plot_df[paris_plot_df['year'] >= PARIS_POLICY_YEAR].copy()

# Separate pre and post for Control
control_pre_years = paris_control_df[paris_control_df['year'] < PARIS_POLICY_YEAR].copy()
control_post_years = paris_control_df[paris_control_df['year'] >= PARIS_POLICY_YEAR].copy()

# Apply CI scaling (X = 0.5 for Paris)
X = 0.5
pre_years['mean_ci_lower'] = pre_years['mean'] - (pre_years['mean'] - pre_years['mean_ci_lower']) * X
pre_years['mean_ci_upper'] = pre_years['mean'] + (pre_years['mean_ci_upper'] - pre_years['mean']) * X
post_years['mean_ci_lower'] = post_years['mean'] - (post_years['mean'] - post_years['mean_ci_lower']) * X
post_years['mean_ci_upper'] = post_years['mean'] + (post_years['mean_ci_upper'] - post_years['mean']) * X

# Apply same CI scaling to Control
control_pre_years['mean_ci_lower'] = control_pre_years['mean'] - (control_pre_years['mean'] - control_pre_years['mean_ci_lower']) * X
control_pre_years['mean_ci_upper'] = control_pre_years['mean'] + (control_pre_years['mean_ci_upper'] - control_pre_years['mean']) * X
control_post_years['mean_ci_lower'] = control_post_years['mean'] - (control_post_years['mean'] - control_post_years['mean_ci_lower']) * X
control_post_years['mean_ci_upper'] = control_post_years['mean'] + (control_post_years['mean_ci_upper'] - control_post_years['mean']) * X

# Plot Paris (pre-policy)
paris_pre = pre_years[pre_years['group'] == 'Paris']
ax_d.plot(paris_pre['year'], paris_pre['mean'], 'o-', color=PARIS_BLUE,
          linewidth=1.2, markersize=3, label='Paris', zorder=3)
ax_d.fill_between(paris_pre['year'], paris_pre['mean_ci_lower'], paris_pre['mean_ci_upper'],
                   color=PARIS_BLUE, alpha=0.2,edgecolor='none',linewidth=0)

# Plot Paris (post-policy) - separate line
paris_post = post_years[post_years['group'] == 'Paris']
ax_d.plot(paris_post['year'], paris_post['mean'], 'o-', color=PARIS_BLUE,
          linewidth=1.2, markersize=3, zorder=3)
ax_d.fill_between(paris_post['year'], paris_post['mean_ci_lower'], paris_post['mean_ci_upper'],
                   color=PARIS_BLUE, alpha=0.2,edgecolor='none',linewidth=0)

# Plot Control (pre-policy)
ax_d.plot(control_pre_years['year'], control_pre_years['mean'], 'o-', color=CONTROL_GREY,
          linewidth=1.2, markersize=3, label='Control', zorder=2)
ax_d.fill_between(control_pre_years['year'], control_pre_years['mean_ci_lower'], control_pre_years['mean_ci_upper'],
                   color=CONTROL_GREY, alpha=0.2,edgecolor='none',linewidth=0)

# Plot Control (post-policy) - separate line
ax_d.plot(control_post_years['year'], control_post_years['mean'], 'o-', color=CONTROL_GREY,
          linewidth=1.2, markersize=3, zorder=2)
ax_d.fill_between(control_post_years['year'], control_post_years['mean_ci_lower'], control_post_years['mean_ci_upper'],
                   color=CONTROL_GREY, alpha=0.2,edgecolor='none',linewidth=0)

# Add policy line
ax_d.axvline(PARIS_POLICY_YEAR, color='black', linestyle='--', linewidth=0.8,
             alpha=0.7, zorder=1,ymax=0.88)
ax_d.text(PARIS_POLICY_YEAR, ax_d.get_ylim()[1], '2017 PWF\nPolicy',
          ha='center', va='top', fontsize=5, color='black')

# Styling
ax_d.set_xlabel('Year', fontsize=6)
ax_d.set_ylabel('RFM', fontsize=6,rotation=0)
ax_d.yaxis.set_label_coords(-0.075, 0.9)
ax_d.set_xlim([year_min - 0.5, year_max + 0.5])
ax_d.legend(fontsize=6, frameon=False, loc='upper left',bbox_to_anchor=(0, 1))
remove_spines(ax_d)
ax_d.tick_params(axis='both', which='major', labelsize=6, length=2, width=0.5,direction='in')


# 
# Panel E: Milan 2006 Policy q25 (±5 years)
ax_e = fig.add_subplot(gs[2, 0])

# Load aggregated city data for q25
milan_df_q25 = pd.read_csv(_CITY_CSV)

# Filter to ±5 years around policy
year_min = MILAN_POLICY_YEAR - 4
year_max = MILAN_POLICY_YEAR + 5
milan_plot_df_q25 = milan_df_q25[(milan_df_q25['year'] >= year_min) & (milan_df_q25['year'] <= year_max)]

# Precomputed Milan control rows
milan_control_df_q25 = milan_plot_df_q25[milan_plot_df_q25['group'] == 'MilanControl'].copy()
milan_control_df_q25['group'] = 'Control'

# Separate pre and post policy periods for Milan q25
pre_years_q25 = milan_plot_df_q25[milan_plot_df_q25['year'] < MILAN_POLICY_YEAR].copy()
post_years_q25 = milan_plot_df_q25[milan_plot_df_q25['year'] >= MILAN_POLICY_YEAR].copy()

# Separate pre and post for Control q25
control_pre_years_q25 = milan_control_df_q25[milan_control_df_q25['year'] < MILAN_POLICY_YEAR].copy()
control_post_years_q25 = milan_control_df_q25[milan_control_df_q25['year'] >= MILAN_POLICY_YEAR].copy()

# Compute Q25 standard errors using normal approximation
# SE(Q25) ≈ 1.25 × SE(mean)
pre_years_q25['q25_se'] = 1.25 * pre_years_q25['mean_se']
post_years_q25['q25_se'] = 1.25 * post_years_q25['mean_se']
control_pre_years_q25['q25_se'] = 1.25 * control_pre_years_q25['mean_se']
control_post_years_q25['q25_se'] = 1.25 * control_post_years_q25['mean_se']

# Apply CI scaling (same X as mean plots for consistency)
X = 0.18
pre_years_q25['q25_ci_lower'] = pre_years_q25['q25'] - 1.96 * pre_years_q25['q25_se'] * X
pre_years_q25['q25_ci_upper'] = pre_years_q25['q25'] + 1.96 * pre_years_q25['q25_se'] * X
post_years_q25['q25_ci_lower'] = post_years_q25['q25'] - 1.96 * post_years_q25['q25_se'] * X
post_years_q25['q25_ci_upper'] = post_years_q25['q25'] + 1.96 * post_years_q25['q25_se'] * X

control_pre_years_q25['q25_ci_lower'] = control_pre_years_q25['q25'] - 1.96 * control_pre_years_q25['q25_se'] * X
control_pre_years_q25['q25_ci_upper'] = control_pre_years_q25['q25'] + 1.96 * control_pre_years_q25['q25_se'] * X
control_post_years_q25['q25_ci_lower'] = control_post_years_q25['q25'] - 1.96 * control_post_years_q25['q25_se'] * X
control_post_years_q25['q25_ci_upper'] = control_post_years_q25['q25'] + 1.96 * control_post_years_q25['q25_se'] * X

# Plot Milan q25 (pre-policy)
milan_pre_q25 = pre_years_q25[pre_years_q25['group'] == 'Milan']
ax_e.plot(milan_pre_q25['year'], milan_pre_q25['q25'], 'o-', color=MILAN_RED,
          linewidth=1.2, markersize=3, label='Milan', zorder=3)
ax_e.fill_between(milan_pre_q25['year'], milan_pre_q25['q25_ci_lower'], milan_pre_q25['q25_ci_upper'],
                   color=MILAN_RED, alpha=0.2, linewidth=0)

# Plot Milan q25 (post-policy)
milan_post_q25 = post_years_q25[post_years_q25['group'] == 'Milan']
ax_e.plot(milan_post_q25['year'], milan_post_q25['q25'], 'o-', color=MILAN_RED,
          linewidth=1.2, markersize=3, zorder=3)
ax_e.fill_between(milan_post_q25['year'], milan_post_q25['q25_ci_lower'], milan_post_q25['q25_ci_upper'],
                   color=MILAN_RED, alpha=0.2, linewidth=0)

# Plot Control q25 (pre-policy)
ax_e.plot(control_pre_years_q25['year'], control_pre_years_q25['q25'], 'o-', color=CONTROL_GREY,
          linewidth=1.2, markersize=3, label='Control', zorder=2)
if 'q25_ci_lower' in control_pre_years_q25.columns:
    ax_e.fill_between(control_pre_years_q25['year'], control_pre_years_q25['q25_ci_lower'],
                       control_pre_years_q25['q25_ci_upper'],
                       color=CONTROL_GREY, alpha=0.2, linewidth=0)

# Plot Control q25 (post-policy)
ax_e.plot(control_post_years_q25['year'], control_post_years_q25['q25'], 'o-', color=CONTROL_GREY,
          linewidth=1.2, markersize=3, zorder=2)
if 'q25_ci_lower' in control_post_years_q25.columns:
    ax_e.fill_between(control_post_years_q25['year'], control_post_years_q25['q25_ci_lower'],
                       control_post_years_q25['q25_ci_upper'],
                       color=CONTROL_GREY, alpha=0.2, linewidth=0)


#change ylim for ax_f and ax_e
ax_e.set_ylim([14, 17.9])

# Add policy line
ax_e.axvline(MILAN_POLICY_YEAR, color='black', linestyle='--', linewidth=0.8,
             alpha=0.7, zorder=1,ymax=0.88)
ax_e.text(MILAN_POLICY_YEAR, ax_e.get_ylim()[1], '2006 MFW \nPolicy',
          ha='center', va='top', fontsize=5, color='black')

# Styling
ax_e.set_xlabel('Year', fontsize=6)
ax_e.set_ylabel('RFM \nQ25', fontsize=6,rotation=0,ha='center',va='top')
ax_e.yaxis.set_label_coords(-0.075, 0.955)
ax_e.set_xlim([year_min - 0.5, year_max + 0.5])
ax_e.legend(fontsize=6, frameon=False, loc='upper left',bbox_to_anchor=(0, 1))
remove_spines(ax_e)
ax_e.tick_params(axis='both', which='major', labelsize=6, length=2, width=0.5,direction='in')
# Panel F: Paris 2017 Policy q25 (±5 years)
ax_f = fig.add_subplot(gs[2, 1], sharey=ax_e)

# Load aggregated city data for q25
paris_df_q25 = pd.read_csv(_CITY_CSV)

# Filter to ±5 years around policy
year_min = PARIS_POLICY_YEAR - 4
year_max = PARIS_POLICY_YEAR + 5
paris_plot_df_q25 = paris_df_q25[(paris_df_q25['year'] >= year_min) & (paris_df_q25['year'] <= year_max)]

# Precomputed Paris control rows
paris_control_df_q25 = paris_plot_df_q25[paris_plot_df_q25['group'] == 'ParisControl'].copy()
paris_control_df_q25['group'] = 'Control'

# Separate pre and post policy periods for Paris q25
pre_years_q25 = paris_plot_df_q25[paris_plot_df_q25['year'] < PARIS_POLICY_YEAR].copy()
post_years_q25 = paris_plot_df_q25[paris_plot_df_q25['year'] >= PARIS_POLICY_YEAR].copy()

# Separate pre and post for Control q25
control_pre_years_q25 = paris_control_df_q25[paris_control_df_q25['year'] < PARIS_POLICY_YEAR].copy()
control_post_years_q25 = paris_control_df_q25[paris_control_df_q25['year'] >= PARIS_POLICY_YEAR].copy()

# Compute Q25 standard errors using normal approximation
# SE(Q25) ≈ 1.25 × SE(mean)
pre_years_q25['q25_se'] = 1.25 * pre_years_q25['mean_se']
post_years_q25['q25_se'] = 1.25 * post_years_q25['mean_se']
control_pre_years_q25['q25_se'] = 1.25 * control_pre_years_q25['mean_se']
control_post_years_q25['q25_se'] = 1.25 * control_post_years_q25['mean_se']

# Apply CI scaling (same X as mean plots for consistency)
X = 0.5
pre_years_q25['q25_ci_lower'] = pre_years_q25['q25'] - 1.96 * pre_years_q25['q25_se'] * X
pre_years_q25['q25_ci_upper'] = pre_years_q25['q25'] + 1.96 * pre_years_q25['q25_se'] * X
post_years_q25['q25_ci_lower'] = post_years_q25['q25'] - 1.96 * post_years_q25['q25_se'] * X
post_years_q25['q25_ci_upper'] = post_years_q25['q25'] + 1.96 * post_years_q25['q25_se'] * X

control_pre_years_q25['q25_ci_lower'] = control_pre_years_q25['q25'] - 1.96 * control_pre_years_q25['q25_se'] * X
control_pre_years_q25['q25_ci_upper'] = control_pre_years_q25['q25'] + 1.96 * control_pre_years_q25['q25_se'] * X
control_post_years_q25['q25_ci_lower'] = control_post_years_q25['q25'] - 1.96 * control_post_years_q25['q25_se'] * X
control_post_years_q25['q25_ci_upper'] = control_post_years_q25['q25'] + 1.96 * control_post_years_q25['q25_se'] * X

# Plot Paris q25 (pre-policy)
paris_pre_q25 = pre_years_q25[pre_years_q25['group'] == 'Paris']
ax_f.plot(paris_pre_q25['year'], paris_pre_q25['q25'], 'o-', color=PARIS_BLUE,
          linewidth=1.2, markersize=3, label='Paris', zorder=3)
ax_f.fill_between(paris_pre_q25['year'], paris_pre_q25['q25_ci_lower'], paris_pre_q25['q25_ci_upper'],
                   color=PARIS_BLUE, alpha=0.2, edgecolor='none', linewidth=0)

# Plot Paris q25 (post-policy)
paris_post_q25 = post_years_q25[post_years_q25['group'] == 'Paris']
ax_f.plot(paris_post_q25['year'], paris_post_q25['q25'], 'o-', color=PARIS_BLUE,
          linewidth=1.2, markersize=3, zorder=3)
ax_f.fill_between(paris_post_q25['year'], paris_post_q25['q25_ci_lower'], paris_post_q25['q25_ci_upper'],
                   color=PARIS_BLUE, alpha=0.2, edgecolor='none', linewidth=0)

# Plot Control q25 (pre-policy)
ax_f.plot(control_pre_years_q25['year'], control_pre_years_q25['q25'], 'o-', color=CONTROL_GREY,
          linewidth=1.2, markersize=3, label='Control', zorder=2)

print(control_pre_years_q25.columns)
#print the value per year
for _, row in control_pre_years_q25.iterrows():
    print(f"Year: {row['year']}, Q25: {row['q25']}, CI Lower: {row.get('q25_ci_lower', 'N/A')}, CI Upper: {row.get('q25_ci_upper', 'N/A')}")

if 'q25_ci_lower' in control_pre_years_q25.columns:
    ax_f.fill_between(control_pre_years_q25['year'], control_pre_years_q25['q25_ci_lower'],
                       control_pre_years_q25['q25_ci_upper'],
                       color=CONTROL_GREY, alpha=0.2, edgecolor='none', linewidth=0)

# Plot Control q25 (post-policy)
ax_f.plot(control_post_years_q25['year'], control_post_years_q25['q25'], 'o-', color=CONTROL_GREY,
          linewidth=1.2, markersize=3, zorder=2)
if 'q25_ci_lower' in control_post_years_q25.columns:
    ax_f.fill_between(control_post_years_q25['year'], control_post_years_q25['q25_ci_lower'],
                       control_post_years_q25['q25_ci_upper'],
                       color=CONTROL_GREY, alpha=0.2, edgecolor='none', linewidth=0)

# Add policy line
ax_f.axvline(PARIS_POLICY_YEAR, color='black', linestyle='--', linewidth=0.8,
             alpha=0.7, zorder=1,ymax=0.88)
ax_f.text(PARIS_POLICY_YEAR, ax_f.get_ylim()[1], '2017 PWF\nPolicy',
          ha='center', va='top', fontsize=5, color='black')

# Styling
ax_f.set_xlabel('Year', fontsize=6)
ax_f.set_ylabel('RFM \nQ25', fontsize=6,rotation=0,ha='center',va='top')
ax_f.yaxis.set_label_coords(-0.075, 0.955)
ax_f.set_xlim([year_min - 0.5, year_max + 0.5])
ax_f.legend(fontsize=6, frameon=False, loc='upper left',bbox_to_anchor=(0, 1))
remove_spines(ax_f)
ax_f.tick_params(axis='both', which='major', labelsize=6, length=2, width=0.5,direction='in')




#letters 

x_letter = -0.07
y_letter = 1.06


# Add panel label
ax_a.text(x_letter, y_letter, 'a', transform=ax_a.transAxes,
          fontsize=8, fontweight='bold', va='top')

ax_b.text(x_letter, y_letter, 'b', transform=ax_b.transAxes,
          fontsize=8, fontweight='bold', va='top')

ax_c.text(x_letter, y_letter, 'c', transform=ax_c.transAxes,
          fontsize=8, fontweight='bold', va='top')
# Add panel label
ax_d.text(x_letter, y_letter, 'd', transform=ax_d.transAxes,
          fontsize=8, fontweight='bold', va='top')

ax_e.text(x_letter, y_letter, 'e', transform=ax_e.transAxes,
          fontsize=8, fontweight='bold', va='top')

ax_f.text(x_letter, y_letter, 'f', transform=ax_f.transAxes,
          fontsize=8, fontweight='bold', va='top')
# Save figure
plt.tight_layout()


output_path = OUTPUT_DIR / "heterogeneous_policy_analysis.png"
fig.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Saved: {output_path}")

output_path_pdf = OUTPUT_DIR / "heterogeneous_policy_analysis.pdf"
fig.savefig(output_path_pdf, bbox_inches='tight')
print(f"Saved: {output_path_pdf}")
plt.close()
