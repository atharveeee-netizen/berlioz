import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

nb_name = "top_solutions/narrowed-877q-dqi-and-progressive-r10-chemistry.ipynb"
with open(nb_name, "r", encoding="utf-8", errors="ignore") as f:
    nb = json.load(f)

for idx, cell in enumerate(nb.get("cells", [])):
    print(f"\n{'='*30} CELL {idx} ({cell.get('cell_type')}) {'='*30}")
    src = "".join(cell.get("source", []))
    print(src)
