lines = open('fact/components/invsqrt_62q.kmx', encoding='ascii').read().splitlines()

# Inspect what changes between line 35825 and line 36820
print("Lines that modify q17, q53, q35, q36, q37, q38 in [35825, 36820]:")
ladder_controls = {'q17', 'q53', 'q35', 'q36', 'q37', 'q38'}

for i in range(35825, 36825):
    l = lines[i].strip()
    parts = l.split()
    if not parts:
        continue
    op = parts[0]
    # check if op modifies any control
    # in CX c t, target t is modified
    # in CCX c1 c2 t, target t is modified
    # in X t / R t / HMR t, target t is modified
    if op in ('X', 'R', 'HMR') and parts[1] in ladder_controls:
        print(f"Line {i:5d}: {l}")
    elif op == 'CX' and parts[2] in ladder_controls:
        print(f"Line {i:5d}: {l}")
    elif op == 'CCX' and parts[3] in ladder_controls:
        print(f"Line {i:5d}: {l}")
    elif op in ('SWAP', 'CSWAP') and any(q in parts[1:] for q in ladder_controls):
        print(f"Line {i:5d}: {l}")
