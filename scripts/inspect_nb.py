import json, sys

path = sys.argv[1]
with open(path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb.get('cells', [])
print(f"Total cells in {path}: {len(cells)}")
for i, c in enumerate(cells):
    src = "".join(c.get('source', []))
    lines = [line.strip() for line in src.splitlines() if line.strip()]
    first_line = lines[0] if lines else ""
    if any(k in src.lower() for k in ['score', 'public', 'leaderboard', 'toffoli', 'qubit', 'submission', 'invsqrt', 'chem', 'dqi']):
        print(f"--- Cell {i} ({c.get('cell_type')}) ---")
        print(f"  {first_line[:120]}")
        for l in lines[1:4]:
            print(f"    {l[:100]}")

