import kickmix as km
import sys
from pathlib import Path

source_dir = Path("build/somejoint_src/blocks/dqi/team-1028-narrow240/source")
sys.path.insert(0, str(source_dir))
sys.path.insert(0, str(source_dir / "playbook/kit/decoder"))
sys.path.insert(0, str(source_dir / "playbook/kit"))
sys.modules['circ'] = km

from final_decoder import decode as ref

b = km.CircuitBuilder()
S = [b.alloc_qubits(12) for _ in range(70)]
E = [b.alloc_bits(12) for _ in range(4095)]

ref.decode(b, S, E)

c = b.finish_circuit()
print(f"Num qubits: {c.num_qubits}")
print(f"Num bits: {c.num_bits}")
stats = c.operation_statistics()
print(f"Toffolis: {stats.num_toffoli_like}")
print(f"Total ops: {len(c)}")
