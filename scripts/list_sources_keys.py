import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("top_solutions/somejoint_quantum-circuits-22-77-local-gm-889-qubit-dqi_clean.ipynb", "r", encoding="utf-8", errors="ignore") as f:
    nb = json.load(f)

c6 = "".join(nb['cells'][6]['source'])

keys = re.findall(r"'([a-zA-Z0-9_\-/\.]+?\.py)'\s*:", c6)
print(f"Total .py keys in SOURCES: {len(keys)}")
for k in keys:
    print("  ", k)
