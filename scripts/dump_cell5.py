import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

nb_name = "top_solutions/narrowed-877q-dqi-and-progressive-r10-chemistry.ipynb"
with open(nb_name, "r", encoding="utf-8", errors="ignore") as f:
    nb = json.load(f)

print("CELL 5:")
print("".join(nb['cells'][5]['source']))
