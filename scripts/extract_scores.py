import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('leaderboard_export/public_notebooks.json', 'r', encoding='utf-8') as f:
    nb = json.load(f)

print("=== PUBLIC NOTEBOOKS CLAIMING LB / GM SCORES ===")
scored = []
for n in nb:
    # regex for score patterns like 2x.xx
    m = re.findall(r'(?:lb|gm|score)?\s*\[?(\d{2}\.\d{2,5})\]?', n['title'], re.I)
    if m:
        for val in m:
            v = float(val)
            if 15.0 <= v <= 35.0:  # reasonable competition score range
                scored.append((v, n))
                break

scored.sort(key=lambda x: x[0], reverse=True)
seen = set()
for sc, n in scored:
    if n['url'] not in seen:
        seen.add(n['url'])
        print(f"Claimed Score {sc:7.4f} | {n['votes']:3d} votes | {n['author']:<22} | {n['title']}")
        print(f"    URL: {n['url']}")
