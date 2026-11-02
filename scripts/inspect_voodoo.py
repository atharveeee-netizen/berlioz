import json

for path in ['build/harvest_mrmeows/21-0-circuits-let-s-all-reach-the-plateau.ipynb', 'build/harvest_voodoo/vqcc-quantum-voodoo.ipynb']:
    print(f"\n==================== {path} ====================")
    nb = json.load(open(path, encoding='utf-8'))
    for i, c in enumerate(nb['cells'][:8]):
        src = ''.join(c.get('source', []))[:500].encode('ascii', 'replace').decode('ascii')
        print(f"--- CELL {i} ({c.get('cell_type')}) ---")
        print(src)
