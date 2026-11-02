import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def dump_cells(nb_path, cell_indices):
    with open(nb_path, "r", encoding="utf-8", errors="ignore") as f:
        nb = json.load(f)
    print(f"=== {nb_path} ===")
    cells = nb.get("cells", [])
    for idx in cell_indices:
        if 0 <= idx < len(cells):
            cell = cells[idx]
            print(f"\n--- Cell {idx} ({cell.get('cell_type')}) ---")
            print("".join(cell.get("source", [])))

if __name__ == "__main__":
    # Dump cells 0, 1, 2, 6, 7, 8, 9, 10, 11 of 23-57
    dump_cells("top_solutions/23-57-lb-verified-three-task-portfolio.ipynb", [0, 1, 6, 7, 8, 9, 10, 11])
