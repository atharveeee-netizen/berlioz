lines = open('fact/components/invsqrt_62q.kmx', encoding='ascii').read().splitlines()

freed = []
for i in range(3797, 15244):
    l = lines[i].strip()
    parts = l.split()
    if parts and parts[0] == 'HMR':
        q = parts[1]
        b = parts[2]
        # check if this q is used again before line 15244
        future = [j for j, line in enumerate(lines[i+1:15244], i+1) if q in line.split()]
        if not future:
            freed.append((i, q, b))

print(f"Total wires freed and untouched until 15244: {len(freed)}")
for f in freed[:20]:
    print(f"Line {f[0]:5d}: HMR {f[1]} {f[2]}")
