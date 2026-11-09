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
field = km.GF2Field(spec.degree)
tables = FieldTables(field)
rng = np.random.default_rng(12345)
weight_probs = optimal_dqi_weights(spec.m, spec.max_errors, spec.degree, spec.r) ** 2

num_shots = 2
syndromes, mbuc, phases = sample_shots(spec, tables, rng, num_shots, weight_probs)

# Import decode_retimed
spec_mod = importlib.util.spec_from_file_location('decoder_under_test', HERE / 'exp/r-main/narrow240/decode_retimed.py')
module = importlib.util.module_from_spec(spec_mod)
sys.modules['decoder_under_test'] = module
spec_mod.loader.exec_module(module)

print("[*] Building forward pass to get A, B...", flush=True)
b = km.CircuitBuilder()
S = [b.alloc_qubits(12) for _ in range(70)]
E = [b.alloc_bits(12) for _ in range(4095)]

mt = module.ref.baseline.project(b, S, E)
module.ref.linear_words(b, S, module.ref.matrix)
et = module.extraction(b, S)
A, B, undo = module.synthesize(b, S, et['pole'])

c = b.finish_circuit()
sim = km.Simulator(batch_size=num_shots, seed=42)
sim.use_same_registers_as(c)
sim.write_across_shots(km.array([q for reg in S for q in reg]), to_bits(syndromes, 12))
sim.write_across_shots(km.array([bit for reg in E for bit in reg]), to_bits(mbuc, 12))
sim.do(c)

a_bits = sim.read_across_shots(km.array([q for reg in A for q in reg]))
b_bits = sim.read_across_shots(km.array([q for reg in B for q in reg]))

for shot in range(num_shots):
    a_vals = [int(sum(int(b) << i for i, b in enumerate(word))) for word in a_bits[:, shot].reshape(len(A), 12)]
    b_vals = [int(sum(int(b) << i for i, b in enumerate(word))) for word in b_bits[:, shot].reshape(len(B), 12)]
    print(f"\n--- Shot {shot} ---")
    print(f"True syndromes S[0..8]: {syndromes[shot, :8]}")
    print(f"A values (first 8):      {a_vals[:8]}")
    print(f"B values (first 8):      {b_vals[:8]}")

