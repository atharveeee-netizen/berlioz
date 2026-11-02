import json
from pathlib import Path

p = Path("top_solutions/highest-public-score-direct-polynomial-phasing.ipynb")
nb = json.loads(p.read_text(encoding='utf-8'))
for i, cell in enumerate(nb.get('cells', [])):
    if cell.get('cell_type') == 'markdown':
        src = "".join(cell.get('source', []))
        print(f"--- Cell {i} ---")
        print(src[:500])
        print()
