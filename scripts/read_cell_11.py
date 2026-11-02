import json

nb = json.load(open("top_solutions/23-57-lb-verified-three-task-portfolio.ipynb", encoding="utf-8"))
src = "".join(nb['cells'][11].get('source', []))
print(src.encode('ascii', errors='replace').decode('ascii'))

