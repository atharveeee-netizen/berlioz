import zipfile
import io
import csv
from kaggle.api.kaggle_api_extended import KaggleApi

z = zipfile.ZipFile('build/leaderboard/google-verifiable-quantum-circuit-compilation.zip')
name = z.namelist()[0]
rows = list(csv.DictReader(io.TextIOWrapper(z.open(name), encoding='utf-8')))

print('=== TOP 10 TEAMS ON LIVE LEADERBOARD ===')
api = KaggleApi()
api.authenticate()

top10 = rows[:10]
for i, r in enumerate(top10, 1):
    rank = i
    score = r.get('Score')
    team = r.get('TeamName')
    members = [m.strip() for m in r.get('TeamMemberUserNames', '').split(',') if m.strip()]
    subs = r.get('SubmissionCount')
    date = r.get('LastSubmissionDate')
    print(f"\n--- Rank #{rank}: {team} | Score: {score} | Subs: {subs} | Date: {date} ---")
    print(f"Members: {members}")
    for u in members:
        try:
            kernels = api.kernels_list(user=u, page_size=5)
            print(f"  User @{u}: {len(kernels)} public kernels")
            for k in kernels:
                print(f"    - {k.title} | ref={k.ref}")
        except Exception as e:
            print(f"  User @{u}: failed to list kernels ({e})")
