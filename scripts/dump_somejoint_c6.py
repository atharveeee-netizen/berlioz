import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("top_solutions/somejoint_quantum-circuits-22-77-local-gm-889-qubit-dqi_clean.ipynb", "r", encoding="utf-8", errors="ignore") as f:
    nb = json.load(f)

print("CELL 6:")
c6 = "".join(nb['cells'][6]['source'])
print(c6[:3000])
print("\n... length:", len(c6))
