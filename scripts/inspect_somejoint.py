import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("top_solutions/somejoint_quantum-circuits-22-77-local-gm-889-qubit-dqi_clean.ipynb", "r", encoding="utf-8", errors="ignore") as f:
    nb = json.load(f)

print(f"Total cells: {len(nb.get('cells', []))}")
for idx, cell in enumerate(nb.get('cells', [])):
    src = "".join(cell.get('source', []))
    lines = [l.strip() for l in src.split("\n") if l.strip()]
    first_line = lines[0] if lines else ""
    if cell.get('cell_type') == 'markdown':
        print(f"[{idx}] MD: {first_line[:80]}")
    else:
        if any(w in src for w in ['dqi.kmb', 'build', 'decoder', 'quotient', '889', '892', '883']):
            print(f"[{idx}] CODE: {first_line[:80]}")
