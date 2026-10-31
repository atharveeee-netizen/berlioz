import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def inspect_notebook(nb_path):
    print(f"\n==================================================")
    print(f"INSPECTING: {nb_path}")
    print(f"==================================================")
    try:
        with open(nb_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
    except Exception as e:
        print(f"Error opening {nb_path}: {e}")
        return

    code_cells = []
    markdown_text = []
    for cell in nb.get('cells', []):
        cell_type = cell.get('cell_type')
        source = "".join(cell.get('source', []))
        if cell_type == 'code':
            code_cells.append(source)
        elif cell_type == 'markdown':
            markdown_text.append(source)

    print(f"Markdown cells: {len(markdown_text)}, Code cells: {len(code_cells)}")
    
    # Search for key parameters: qubits, R, B, C, lambda, Toffoli, invsqrt, dqi, dfthc
    full_text = "\n".join(markdown_text + code_cells)
    
    # Check for specific strings
    keywords = ['877', '881', '888', '889', '42', '63', 'r10', 'r8', 'r6', '5-word', '4-word', 'bezout', 'schur', 'invsqrt', 'toffoli', 'lambda']
    print("Keyword mentions:")
    for kw in keywords:
        count = full_text.lower().count(kw)
        if count > 0:
            print(f"  - '{kw}': {count} occurrences")

    # Sample markdown summaries
    print("\nSample Markdown / Headings:")
    for m in markdown_text[:5]:
        for line in m.split('\n'):
            if line.startswith('#'):
                print(f"  {line}")

if __name__ == '__main__':
    notebooks = [
        'top_solutions/narrowed-877q-dqi-and-progressive-r10-chemistry.ipynb',
        'top_solutions/quantum-circuits-thc-joint-norm-881q-dqi.ipynb',
        'top_solutions/bezout-schur-5-word-qrom.ipynb',
        'top_solutions/quantum-circuits-exact-gauge-5-word-qrom.ipynb',
        'top_solutions/highest-public-score-direct-polynomial-phasing.ipynb',
        'top_solutions/quantum-circuits-881q-paired-dqi-r6-df-thc.ipynb'
    ]
    for nb in notebooks:
        inspect_notebook(nb)
