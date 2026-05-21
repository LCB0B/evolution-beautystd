"""Top-30 brand hierarchy table (CSV + LaTeX). No figure image.

Reads:  ../data/hierarchy_top30.csv
Writes:
  ../figures/hierarchy_top30.csv
  ../figures/hierarchy_top30.tex
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"; FIG.mkdir(exist_ok=True)

table = pd.read_csv(DATA / "hierarchy_top30.csv")
formatted = table.copy()
formatted["Prestige"] = formatted["Prestige"].apply(lambda x: f"{x:,.0f}")
formatted["Records"] = formatted["Records"].apply(lambda x: f"{int(x):,}")
formatted["Models"] = formatted["Models"].apply(lambda x: f"{int(x):,}")
formatted["% Elite"] = formatted["% Elite"].apply(lambda x: f"{x:.1f}")
for col in ["Mean MP", "Median MP", "Std MP"]:
    formatted[col] = formatted[col].apply(lambda x: f"{x:,.0f}")
formatted.to_csv(FIG / "hierarchy_top30.csv", index=False)

latex = formatted.copy()
latex["Brand"] = latex["Brand"].str.replace("&", r"\&", regex=False)
header = (
    r"\begin{table}[htbp]" "\n"
    r"\centering" "\n"
    r"\caption{Top 30 brands and magazines by network prestige score. "
    r"Prestige is computed via iterative bipartite centrality across shows, "
    r"editorials, advertisements, and magazine covers. "
    r"\%~Elite reports the percentage of each brand's unique models whose career "
    r"records also include at least one appearance for another Elite-tier brand. "
    r"Model prestige (MP) columns report the mean, median, and standard deviation of "
    r"model-level prestige scores across each brand's unique models.}" "\n"
    r"\label{tab:hierarchy_top30}" "\n"
    r"\small" "\n"
    r"\begin{tabular}{rlrllrrrrrr}" "\n"
    r"\toprule" "\n"
    r" & & & & & & & \multicolumn{3}{c}{Model prestige} \\" "\n"
    r"\cmidrule(lr){8-10}" "\n"
    r"Rank & Brand & Prestige & Tier & Records & Models & \% Elite & Mean & Median & Std \\" "\n"
    r"\midrule"
)
rows = []
for _, r in latex.iterrows():
    rows.append(f"{r['Rank']} & {r['Brand']} & {r['Prestige']} & {r['Tier']} & "
                f"{r['Records']} & {r['Models']} & {r['% Elite']} & "
                f"{r['Mean MP']} & {r['Median MP']} & {r['Std MP']} \\\\")
footer = r"\bottomrule" "\n" r"\end{tabular}" "\n" r"\end{table}"
with open(FIG / "hierarchy_top30.tex", "w") as f:
    f.write(header + "\n" + "\n".join(rows) + "\n" + footer)
print("Saved hierarchy_top30.{csv,tex}")
