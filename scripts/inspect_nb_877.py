import json

nb_path = "top_solutions/narrowed-877q-dqi-and-progressive-r10-chemistry.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
for i, cell in enumerate(nb['cells']):
    ctype = cell.get('cell_type')
    src = "".join(cell.get('source', []))
    print(f"\n--- CELL {i} ({ctype}) ---")
    print(src[:800])
