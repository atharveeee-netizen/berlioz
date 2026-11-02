import sys, time
from pathlib import Path
import kickmix as km
import numpy as np

sys.modules['circ'] = km
sys.path.insert(0, 'verifiers')
sys.path.insert(0, 'build/somejoint_src/blocks/dqi/team-1028-narrow240/source/playbook/kit/decoder')

import importlib.util
HERE = Path('build/somejoint_src/blocks/dqi/team-1028-narrow240/source')

from dqi.verify_submission_dqi import ProblemSpecDQI, FieldTables, sample_shots, to_bits, optimal_dqi_weights

print("[*] Pre-flight verification of Newton builder integration...", flush=True)

spec = importlib.util.spec_from_file_location('decoder_under_test', HERE / 'exp/r-main/narrow240/decode_retimed.py')
module = importlib.util.module_from_spec(spec)
sys.modules['decoder_under_test'] = module
spec.loader.exec_module(module)

b = km.CircuitBuilder()
S = [b.alloc_qubits(12) for _ in range(70)]
E = [b.alloc_bits(12) for _ in range(4095)]

# Mock scan for instant verification
module.ref.baseline.scan = lambda b, A, B, E, **kwargs: None

module.decode(b, S, E)

metadata = []
for i in range(70):
    metadata.append(f'REGISTER r{i} "S{i}"')
    metadata.extend(f'APPEND_TO_REGISTER q{12 * i + k} r{i}' for k in range(12))
for j in range(4095):
    metadata.append(f'REGISTER r{70 + j} "E{j}"')
    metadata.extend(f'APPEND_TO_REGISTER b{12 * j + k} r{70 + j}' for k in range(12))

c = km.Circuit('\n'.join(metadata)) + b.finish_circuit()
print(f"[+] Fast pre-flight circuit built successfully! Qubits={c.num_qubits}, Gates={len(c):,}, Toffolis={c.operation_statistics().num_toffoli_like:,}")

