import csv
import glob

csv_files = glob.glob('build/leaderboard/*.csv')
rows = list(csv.DictReader(open(csv_files[0], encoding='utf-8')))

print("=== LEADERBOARD TOP 150 BREAKDOWN ===")
tiers = [
    (1, 10),
    (11, 25),
    (26, 50),
    (51, 100),
    (101, 169)
]

for start, end in tiers:
    print(f"\n--- RANKS {start} TO {end} ---")
    for i in [start, (start + end) // 2, end]:
        if i <= len(rows):
            r = rows[i - 1]
            score = r.get('Score', '')
            name = r.get('TeamName', '').encode('ascii', 'replace').decode('ascii')
            print(f"  #{i:3d}: {score} | {name}")
