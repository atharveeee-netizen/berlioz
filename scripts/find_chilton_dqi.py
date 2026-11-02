import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
nb_path = "top_solutions/23-57-lb-verified-three-task-portfolio.ipynb"
with open(nb_path, "r", encoding="utf-8", errors="ignore") as f:
    nb = json.load(f)

for i, cell in enumerate(nb['cells']):
    src = "".join(cell.get('source', []))
    if any(k in src.lower() for k in ['schur', 'jday', '883', 'alexchilton']):
        lines = [l.strip() for l in src.split('\n') if any(k in l.lower() for k in ['schur', 'jday', '883', 'alexchilton', 'dataset', 'input'])]
        print(f"Cell {i} ({cell['cell_type']}):")
        for l in lines[:5]:
            print(f"   {l}")
