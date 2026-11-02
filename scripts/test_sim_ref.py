import kickmix as km
import numpy as np
import sys
from pathlib import Path

source_dir = Path("build/somejoint_src/blocks/dqi/team-1028-narrow240/source")
sys.path.insert(0, str(source_dir))
sys.path.insert(0, str(source_dir / "playbook/kit/decoder"))
sys.path.insert(0, str(source_dir / "playbook/kit"))
sys.path.insert(0, "verifiers")
sys.modules['circ'] = km

from final_decoder import decode as ref
from dqi.verify_submission_dqi import ProblemSpecDQI, FieldTables, sample_shots, to_bits, validate_registers, optimal_dqi_weights, verify

spec = ProblemSpecDQI.benchmark_instance(num_shots=1)

b = km.CircuitBuilder()
S = [b.alloc_qubits(12) for _ in range(70)]
E = [b.alloc_bits(12) for _ in range(4095)]

ref.decode(b, S, E)

metadata = []
for i in range(70):
    metadata.append(f'REGISTER r{i} "S{i}"')
    metadata.extend(f'APPEND_TO_REGISTER q{12 * i + k} r{i}' for k in range(12))
for j in range(4095):
    metadata.append(f'REGISTER r{70 + j} "E{j}"')
    metadata.extend(f'APPEND_TO_REGISTER b{12 * j + k} r{70 + j}' for k in range(12))

circuit = km.Circuit('\n'.join(metadata)) + b.finish_circuit()

print(f"Built circuit: Q={circuit.num_qubits}, Toffolis={circuit.operation_statistics().num_toffoli_like}")
print("Verifying 1 shot...")
res = verify(circuit, spec, batch_size=1, log2_delta=-10.0, max_workers=1)
print(f"Status: {res['status']}, Val errors: {res['value_errors']}, Phase errors: {res['phase_errors']}")
print(f"Toffolis: {res['toffoli_count']}")
