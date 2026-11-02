import csv
import glob

import zipfile
import io

z = zipfile.ZipFile('build/leaderboard/google-verifiable-quantum-circuit-compilation.zip')
name = z.namelist()[0]
rows = list(csv.DictReader(io.TextIOWrapper(z.open(name), encoding='utf-8')))
print(f'Total teams on leaderboard: {len(rows)}')

print("=== TOP 40 ON LEADERBOARD ===")
for i, r in enumerate(rows[:40], 1):
    score = r.get('Score', '')
    name = r.get('TeamName', '').encode('ascii', 'replace').decode('ascii')
    tid = r.get('TeamId', '')
print("\n=== SCORE BANDS ABOVE OUR CURRENT SCORE (23.91003) ===")
curr_s = 28.0
for i, r in enumerate(rows, 1):
    s = float(r.get('Score', 0))
    if s < curr_s and s >= 23.91:
        name = r.get('TeamName', '').encode('ascii', 'replace').decode('ascii')
        print(f"Rank #{i:3d}: {s:.5f} | {name:30s}")
        curr_s = s - 0.05

