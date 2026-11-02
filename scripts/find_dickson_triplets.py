import re

lines = open('fact/components/invsqrt_62q.kmx', encoding='ascii').read().splitlines()

# Search for patterns where two CCX gates target the same register with shared control,
# followed or preceded by a third CCX gate between the two other controls!
# i.e., CCX(u, w, T), CCX(v, w, T), and CCX(u, v, ...)

ccx_list = []
for i, l in enumerate(lines):
    parts = l.strip().split()
    if parts and parts[0] == 'CCX':
        c1, c2, t = parts[1], parts[2], parts[3]
        ccx_list.append((i, set([c1, c2]), t, l))

print(f"Total CCX gates: {len(ccx_list)}")

triplets = []
for idx in range(len(ccx_list) - 2):
    i1, ctrls1, t1, l1 = ccx_list[idx]
    for jdx in range(idx + 1, min(idx + 10, len(ccx_list))):
        i2, ctrls2, t2, l2 = ccx_list[jdx]
        if t1 != t2:
            continue
        shared_w = ctrls1.intersection(ctrls2)
        if len(shared_w) != 1:
            continue
        w = list(shared_w)[0]
        u = list(ctrls1 - shared_w)[0]
        v = list(ctrls2 - shared_w)[0]
        # Now search within a window of 50 CCX gates for a CCX between u and v (or with CX linear combinations of u and v)
        for kdx in range(max(0, idx - 15), min(len(ccx_list), jdx + 16)):
            if kdx in (idx, jdx):
                continue
            i3, ctrls3, t3, l3 = ccx_list[kdx]
            if {u, v} == ctrls3 or (u in ctrls3 and v in ctrls3):
                triplets.append((i1, i2, i3, u, v, w, t1, t3))

print(f"Found {len(triplets)} candidate Dickson 3-to-2 quadratic triplets:")
for tr in triplets[:20]:
    print(f"Lines {tr[0]}, {tr[1]}, {tr[2]} -> u={tr[3]}, v={tr[4]}, w={tr[5]} | targets: T1={tr[6]}, T3={tr[7]}")
