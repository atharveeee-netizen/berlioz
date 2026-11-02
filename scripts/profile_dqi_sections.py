"""Profile Toffoli count in each section of the DQI decoder."""

import importlib.util
from pathlib import Path
import sys
import kickmix as km

HERE = Path('build/somejoint_src/blocks/dqi/team-1028-narrow240/source')
sys.modules['circ'] = km
sys.path[:0] = [str(HERE), str(HERE / 'exp/r-main/narrow240')]

spec = importlib.util.spec_from_file_location('decoder_under_test', HERE / 'exp/r-main/narrow240/decode_retimed.py')
module = importlib.util.module_from_spec(spec)
sys.modules['decoder_under_test'] = module
spec.loader.exec_module(module)

b = km.CircuitBuilder()
S = [b.alloc_qubits(12) for _ in range(70)]
E = [b.alloc_bits(12) for _ in range(4095)]

module.decode(b, S, E)

c = b.finish_circuit()
print(f"Total circuit operations: {len(c)}")
print(f"Total Toffoli-like gates: {c.operation_statistics().num_toffoli_like}")
print(f"Total Active Qubits:      {c.num_qubits}")

# Let's inspect operations by marks
stats_by_mark = c.operation_statistics_by_mark()
print("\n=== TOFFOLI GATES BY MARKED SECTION ===")
for mark, stats in stats_by_mark.items():
    print(f"{mark:20s}: Toffolis={stats.num_toffoli_like:7d}, Total ops={stats.num_operations:8d}")
