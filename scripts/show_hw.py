import csv

rows = list(csv.DictReader(open('build/harvest_hedgewizardry/entries.csv', encoding='utf-8')))
for r in rows:
    if r['id'] in ('HW-01', 'HW-06', 'HW-07', 'HW-08'):
        print(f"\n=== {r['id']} ({r.get('task')}) ===")
        print(f"Title:        {r.get('title')}")
        print(f"Base:         {r.get('base_circuit')}")
        print(f"Candidate:    {r.get('candidate_sha12')} ({r.get('dataset_path')})")
        print(f"Qubits:       {r.get('qubits')} (delta: {r.get('delta_qubits')})")
        print(f"Toffolis:     {r.get('toffoli_mean')} (delta: {r.get('delta_toffoli_mean')})")
        print(f"Score:        {r.get('local_task_score')}")
        print(f"Expected GM:  {r.get('expected_gm_candidate')} (gain: +{r.get('expected_gm_gain_pct')}%)")
        print(f"Card Summary: {r.get('card_summary')[:200]}")
