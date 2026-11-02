import json
from pathlib import Path

p = Path("top_solutions/23-57-lb-verified-three-task-portfolio.ipynb")
nb = json.loads(p.read_text(encoding="utf-8"))

print(f"Total cells: {len(nb['cells'])}")
for i, c in enumerate(nb['cells']):
    src = "".join(c.get('source', []))
    if any(k in src.lower() for k in ['dqi', 'decoder', 'schur', '881', '877', '889', 'unsynthesis']):
        first_line = src.splitlines()[0] if src.splitlines() else ""
        print(f"Cell {i:2d} ({c.get('cell_type')}): {first_line[:80]}")

