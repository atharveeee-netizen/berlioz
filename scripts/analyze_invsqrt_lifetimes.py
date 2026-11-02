from collections import defaultdict
import re

lines = open('build/harvest_busyaprime/invsqrt.kmx', encoding='ascii').read().splitlines()
print(f"Total lines/gates: {len(lines)}")

first_seen = {}
last_seen = {}
gate_counts = defaultdict(lambda: defaultdict(int))

q_pattern = re.compile(r'\bq(\d+)\b')

for line_idx, line in enumerate(lines):
    parts = line.strip().split()
    if not parts:
        continue
    op = parts[0]
    qubits = [int(m.group(1)) for m in q_pattern.finditer(line)]
    for q in qubits:
        if q not in first_seen:
            first_seen[q] = line_idx
        last_seen[q] = line_idx
        gate_counts[q][op] += 1

num_qubits = max(last_seen.keys()) + 1
print(f"Detected qubits: 0 to {num_qubits - 1} (Total {num_qubits} qubits)")

print("\n=== QUBIT LIFETIMES & ACTIVITY ===")
for q in range(num_qubits):
    f = first_seen.get(q, -1)
    l = last_seen.get(q, -1)
    total_ops = sum(gate_counts[q].values())
    ccx_ops = gate_counts[q].get('CCX', 0)
    print(f"q{q:2d}: first={f:5d}, last={l:5d}, duration={l - f:5d}, total_ops={total_ops:5d}, CCX={ccx_ops:4d}")
