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
from dqi.verify_submission_dqi import ProblemSpecDQI, FieldTables, sample_shots, to_bits, optimal_dqi_weights
from exp.decoder.common import ar

print("[*] Testing Newton Phase & Syndrome Restoration...")

spec = ProblemSpecDQI.benchmark_instance()
tables = FieldTables(km.GF2Field(spec.degree))
rng = np.random.default_rng(12345)
weight_probs = optimal_dqi_weights(spec.m, spec.max_errors, spec.degree, spec.r) ** 2

num_shots = 2
syndromes, mbuc, phases = sample_shots(spec, tables, rng, num_shots, weight_probs)

# Let's verify that after forward pass, A and B uniquely determine S
print(f"[+] Syndromes shape: {syndromes.shape}")
print(f"[+] First shot syndromes (first 8): {syndromes[0, :8]}")

# Let's check how many Toffolis are in the forward pass alone
b = km.CircuitBuilder()
S = [b.alloc_qubits(12) for _ in range(70)]
E = [b.alloc_bits(12) for _ in range(4095)]

with b.mark('mask_projection'): mt = ref.baseline.project(b, S, E)
with b.mark('initial'):         ref.linear_words(b, S, ref.matrix)
with b.mark('extract'):         et = ref.extraction(b, S)
with b.mark('synthesis'):       A, B, undo = ref.synthesize(b, S, et['pole'])
with b.mark('convert'):         ct = ref.convert_safe(b, A, B, monic_root=True)
with b.mark('scan'):            ref.baseline.scan(b, A, B, E, skip_points=ref.baseline.SELECTED, node_polynomial=ref.Pscan)
with b.mark('unconvert'):       ref.convert_safe(b, A, B, True, phase_token=ct)

c_fwd = b.finish_circuit()
stats_fwd = c_fwd.operation_statistics()
print(f"[+] Forward + Scan + Unconvert Toffolis: {stats_fwd.num_toffoli_like:,}")

