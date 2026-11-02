import csv

rows = list(csv.DictReader(open('build/harvest_manifest/manifest.csv', encoding='utf-8')))
print(f'Total circuits in manifest: {len(rows)}')

tasks = set(r.get('task') for r in rows)
print(f'Tasks: {tasks}')

for task in ['invsqrt', 'dqi', 'chemistry']:
    t_rows = [r for r in rows if r.get('task') == task]
    def get_score(r):
        try:
            return float(r.get('local_task_score', r.get('score', 1e18)))
        except:
            return 1e18
    t_rows.sort(key=get_score)
    print(f'\n=== TOP 5 {task.upper()} CIRCUITS IN PUBLIC MANIFEST ===')
    for r in t_rows[:5]:
        sha = r.get('sha12', '')
        score = r.get('local_task_score', '')
        q = r.get('qubits', '')
        auth = r.get('author', '')
        nb = r.get('notebook_title', '')
        summary = r.get('change_summary', '')
        print(f"[{sha}] score={score} Q={q} author={auth}")
        print(f"    nb: {nb}")
        print(f"    change: {summary}")
