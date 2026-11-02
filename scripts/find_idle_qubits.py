import re

lines = open('build/harvest_busyaprime/invsqrt.kmx', encoding='ascii').read().splitlines()
q_pattern = re.compile(r'\bq(\d+)\b')

# Track qubit state throughout execution:
# State can be:
# 'UNINITIALIZED' (clean |0>)
# 'ACTIVE' (in superposition / holding non-zero state)
# 'CLEAN' (measured with HMR or R, clean |0>)

state = {q: 'UNINITIALIZED' for q in range(62)}
# q0..q21 are inputs (ACTIVE from start)
for q in range(22):
    state[q] = 'ACTIVE'

clean_counts = []

for i, l in enumerate(lines):
    parts = l.strip().split()
    if not parts:
        continue
    op = parts[0]
    qubits = [int(m.group(1)) for m in q_pattern.finditer(l)]
    
    if op == 'R':
        target = int(parts[1][1:])
        state[target] = 'CLEAN'
    elif op == 'HMR':
        target = int(parts[1][1:])
        state[target] = 'CLEAN'
    else:
        for q in qubits:
            if q >= 22:
                state[q] = 'ACTIVE'

    # Check state at key lines
    if op == 'R' and target in (58, 59, 60, 61):
        free_qubits = [q for q in range(22, 58) if state[q] in ('UNINITIALIZED', 'CLEAN')]
        print(f"Line {i:5d}: {l} -> Available clean qubits in q22..q57: {len(free_qubits)} -> {free_qubits[:10]}")
