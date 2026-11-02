import json

nb = json.load(open("top_solutions/23-57-lb-verified-three-task-portfolio.ipynb", encoding="utf-8"))
for idx in [9, 16]:
    print(f"=== CELL {idx} ===")
    src = "".join(nb['cells'][idx].get('source', []))
    print(src.encode('ascii', errors='replace').decode('ascii'))
    print()

