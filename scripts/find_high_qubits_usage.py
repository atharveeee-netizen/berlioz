import re

lines = open('fact/components/invsqrt_62q.kmx', encoding='ascii').read().splitlines()
q_pattern = re.compile(r'\bq(\d+)\b')

print(f"Total lines in invsqrt_62q.kmx: {len(lines)}")

for high_q in [58, 59, 60, 61]:
    qlines = [(i, l) for i, l in enumerate(lines) if f'q{high_q}' in l.split()]
    print(f"\n=== QUBIT q{high_q} (Total {len(qlines)} gates) ===")
    if qlines:
        first_i, first_l = qlines[0]
        last_i, last_l = qlines[-1]
        print(f"  First: line {first_i:5d}: {first_l}")
        print(f"  Last:  line {last_i:5d}: {last_l}")
        # Show all distinct gate types using q{high_q}
        gate_types = set(l.split()[0] for _, l in qlines)
        print(f"  Gate types: {gate_types}")
