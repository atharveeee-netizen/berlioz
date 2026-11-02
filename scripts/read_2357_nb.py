import json
from pathlib import Path

p = Path("top_solutions/23-57-lb-verified-three-task-portfolio.ipynb")
nb = json.loads(p.read_text(encoding='utf-8', errors='ignore'))
for i, cell in enumerate(nb.get('cells', [])):
    if cell.get('cell_type') == 'markdown':
        src = "".join(cell.get('source', []))
        if any(w in src.lower() for w in ['dqi', 'somejoint', 'schur', 'syndrome', 'decoder']):
            print(f"--- Cell {i} ---")
            print(src[:600].encode('ascii', errors='ignore').decode('ascii'))
            print()
