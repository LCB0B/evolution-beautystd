"""Career-record evolution plots: by category, by gender, stacked area.

Reads:  ../data/career_records_by_year.csv  (year, category, gender, count)
Writes:
  ../figures/career_records_by_category_per_year.{png,pdf}
  ../figures/records_by_gender_per_year.{png,pdf}
  ../figures/career_records_stacked_area.png
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"; FIG.mkdir(exist_ok=True)

cm = 1 / 2.54
df = pd.read_csv(DATA / "career_records_by_year.csv")

# pivot by category (all genders combined)
yearly = df.groupby(["year", "category"])["count"].sum().reset_index()
pivot_cat = yearly.pivot(index="year", columns="category", values="count").fillna(0)
order = pivot_cat.sum().sort_values(ascending=False).index.tolist()


# --- 1. records by category per year (top 4) ---
plt.figure(figsize=(18 * cm, 10 * cm))
top4 = order[:4]
cat_colors = ["#07AB92", "#8E44AD", "#FF7DBE", "#61C2FF", "#F1C40F", "#FF9123"]
for i, cat in enumerate(top4):
    plt.plot(pivot_cat.index, pivot_cat[cat], marker="o", linewidth=1.5,
             markersize=4, label=cat, color=cat_colors[i % len(cat_colors)])
plt.xlabel("Year", fontsize=12); plt.ylabel("Number of Records", fontsize=12)
plt.legend(bbox_to_anchor=(0.04, 1), loc="upper left", fontsize=10)
plt.grid(True, alpha=0.3)
plt.gca().spines["top"].set_visible(False); plt.gca().spines["right"].set_visible(False)
for ext in ("png", "pdf"):
    plt.savefig(FIG / f"career_records_by_category_per_year.{ext}", dpi=300,
                bbox_inches="tight")
plt.close()

# --- 2. records by gender per year (female vs male+unknown collapsed) ---
gender = df[df["gender"].isin(["female", "male", "unknown"])]
gender_yearly = (gender.groupby(["year", "gender"])["count"].sum()
                 .reset_index()
                 .pivot(index="year", columns="gender", values="count")
                 .fillna(0))
# Collapse non-female into 'male' bucket
gender_yearly["male"] = gender_yearly.get("male", 0) + gender_yearly.get("unknown", 0)

plt.figure(figsize=(18 * cm, 10 * cm))
for gender_label, ls in [("female", "--"), ("male", "-.")]:
    if gender_label in gender_yearly.columns:
        plt.plot(gender_yearly.index, gender_yearly[gender_label], marker="o",
                 linewidth=1.5, markersize=4, label=gender_label, color="k",
                 linestyle=ls)
plt.xlabel("Year", fontsize=12); plt.ylabel("Number of Records", fontsize=12)
plt.legend(bbox_to_anchor=(0.04, 1), loc="upper left", fontsize=10)
plt.grid(True, alpha=0.3)
plt.gca().spines["top"].set_visible(False); plt.gca().spines["right"].set_visible(False)
for ext in ("png", "pdf"):
    plt.savefig(FIG / f"records_by_gender_per_year.{ext}", dpi=300, bbox_inches="tight")
plt.close()

# --- 3. stacked area ---
plt.figure(figsize=(15, 10))
stack_colors = ["#FF7DBE", "#61C2FF", "#8E44AD", "#FF9123", "#F1C40F", "#07AB92"]
cols = pivot_cat.columns.tolist()
plt.stackplot(pivot_cat.index, *[pivot_cat[c] for c in cols], labels=cols,
              colors=[stack_colors[i % len(stack_colors)] for i in range(len(cols))],
              alpha=0.8)
plt.title("Career Records Distribution Over Time (Stacked)", fontsize=16, fontweight="bold")
plt.xlabel("Year", fontsize=12); plt.ylabel("Number of Records", fontsize=12)
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.grid(True, alpha=0.3); plt.tight_layout()
plt.savefig(FIG / "career_records_stacked_area.png", dpi=300, bbox_inches="tight")
plt.close()

print("Saved 3 career-evolution figures")
