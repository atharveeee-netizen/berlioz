import kickmix as km
import sys
from pathlib import Path

# Add paths
source_dir = Path("build/somejoint_src/blocks/dqi/team-1028-narrow240/source")
sys.path.insert(0, str(source_dir))
sys.path.insert(0, str(source_dir / "playbook/kit/decoder"))
sys.path.insert(0, str(source_dir / "playbook/kit"))
sys.modules['circ'] = km

from final_decoder import decode as ref

class CountingBuilder:
    def __init__(self):
        self.b = km.CircuitBuilder()
        self.stage_toffolis = {}
        self.current_stage = "pre"
        self.toffolis_at_entry = 0

    def mark(self, name):
        class MarkContext:
            def __init__(ctx, builder, stage_name):
                ctx.builder = builder
                ctx.stage_name = stage_name
            def __enter__(ctx):
                # get current toffoli count from finish_circuit or track
                pass
            def __exit__(ctx, *args):
                pass
        return self.b.mark(name)

# Let's inspect ref.decode marks by running with real builder
b = km.CircuitBuilder()
S = [b.alloc_qubits(12) for _ in range(70)]
E = [b.alloc_bits(12) for _ in range(4095)]

print("Building circuit and collecting marks...")
ref.decode(b, S, E)
circuit = b.finish_circuit()

toffolis_by_mark = {}
current_mark = "pre"
mark_counts = {current_mark: 0}

for op in circuit:
    # check if op is a MARK instruction
    op_str = str(op)
    if "MARK" in op_str:
        # e.g. MARK "synthesis"
        parts = op_str.split('"')
        if len(parts) >= 2:
            current_mark = parts[1]
            if current_mark not in mark_counts:
                mark_counts[current_mark] = 0
    elif "CCX" in op_str or "CCZ" in op_str or "CSWAP" in op_str:
        mark_counts[current_mark] = mark_counts.get(current_mark, 0) + 1

print("\n--- TOFFOLI BREAKDOWN BY STAGE ---")
total = 0
for stage, count in mark_counts.items():
    print(f"  {stage:20s}: {count:8d} Toffolis")
    total += count
print(f"  {'TOTAL':20s}: {total:8d} Toffolis")
