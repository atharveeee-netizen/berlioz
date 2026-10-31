import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('leaderboard_export/public_notebooks.json', 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f"Total notebooks: {len(nb)}")
print("\n=== TOP 40 PUBLIC NOTEBOOKS BY VOTES ===")
for i, n in enumerate(nb[:40], 1):
    print(f"{i:2d}. [{n['votes']:3d} votes] {n['author']:<25} | {n['title']:<60} | {n['url']}")
