lines = open('fact/components/invsqrt_62q.kmx', encoding='ascii').read().splitlines()

for q in range(22, 62):
    before = [(i, l) for i, l in enumerate(lines[:3797]) if f'q{q}' in l.split()]
    after = [(i, l) for i, l in enumerate(lines[3797:], 3797) if f'q{q}' in l.split()]
    
    last_before = before[-1] if before else (None, None)
    first_after = after[0] if after else (None, None)
    
    print(f"q{q:2d}: last before 3797: {last_before[0]} ({last_before[1]}) | first after: {first_after[0]} ({first_after[1]})")
