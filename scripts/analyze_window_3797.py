import re

lines = open('fact/components/invsqrt_62q.kmx', encoding='ascii').read().splitlines()

# At line 3797, which qubits are used between line 250 and line 3797?
# Let's count total operations on each qubit q in the window [250, 3797]
print("Operations on each qubit in window [250, 3797]:")
for q in range(62):
    uses = [i for i, l in enumerate(lines[250:3797], 250) if f'q{q}' in l.split()]
    after = [i for i, l in enumerate(lines[3797:], 3797) if f'q{q}' in l.split()]
    first_after = after[0] if after else None
    if len(uses) < 10 or first_after is None or first_after > 10000:
        print(f"q{q:2d}: uses in [250, 3797] = {len(uses):3d} | first after 3797 = {first_after}")
