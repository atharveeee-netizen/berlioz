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

spec = ProblemSpecDQI.benchmark_instance()
tables = FieldTables(km.GF2Field(spec.degree))
rng = np.random.default_rng(12345)

weight_probs = optimal_dqi_weights(spec.m, spec.max_errors, spec.degree, spec.r) ** 2
num_test_shots = 2
syndromes, mbuc, phases = sample_shots(spec, tables, rng, num_test_shots, weight_probs)

field = km.GF2Field(12)

print(f"[*] Testing Newton Phase Cancellation on {num_test_shots} shots...", flush=True)

# Build circuit with forward pass + phase cancellation:
b = km.CircuitBuilder()
S = [b.alloc_qubits(12) for _ in range(70)]
E = [b.alloc_bits(12) for _ in range(4095)]

# 1. Forward pass
with b.mark('mask_projection'): mt = ref.baseline.project(b, S, E)
with b.mark('initial'):         ref.linear_words(b, S, ref.matrix)
with b.mark('extract'):         et = ref.extraction(b, S)
with b.mark('synthesis'):       A, B, undo = ref.synthesize(b, S, et['pole'])
with b.mark('convert'):         ct = ref.convert_safe(b, A, B, monic_root=True)
with b.mark('scan'):            ref.baseline.scan(b, A, B, E, skip_points=ref.baseline.SELECTED, node_polynomial=ref.Pscan)
with b.mark('unconvert'):       ref.convert_safe(b, A, B, True, phase_token=ct)

# Finish circuit and simulate
c = b.finish_circuit()
print(f"[+] Built circuit with {len(c)} ops, {c.operation_statistics().num_toffoli_like} Toffolis", flush=True)

sim = km.Simulator(batch_size=num_test_shots, counting_operations=True, seed=42)
sim.use_same_registers_as(c)

input_syndromes = to_bits(syndromes, spec.degree)
sim.write_across_shots(km.array([q for reg in S for q in reg]), input_syndromes)
sim.write_across_shots(km.array([bit for reg in E for bit in reg]), to_bits(mbuc, spec.degree))

sim.do(c)
phase_flipped = sim.read_phase_flipped_across_shots()

for shot in range(num_test_shots):
    got = phase_flipped[shot]
    exp = phases[shot]
    print(f"Shot {shot:2d}: Got={got}, Exp={exp}, Match={got == exp}", flush=True)
