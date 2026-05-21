"""Shared plotting style: fonts, colours, figure sizes, small helpers."""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams, font_manager
from pathlib import Path

# Pick up any font files dropped in ~/font (Helvetica clone, etc.). Optional.
font_dir = Path.home() / "font"
if font_dir.exists():
    for font_path in list(font_dir.glob("*.ttf")) + list(font_dir.glob("*.otf")):
        font_manager.fontManager.addfont(str(font_path))

rcParams["font.family"] = "sans-serif"
rcParams["font.sans-serif"] = ["Helvetica"]

# Embed fonts as TrueType so PDF/PS text stays editable in Illustrator/Inkscape.
rcParams['pdf.fonttype'] = 42
rcParams['ps.fonttype'] = 42

rcParams['font.size'] = 6
rcParams['axes.linewidth'] = 0.5
rcParams['grid.linewidth'] = 0.5
rcParams['lines.linewidth'] = 1.0
rcParams['patch.linewidth'] = 0.5
rcParams['xtick.major.width'] = 0.5
rcParams['ytick.major.width'] = 0.5
rcParams['xtick.minor.width'] = 0.25
rcParams['ytick.minor.width'] = 0.25

# Per-event colour palette.
colors = ['#FF7DBE', "#61C2FF", '#8E44AD', "#FF9123", '#F1C40F', '#07AB92']

cm = 1 / 2.54  # inches per centimetre

# Figure dimensions
FIGURE_WIDTH_MM = 180
FIGURE_WIDTH_CM = FIGURE_WIDTH_MM / 10
FIGURE_HEIGHT_CM = FIGURE_WIDTH_CM * 0.75  # 4:3 aspect ratio for 2x2 panels

def remove_spines(ax, spines=['top', 'right']):
    """
    Remove specified spines from axes for cleaner appearance.
    
    Args:
        ax: matplotlib axes object
        spines: list of spine names to remove ('top', 'right', 'bottom', 'left')
    """
    for spine in spines:
        ax.spines[spine].set_visible(False)

def setup_panel(ax, title=None, xlabel=None, ylabel=None):
    """
    Set up a panel with consistent styling.
    
    Args:
        ax: matplotlib axes object
        title: panel title
        xlabel: x-axis label
        ylabel: y-axis label
    """
    remove_spines(ax)
    
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    
    ax.tick_params(axis='both', which='major', direction='in', length=3)
    ax.tick_params(axis='both', which='minor', direction='in', length=1.5)
    
    # Add subtle grid


def get_career_event_style(event_idx, event_name):
    """
    Get consistent styling for career events.
    
    Args:
        event_idx: index of the career event
        event_name: name of the career event
    
    Returns:
        dict: styling parameters
    """
    base_styles = {
        'color': colors[event_idx % len(colors)],
        'linewidth': 1.2,
        'marker': 'o',
        'markersize': 2,
        'alpha': 0.8
    }
    
    # Special styling for fashion shows (baseline)
    if 'fashion_shows' in event_name.lower() or event_name == 'fashion_shows':
        base_styles.update({
            'linewidth': 2.0,
            'alpha': 1.0,
            'linestyle': '-',
            'color': '#000000'  # Black for baseline
        })
    
    return base_styles

def format_measurement_name(measurement):
    """
    Convert measurement column names to display-friendly labels.
    
    Args:
        measurement: column name from CSV
    
    Returns:
        str: formatted display name
    """
    mapping = {
        'height_cm': 'Height (cm)',
        'bust-eu_clean': 'Bust (EU)',
        'waist-eu_clean': 'Waist (EU)',
        'hips-eu_clean': 'Hips (EU)',
        'bust-us_clean': 'Bust (US)',
        'waist-us_clean': 'Waist (US)',
        'hips-us_clean': 'Hips (US)'
    }
    return mapping.get(measurement, measurement.replace('_', ' ').title())

def format_career_event_name(event_name):
    """
    Convert career event names to display-friendly labels.
    
    Args:
        event_name: career event name from file
    
    Returns:
        str: formatted display name
    """
    mapping = {
        'advertisements': 'Advertisements',
        'magazine_covers': 'Magazine Covers',
        'editorials': 'Editorials',
        'catalogues': 'Catalogues',
        'lookbooks': 'Lookbooks',
        'fashion_shows': 'Fashion Shows'
    }
    return mapping.get(event_name, event_name.replace('_', ' ').title())

def save_figure(fig, filename, output_dir, formats=['png', 'pdf']):
    """
    Save figure in multiple formats with consistent settings.
    
    Args:
        fig: matplotlib figure object
        filename: base filename (without extension)
        output_dir: output directory path
        formats: list of formats to save
    """
    for fmt in formats:
        filepath = output_dir / f"{filename}.{fmt}"
        fig.savefig(
            filepath,
            format=fmt,
            dpi=300,
        )
        print(f"Saved: {filepath}")