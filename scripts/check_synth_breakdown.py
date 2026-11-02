import kickmix as km
import sys
from pathlib import Path

source_dir = Path("build/somejoint_src/blocks/dqi/team-1028-narrow240/source")
sys.path.insert(0, str(source_dir))
sys.path.insert(0, str(source_dir / "playbook/kit/decoder"))
sys.path.insert(0, str(source_dir / "playbook/kit"))
sys.modules['circ'] = km

from final_decoder import decode as ref

# Measure forward synthesize Toffolis
b_fwd = km.CircuitBuilder()
S = [b_fwd.alloc_qubits(12) for _ in range(70)]
pole = b_fwd.alloc_qubits(1)[0]
C, A, undo = ref.synthesize(b_fwd, S, pole)
c_fwd = b_fwd.finish_circuit()
t_fwd = c_fwd.operation_statistics().num_toffoli_like

# Measure undo Toffolis
b_all = km.CircuitBuilder()
S2 = [b_all.alloc_qubits(12) for _ in range(70)]
pole2 = b_all.alloc_qubits(1)[0]
C2, A2, undo2 = ref.synthesize(b_all, S2, pole2)
undo2()
b_all.free(pole2)
c_all = b_all.finish_circuit()
t_all = c_all.operation_statistics().num_toffoli_like
t_undo = t_all - t_fwd

print(f"Forward synthesize Toffolis: {t_fwd}")
print(f"Undo synthesize Toffolis:    {t_undo}")
print(f"Total synthesize+undo:       {t_all}")
