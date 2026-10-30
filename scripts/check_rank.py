import zipfile, csv, io, os

zip_path = "google-verifiable-quantum-circuit-compilation.zip"
if not os.path.exists(zip_path):
    print("Zip not found")
    exit(1)

with zipfile.ZipFile(zip_path) as z:
    for name in z.namelist():
        print("Examining:", name)
        with z.open(name) as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8"))
            rows = list(reader)
            print(f"Total teams on full leaderboard: {len(rows)}")
            for rank, row in enumerate(rows, 1):
                tname = row.get("TeamName", "")
                score = row.get("Score", "")
                if "turingirl" in tname.lower() or "akshit" in tname.lower() or "atharve" in tname.lower():
                    print(f"[*] EXACT MATCH FOUND:")
                    print(f"    Rank: #{rank}")
                    print(f"    Team Name: {tname}")
                    print(f"    Score: {score}")
                    print(f"    Submission Date: {row.get('SubmissionDate')}")
                    print(f"    Total Teams: {len(rows)}")
                    print(f"    Top Percentile: {(rank / len(rows)) * 100:.2f}%")
                    break

os.remove(zip_path)
