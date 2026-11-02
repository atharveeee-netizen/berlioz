import json
import sys

def inspect_notebook(nb_path):
    with open(nb_path, "r", encoding="utf-8", errors="ignore") as f:
        nb = json.load(f)
    print(f"=== {nb_path} ===")
    for idx, cell in enumerate(nb.get("cells", [])):
        src = "".join(cell.get("source", []))
        cell_type = cell.get("cell_type")
        lines = [l.strip() for l in src.split("\n") if l.strip()]
        first_line = lines[0] if lines else ""
        print(f"[{idx}] {cell_type}: {first_line[:80]}")

if __name__ == "__main__":
    inspect_notebook("top_solutions/23-57-lb-verified-three-task-portfolio.ipynb")
