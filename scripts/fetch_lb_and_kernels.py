import csv
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

def parse_leaderboard():
    csv_path = 'leaderboard_export/google-verifiable-quantum-circuit-compilation-publicleaderboard-2026-10-31T06_27_40.csv'
    with open(csv_path, mode='r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Total teams on LB: {len(rows)}")

    print("\n=== TOP 25 LEADERBOARD ===")
    for i, r in enumerate(rows[:25], 1):
        team = r.get('TeamName', '')
        score = r.get('Score', '')
        date = r.get('LastSubmissionDate', '')
        team_id = r.get('TeamId', '')
        members = r.get('TeamMemberUserNames', '')
        print(f"{i:2d}. [Rank {i:2d}] {team:<32} | Score: {float(score):.5f} | Subs: {r.get('SubmissionCount')} | Members: {members}")

    print("\n=== TARGET TEAM SEARCH (akshitagarwal / TuringIRL) ===")
    for i, r in enumerate(rows, 1):
        members = r.get('TeamMemberUserNames', '').lower()
        name = r.get('TeamName', '').lower()
        if 'akshit' in members or 'akshit' in name or 'turing' in name:
            print(f"Found -> Rank {i:3d}: {r.get('TeamName')} | Score: {r.get('Score')} | Subs: {r.get('SubmissionCount')} | Members: {r.get('TeamMemberUserNames')}")

    print("\n=== TOP 10 SCORE BREAKDOWN ===")
    for i in range(10):
        r = rows[i]
        print(f"Rank {i+1:2d}: {float(r.get('Score')):.5f} ({r.get('TeamName')}) [Members: {r.get('TeamMemberUserNames')}]")

if __name__ == '__main__':
    parse_leaderboard()
