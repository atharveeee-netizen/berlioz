import zipfile, io, csv

with zipfile.ZipFile('google-verifiable-quantum-circuit-compilation.zip') as z:
    name = z.namelist()[0]
    with z.open(name) as f:
        reader = csv.reader(io.TextIOWrapper(f, 'utf-8', errors='ignore'))
        header = next(reader)
        print("Header:", header)
        found = False
        for rank, row in enumerate(reader, 1):
            members = row[6].lower()
            tname = row[2].lower()
            score = row[4]
            # search for common handles
            if any(term in members or term in tname for term in ['atharv', 'netizen', 'pancham', 'berlioz', 'syzygy', 'aic']):
                print(f"Rank {rank:4d}: Team {row[1]} '{row[2]}' Members: {row[6]} | Score: {score}")
                found = True
        if not found:
            print("Did not match keyword in members or team name.")
