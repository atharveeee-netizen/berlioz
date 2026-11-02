import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("top_solutions/23-57-lb-verified-three-task-portfolio.ipynb", "r", encoding="utf-8", errors="ignore") as f:
    nb = json.load(f)

for idx in [2, 6]:
    print(f"\n--- Cell {idx} ---")
    print("".join(nb['cells'][idx]['source']))
