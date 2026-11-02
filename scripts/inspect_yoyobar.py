import json

nb = json.load(open('build/harvest_yoyobar/lb-22-99-invsqrt-101-62-qubits.ipynb', encoding='utf-8'))
for i, c in enumerate(nb['cells']):
    src = ''.join(c.get('source', []))
    if any(k in src.lower() for k in ['qubit', 'invsqrt', '62', '63']):
        safe_src = src[:600].encode('ascii', 'replace').decode('ascii')
        print(f"=== CELL {i} ({c.get('cell_type')}) ===")
        print(safe_src)
        print("=" * 40)
