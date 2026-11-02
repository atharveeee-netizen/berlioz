lines = open('fact/components/invsqrt_62q.kmx', encoding='ascii').read().splitlines()

# Track all CCX gates and their controls
ccx_dict = {} # (c1, c2) -> list of (line_idx, target)
for i, l in enumerate(lines):
    parts = l.strip().split()
    if parts and parts[0] == 'CCX':
        c1, c2, target = parts[1], parts[2], parts[3]
        key = tuple(sorted((c1, c2)))
        if key not in ccx_dict:
            ccx_dict[key] = []
        ccx_dict[key].append((i, target))

print("Pairs of CCX gates with identical controls:")
dup_count = 0
for ctrls, occurrences in ccx_dict.items():
    if len(occurrences) > 1:
        dup_count += len(occurrences) - 1
        print(f"Controls {ctrls}: {len(occurrences)} occurrences:")
        for idx, target in occurrences:
            print(f"   Line {idx:5d} -> target {target}")

print(f"\nTotal redundant CCX gates with identical controls: {dup_count}")
