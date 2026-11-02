lines = open('fact/components/invsqrt_62q.kmx', encoding='ascii').read().splitlines()

# Search for exact Ehan-style clusters:
# CCX c1 shared T
# CCX c2 shared T (within 15 lines of first CCX)
# CCX c1 (or c2) other c2 (or c1) (within 30 lines)

clusters = []
for i in range(len(lines)):
    l1 = lines[i].strip()
    if not l1.startswith('CCX'):
        continue
    p1 = l1.split()
    c1a, c1b, t1 = p1[1], p1[2], p1[3]
    
    # search within next 20 lines for another CCX targeting t1
    for j in range(i + 1, min(i + 20, len(lines))):
        l2 = lines[j].strip()
        if not l2.startswith('CCX'):
            continue
        p2 = l2.split()
        c2a, c2b, t2 = p2[1], p2[2], p2[3]
        if t1 != t2:
            continue
        
        # Check if they share exactly one control
        set1 = {c1a, c1b}
        set2 = {c2a, c2b}
        shared = set1.intersection(set2)
        if len(shared) != 1:
            continue
        w = list(shared)[0]
        u = list(set1 - shared)[0]
        v = list(set2 - shared)[0]
        
        # Now search within next 50 lines for a CCX involving u and v
        for k in range(j + 1, min(j + 50, len(lines))):
            l3 = lines[k].strip()
            if not l3.startswith('CCX'):
                continue
            p3 = l3.split()
            c3a, c3b, t3 = p3[1], p3[2], p3[3]
            set3 = {c3a, c3b}
            if u in set3 or v in set3:
                clusters.append((i, j, k, u, v, w, t1, t3, l1, l2, l3))

print(f"Total Ehan-style candidate clusters found: {len(clusters)}")
for cl in clusters:
    print(f"Lines {cl[0]:5d}, {cl[1]:5d}, {cl[2]:5d} -> u={cl[3]}, v={cl[4]}, w={cl[5]} | T1={cl[6]}, T3={cl[7]}")
    print(f"   {cl[8]}")
    print(f"   {cl[9]}")
    print(f"   {cl[10]}")
