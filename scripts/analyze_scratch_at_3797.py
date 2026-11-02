import re

lines = open('fact/components/invsqrt_62q.kmx', encoding='ascii').read().splitlines()

# At line 3797, all 40 scratch qubits q22..q61 are live.
# Let's inspect when each qubit was last modified before line 3797,
# and how many gates were used to compute it!

for q in range(22, 62):
    # find all gates modifying q before 3797
    mod_gates = []
    for i in range(3797):
        parts = lines[i].strip().split()
        if not parts:
            continue
        op = parts[0]
        # in CX c t, target t is modified (and c is unmodified)
        # in CCX c1 c2 t, target t is modified
        # in X t, t is modified
        # in R t / HMR t, t is reset
        if op in ('X', 'R', 'HMR') and parts[1] == f'q{q}':
            mod_gates.append((i, lines[i]))
        elif op == 'CX' and parts[2] == f'q{q}':
            mod_gates.append((i, lines[i]))
        elif op == 'CCX' and parts[3] == f'q{q}':
            mod_gates.append((i, lines[i]))
        elif op in ('SWAP', 'CSWAP') and f'q{q}' in parts[1:]:
            mod_gates.append((i, lines[i]))
            
    last_mod = mod_gates[-1] if mod_gates else (None, None)
    print(f"q{q:2d}: total mod gates before 3797 = {len(mod_gates):3d} | last: line {last_mod[0]} ({last_mod[1]})")
