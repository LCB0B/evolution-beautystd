"""Convenience wrapper: re-runs outliers_comparison.py with OC_GENDER=male.

The female script (outliers_comparison.py) automatically regenerates the male
variant after the female one. This file exists so that someone running
``python outliers_comparison_male.py`` directly gets the male figure without
also re-rendering the female one.
"""
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
env = {**os.environ, "OC_GENDER": "male"}
subprocess.run([sys.executable, str(HERE / "outliers_comparison.py")],
                env=env, check=True)
