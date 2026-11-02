import re
from collections import defaultdict

lines = open('fact/components/invsqrt_62q.kmx', encoding='ascii').read().splitlines()

# Find all CCX gates
ccx_gates = []
for i, l in enumerate(lines):
    parts = l.strip().split()
    if parts and parts[0] == 'CCX':
        c1, c2, target = parts[1], parts[2], parts[3]
        # sort controls so (c1, c2) == (c2, c1)
        ctrls = tuple(sorted((c1, c2)))
        ccx_gates.append((i, ctrls, target))

print(f"Total CCX gates in invsqrt: {len(ccx_gates)}")

# Group CCX gates by shared target or shared controls within windows of 50 lines
shared_target_pairs = []
for idx in range(len(ccx_gates) - 1):
    i1, c1, t1 = ccx_gates[idx]
    for jdx in range(idx + 1, min(idx + 10, len(ccx_gates))):
        i2, c2, t2 = ccx_gates[jdx]
        if i2 - i1 > 40:
            break
        if t1 == t2:
            # Two CCX targeting the same qubit! (c1a * c1b) ^ (c2a * c2b) -> t1
            # Check if they share a control wire!
            shared_ctrl = set(c1).intersection(set(c2))
            if shared_ctrl:
                shared_target_pairs.append((i1, i2, c1, c2, t1, list(shared_ctrl)[0]))

print(f"Found {len(shared_target_pairs)} candidate shared-target CCX pairs within 40 lines!")
for p in shared_target_pairs[:15]:
    i1, i2, c1, c2, t, sc = p
    print(f"Lines {i1:5d} & {i2:5d} -> Target {t}, Shared control {sc}: {c1} and {c2}")
