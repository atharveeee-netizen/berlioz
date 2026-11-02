import csv

rows = list(csv.DictReader(open('build/harvest_manifest/manifest.csv', encoding='utf-8')))

print("=== DQI CIRCUITS WITH < 892 QUBITS IN MANIFEST ===")
for r in rows:
    if r.get('task') == 'dqi':
        try:
            q = int(r.get('qubits', 9999))
            if q < 892:
                print(f"[{r.get('sha12')}] Q={q} score={r.get('local_task_score')} author={r.get('author')}")
                print(f"    change: {r.get('change_summary')}")
        except:
            pass

print("\n=== INVSQRT CIRCUITS WITH < 62 QUBITS IN MANIFEST ===")
for r in rows:
    if r.get('task') == 'invsqrt':
        try:
            q = int(r.get('qubits', 9999))
            if q < 62:
                print(f"[{r.get('sha12')}] Q={q} score={r.get('local_task_score')} author={r.get('author')}")
                print(f"    change: {r.get('change_summary')}")
        except:
            pass
