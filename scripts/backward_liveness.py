"""Perform standard compiler backward liveness analysis on invsqrt.kmx to find exact peak live qubit width."""

import re

lines = open('build/harvest_busyaprime/invsqrt.kmx', encoding='ascii').read().splitlines()
q_pattern = re.compile(r'\bq(\d+)\b')

n_lines = len(lines)
num_qubits = 62

# For each gate line, determine:
# defs: qubits whose previous value is destroyed/overwritten (R, HMR)
# uses: qubits whose value is read/tested/modified
# Note: In quantum reversible gates (CX, CCX, CZ, etc.), all operands are 'used' (and modified).
# But R q completely resets q to |0>, so R q is a pure DEF of clean |0>.
# HMR q b measures q in X basis and resets q to |0>, so after HMR, the qubit's previous state is dead!

# Let's track:
# next_use[line][q] = line of next use of q
# next_kill[line][q] = line of next HMR or R of q

# Backward pass:
# is_live[line][q] is True if q will be used before it is next reset/HMR'd
is_live = [False] * num_qubits
live_counts = [0] * n_lines

for i in reversed(range(n_lines)):
    line = lines[i].strip()
    if not line:
        continue
    parts = line.split()
    op = parts[0]
    qubits = [int(m.group(1)) for m in q_pattern.finditer(line)]
    
    if op == 'R':
        target = int(parts[1][1:])
        # R resets qubit to |0>. Its previous state is dead!
        is_live[target] = False
    elif op == 'HMR':
        target = int(parts[1][1:])
        # HMR measures and resets qubit to |0>. Its previous state is dead!
        # (Though classical bit b is written, the quantum wire is now clean |0>).
        is_live[target] = False
    else:
        # Any gate reading or modifying q makes q live!
        for q in qubits:
            is_live[q] = True
            
    # Count how many qubits are currently holding live state
    live_counts[i] = sum(is_live)

peak_live = max(live_counts)
peak_line = live_counts.index(peak_live)
print(f"=== BACKWARD LIVENESS ANALYSIS RESULT ===")
print(f"Maximum concurrently live qubits: {peak_live} at line {peak_line}")
print(f"Lines around peak:")
for j in range(max(0, peak_line - 5), min(n_lines, peak_line + 6)):
    print(f"  {j:5d} ({live_counts[j]} live): {lines[j]}")
