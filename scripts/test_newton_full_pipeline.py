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
from exp.decoder.common import ar

spec = ProblemSpecDQI.benchmark_instance()
tables = FieldTables(km.GF2Field(spec.degree))
rng = np.random.default_rng(12345)
weight_probs = optimal_dqi_weights(spec.m, spec.max_errors, spec.degree, spec.r) ** 2

num_shots = 4
syndromes, mbuc, phases = sample_shots(spec, tables, rng, num_shots, weight_probs)

print(f"[*] Testing baseline decode reversibility on {num_shots} shots without full scan...", flush=True)

# Import decode_retimed
spec_mod = importlib.util.spec_from_file_location('decoder_under_test', HERE / 'exp/r-main/narrow240/decode_retimed.py')
module = importlib.util.module_from_spec(spec_mod)
sys.modules['decoder_under_test'] = module
spec_mod.loader.exec_module(module)

# Create circuit
b = km.CircuitBuilder()
S = [b.alloc_qubits(12) for _ in range(70)]
E = [b.alloc_bits(12) for _ in range(4095)]

# Build full decode but with scan skipped (to test exact state reversibility of S)
with b.mark('mask_projection'): mt = module.ref.baseline.project(b, S, E)
with b.mark('initial'): module.ref.linear_words(b, S, module.ref.matrix)
with b.mark('extract'): et = module.extraction(b, S)
with b.mark('synthesis'): A, B, undo = module.synthesize(b, S, et['pole'])
with b.mark('convert'): ct = module.convert_safe(b, A, B, monic_root=True)
with b.mark('unconvert'): module.convert_safe(b, A, B, True, phase_token=ct)
with b.mark('unsynthesis'): undo()
with b.mark('unextract'): module.extraction(b, S, True, et)
with b.mark('uninitial'): module.ref.linear_words(b, S, module.ref.matrix, True)
with b.mark('restore_masks'): module.ref.baseline.restore(b, E, mt)

c = b.finish_circuit()
print(f"[+] Circuit built! Gates={len(c):,}, Toffolis={c.operation_statistics().num_toffoli_like:,}", flush=True)

sim = km.Simulator(batch_size=num_shots, counting_operations=True, seed=42)
sim.use_same_registers_as(c)
sim.write_across_shots(km.array([q for reg in S for q in reg]), to_bits(syndromes, 12))
sim.write_across_shots(km.array([bit for reg in E for bit in reg]), to_bits(mbuc, 12))

print("[*] Running simulation...", flush=True)
t0 = time.time()
sim.do(c)
print(f"[+] Simulation done in {time.time() - t0:.2f}s", flush=True)

# Verify syndrome restoration across all shots
all_ok = True
for shot in range(num_shots):
    shot_match = True
    for word_idx in range(70):
        bits = sim.read_across_shots(km.array(S[word_idx]))[:, shot].flatten()
        val = sum(int(bit) << i for i, bit in enumerate(bits))
        exp = syndromes[shot, word_idx]
        if val != exp:
            shot_match = False
            all_ok = False
            print(f"Shot {shot} word {word_idx}: got {val}, expected {exp}")
            break
    if shot_match:
        print(f"Shot {shot}: All 70 syndrome words exactly restored!")

phase_flipped = sim.read_phase_flipped_across_shots()
print(f"Phase flipped (scan skipped, expect all False): {phase_flipped.tolist()}")
print(f"Overall test SUCCESS: {all_ok}")

