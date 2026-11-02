import json
import os
import re

nb_dir = "top_solutions"
interesting = [
    "narrowed-877q-dqi-and-progressive-r10-chemistry.ipynb",
    "quantum-circuits-881q-paired-dqi-r6-df-thc.ipynb",
    "quantum-circuits-thc-joint-norm-881q-dqi.ipynb",
    "atakanaldemir_qcc-888q-repair-and-native-chemistry-co-design.ipynb",
    "michaelrustad_vqcc-r10-merged-group-chemistry-12-87-lb.ipynb",
    "23-57-lb-verified-three-task-portfolio.ipynb",
]

for nb_name in interesting:
    p = os.path.join(nb_dir, nb_name)
    if not os.path.exists(p):
        print(f"MISSING: {nb_name}")
        continue
    print(f"\n{'='*60}\nFILE: {nb_name}\n{'='*60}")
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        nb = json.load(f)
    
    cells = nb.get("cells", [])
    print(f"Total cells: {len(cells)}")
    for i, cell in enumerate(cells):
        src = "".join(cell.get("source", []))
        # Look for titles, mentions of dqi, chem, brot, qubits, toffolis, scores, datasets
        matches = re.findall(r"(?:[0-9]{3}q|brot|toffoli|gm|score|kaggle/input|r10|r6|88[0-9]q|87[0-9]q)", src, re.IGNORECASE)
        lines = [line.strip() for line in src.split("\n") if line.strip()]
        headers = [line for line in lines if line.startswith("#")]
        if headers:
            print(f"Cell {i} [{cell.get('cell_type')}]: {headers[:3]}")
        
        # Check for dataset paths or specific code blocks
        for line in lines:
            if "kaggle/input" in line.lower() or "submission" in line.lower() or "brot" in line.lower():
                print(f"   Cell {i}: {line[:120]}")
