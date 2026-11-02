import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("top_solutions/23-57-lb-verified-three-task-portfolio.ipynb", "r", encoding="utf-8", errors="ignore") as f:
    nb = json.load(f)

cells = nb.get("cells", [])
for idx in [2, 5, 6, 18, 19, 20, 21, 22, 23, 24, 25]:
    if 0 <= idx < len(cells):
        cell = cells[idx]
        print(f"\n--- Cell {idx} ({cell.get('cell_type')}) ---")
        src = "".join(cell.get("source", []))
        print(src[:2000])
