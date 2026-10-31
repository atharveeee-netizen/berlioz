import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('leaderboard_export/public_notebooks.json', 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f"Total notebooks: {len(nb)}")
print("\n--- NOTEBOOKS WITH TECHNIQUE / LB KEYWORDS ---")
key_notebooks = []
for n in nb:
    t = n['title'].lower()
    if any(k in t for k in ['lb', 'score', 'qubit', 'dqi', 'thc', 'qrom', 'invsqrt', 'gauge', 'plateau', 'gm', 'compilation', 'circuit']):
        key_notebooks.append(n)
        print(f"{n['votes']:3d} votes | {n['author']:<20} | {n['title']:<60} | {n['url']}")

print(f"\nFound {len(key_notebooks)} relevant technique notebooks.")
