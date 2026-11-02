import csv
import glob

csv_files = glob.glob('build/leaderboard/*.csv')
rows = list(csv.DictReader(open(csv_files[0], encoding='utf-8')))

print("=== TEAMS AROUND 23.91 ===")
for i, r in enumerate(rows, 1):
    try:
        s = float(r.get('Score', 0))
        if 23.90 <= s <= 23.93:
            name = r.get('TeamName', '').encode('ascii', 'replace').decode('ascii')
            print(f"#{i:3d}: {s:.5f} | {name} (id {r.get('TeamId')})")
    except:
        pass
