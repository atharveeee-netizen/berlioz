import json
from pathlib import Path

for nb_file in Path("top_solutions").glob("*.ipynb"):
    try:
        nb = json.loads(nb_file.read_text(encoding="utf-8"))
        for i, c in enumerate(nb.get("cells", [])):
            src = "".join(c.get("source", []))
            for k in ["newton", "recurrence", "lfsr", "top 10", "unsynthesis", "syzygy"]:
                if k in src.lower():
                    print(f"[{nb_file.name}] Cell {i} matched '{k}':")
                    lines = [line for line in src.splitlines() if k in line.lower()]
                    for l in lines[:3]:
                        print("   ", l.strip()[:100])
    except Exception as e:
        pass

