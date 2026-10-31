import csv
import json
import math
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Read full leaderboard
csv_path = 'leaderboard_export/google-verifiable-quantum-circuit-compilation-publicleaderboard-2026-10-31T06_27_40.csv'
with open(csv_path, mode='r', encoding='utf-8', errors='replace') as f:
    rows = list(csv.DictReader(f))

# Write cleaned top 50 CSV
top50_path = 'leaderboard_export/top50_leaderboard_clean.csv'
with open(top50_path, mode='w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Rank', 'TeamName', 'Score', 'Submissions', 'LastSubmissionDate', 'Members', 'ProductRatio'])
    for i, r in enumerate(rows[:50], 1):
        sc = float(r.get('Score', 0))
        prod = sc ** 3
        writer.writerow([
            i,
            r.get('TeamName', ''),
            f"{sc:.5f}",
            r.get('SubmissionCount', ''),
            r.get('LastSubmissionDate', ''),
            r.get('TeamMemberUserNames', ''),
            f"{prod:.1f}"
        ])

print(f"Wrote top 50 to {top50_path}")

# Find TuringIRL
for i, r in enumerate(rows, 1):
    if 'akshit' in r.get('TeamMemberUserNames', '').lower() or 'turing' in r.get('TeamName', '').lower():
        sc = float(r.get('Score', 0))
        print(f"Berlioz / TuringIRL: Rank {i} | Score: {sc:.5f} | Product: {sc**3:.1f}")

