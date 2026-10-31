import json
import csv
import sys
from kaggle.api.kaggle_api_extended import KaggleApi

sys.stdout.reconfigure(encoding='utf-8')

def main():
    api = KaggleApi()
    api.authenticate()

    with open('leaderboard_export/public_notebooks.json', 'r', encoding='utf-8') as f:
        nb = json.load(f)

    # Let's also check top 50 users from leaderboard
    csv_path = 'leaderboard_export/google-verifiable-quantum-circuit-compilation-publicleaderboard-2026-10-31T06_27_40.csv'
    with open(csv_path, mode='r', encoding='utf-8', errors='replace') as f:
        rows = list(csv.DictReader(f))

    print(f"Total LB entries: {len(rows)}")
    top_teams = rows[:50]
    
    user_to_team = {}
    for r in top_teams:
        rank = r.get('\ufeffRank', '')
        team_name = r.get('TeamName', '')
        score = r.get('Score', '')
        members = r.get('TeamMemberUserNames', '').split(',')
        for m in members:
            m = m.strip()
            if m:
                user_to_team[m.lower()] = {
                    'rank': rank,
                    'team': team_name,
                    'score': score
                }

    print(f"Top 50 unique team members: {len(user_to_team)}")

    print("\n=== PUBLIC NOTEBOOKS FROM TOP 50 COMPETITORS ===")
    matches = []
    for n in nb:
        author = n['ref'].split('/')[0].lower()
        if author in user_to_team:
            tinfo = user_to_team[author]
            matches.append((tinfo, n))
            print(f"Rank {tinfo['rank']:>2} [{tinfo['score']}] Team: '{tinfo['team']}' | Author: {author}")
            print(f"    Notebook: {n['title']} (Votes: {n['votes']})")
            print(f"    URL: {n['url']}")

    print("\n=== SEARCHING KAGGLE DIRECTLY FOR TOP 10 USERS' NOTEBOOKS ===")
    top10_users = []
    for r in rows[:10]:
        for m in r.get('TeamMemberUserNames', '').split(','):
            if m.strip():
                top10_users.append((r.get('\ufeffRank'), r.get('TeamName'), r.get('Score'), m.strip()))

    for rank, team, score, user in top10_users:
        try:
            user_kernels = api.kernels_list(user=user, page_size=10)
            if user_kernels:
                print(f"\nUser '{user}' (Rank {rank}, Team '{team}', Score {score}) has {len(user_kernels)} kernels:")
                for uk in user_kernels:
                    print(f"  - {uk.title} (Votes: {getattr(uk, 'total_votes', 0)}) -> https://www.kaggle.com/code/{uk.ref}")
        except Exception as e:
            pass

if __name__ == '__main__':
    main()
