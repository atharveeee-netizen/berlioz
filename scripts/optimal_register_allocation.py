import re
import heapq

lines = open('build/circuits/test_remap_q61_q47.kmx', encoding='ascii').read().splitlines()
q_pat = re.compile(r'\bq(\d+)\b')

# 1. Inputs q0..q21 are pinned: color(q) = q for q < 22.
# 2. For each scratch qubit q >= 22:
# Trace its actual life segments.
# A segment starts at the first gate that uses q (or the first gate using q after an HMR).
# A segment ends at the HMR gate that measures/resets q (or the very last gate using q).

segments = [] # list of (orig_q, start_line, end_line)

current_start = {}
last_op = {}

for line_idx, line in enumerate(lines):
    parts = line.strip().split()
    if not parts:
        continue
    op = parts[0]
    qubits_in_line = [int(m.group(1)) for m in q_pat.finditer(line)]
    
    if op == 'HMR':
        q = int(parts[1][1:])
        if q >= 22:
            start = current_start.get(q, line_idx)
            segments.append((q, start, line_idx))
            if q in current_start:
                del current_start[q]
            if q in last_op:
                del last_op[q]
    elif op == 'R':
        q = int(parts[1][1:])
        if q >= 22:
            if q in current_start:
                segments.append((q, current_start[q], line_idx - 1))
            current_start[q] = line_idx
    else:
        for q in qubits_in_line:
            if q >= 22:
                if q not in current_start:
                    current_start[q] = line_idx
                last_op[q] = line_idx

# Any remaining open segments end at their last operation
for q, start in current_start.items():
    end = last_op.get(q, len(lines) - 1)
    segments.append((q, start, end))

print(f"Total live segments extracted for scratch qubits: {len(segments)}")

# Check max concurrency of these segments across all gates:
events = []
for orig_q, s, e in segments:
    events.append((s, 1, orig_q))
    events.append((e + 1, -1, orig_q))

events.sort(key=lambda x: (x[0], -x[1]))

max_concurrent = 0
curr = 0
for t, typ, q in events:
    curr += typ
    if curr > max_concurrent:
        max_concurrent = curr

print(f"Max concurrently active scratch segments: {max_concurrent}")
print(f"Total qubits needed = 22 (inputs) + {max_concurrent} (scratches) = {22 + max_concurrent} QUBITS!")

