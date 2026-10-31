import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def extract_section(nb_path, search_terms):
    print(f"\n--- Checking {nb_path} for {search_terms} ---")
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    for i, cell in enumerate(nb.get('cells', [])):
        src = "".join(cell.get('source', []))
        if any(term.lower() in src.lower() for term in search_terms):
            print(f"Cell {i} ({cell.get('cell_type')}):")
            # print up to 15 lines of snippet
            lines = src.split('\n')
            for l in lines[:15]:
                print(f"  {l}")
            if len(lines) > 15:
                print(f"  ... [{len(lines)-15} more lines]")

extract_section('top_solutions/narrowed-877q-dqi-and-progressive-r10-chemistry.ipynb', ['877', 'qubits', 'narrowed'])
extract_section('top_solutions/bezout-schur-5-word-qrom.ipynb', ['5-word', 'qrom', 'schur'])
extract_section('top_solutions/quantum-circuits-881q-paired-dqi-r6-df-thc.ipynb', ['881', 'r6', 'joint norm'])
