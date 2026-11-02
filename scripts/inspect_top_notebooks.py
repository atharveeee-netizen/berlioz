import json
from pathlib import Path

notebooks = [
    "top_solutions/highest-public-score-direct-polynomial-phasing.ipynb",
    "top_solutions/narrowed-877q-dqi-and-progressive-r10-chemistry.ipynb",
    "top_solutions/quantum-circuits-881q-paired-dqi-r6-df-thc.ipynb",
    "top_solutions/quantum-circuits-thc-joint-norm-881q-dqi.ipynb",
    "top_solutions/23-57-lb-verified-three-task-portfolio.ipynb",
]

for nb_path in notebooks:
    p = Path(nb_path)
    if not p.exists():
        continue
    try:
        nb = json.loads(p.read_text(encoding='utf-8'))
        print(f"\n=================== {p.name} ===================")
        for i, cell in enumerate(nb.get('cells', [])):
            cell_type = cell.get('cell_type')
            source = "".join(cell.get('source', []))
            # print headers or search terms
            lines = [l.strip() for l in source.split('\n') if l.strip()]
            for line in lines:
                if line.startswith('#') or any(kw in line.lower() for kw in ['score', 'cost', 'qubit', 'toffoli', 'ratio', 'bm', 'lfsr']):
                    print(f"  [{cell_type}:{i}] {line[:100]}")
    except Exception as e:
        print(f"Error reading {nb_path}: {e}")
