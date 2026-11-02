import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

for nb_name in ["top_solutions/quantum-circuits-881q-paired-dqi-r6-df-thc.ipynb", "top_solutions/narrowed-877q-dqi-and-progressive-r10-chemistry.ipynb"]:
    print(f"\n==================== {nb_name} ====================")
    with open(nb_name, "r", encoding="utf-8", errors="ignore") as f:
        nb = json.load(f)
    cells = nb.get("cells", [])
    for idx, c in enumerate(cells):
        src = "".join(c.get("source", []))
        lines = [l.strip() for l in src.split("\n") if l.strip()]
        if not lines:
            continue
        first_line = lines[0]
        if first_line.startswith("#") or "881" in src or "877" in src or "dqi" in first_line.lower() or "chemistry" in first_line.lower():
            print(f"[{idx}] {c.get('cell_type')}: {first_line[:90]}")
            # If markdown, show more
            if c.get('cell_type') == 'markdown':
                for l in lines[1:8]:
                    print(f"     {l[:90]}")
