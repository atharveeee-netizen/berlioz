import re

lines = open('build/circuits/ehan_invsqrt.kmx', encoding='ascii').read().splitlines()
q_pat = re.compile(r'\bq(\d+)\b')

# For each qubit q in 22..57, find all its gate line numbers
gate_lines = {q: [] for q in range(22, 58)}
for i, l in enumerate(lines):
    for m in q_pat.finditer(l):
        q = int(m.group(1))
        if 22 <= q < 58:
            gate_lines[q].append(i)

# Find the biggest idle gap in each qubit q
print("=== BIGGEST IDLE GAPS IN SCRATCH QUBITS q22..q57 ===")
gaps = []
for q in range(22, 58):
    gl = gate_lines[q]
    if not gl:
        print(f"q{q}: NEVER USED!")
        continue
    # Check gap between 0 and first use
    if gl[0] > 0:
        gaps.append((q, 0, gl[0], gl[0]))
    # Check internal gaps
    for idx in range(len(gl) - 1):
        gap_size = gl[idx+1] - gl[idx] - 1
        if gap_size > 2000:
            gaps.append((q, gl[idx], gl[idx+1], gap_size))
    # Check gap after last use
    if gl[-1] < len(lines) - 1:
        gap_size = len(lines) - 1 - gl[-1]
        if gap_size > 2000:
            gaps.append((q, gl[-1], len(lines) - 1, gap_size))

gaps.sort(key=lambda x: x[3], reverse=True)
for g in gaps[:30]:
    print(f"q{g[0]:2d}: lines {g[1]:5d} to {g[2]:5d} (GAP = {g[3]:5d} gates)")
