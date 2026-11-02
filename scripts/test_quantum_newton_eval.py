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
rng = np.random.default_rng(42)

weight_probs = optimal_dqi_weights(spec.m, spec.max_errors, spec.degree, spec.r) ** 2
syndromes, mbuc, phases = sample_shots(spec, tables, rng, 1, weight_probs)

b = km.CircuitBuilder()
S = [b.alloc_qubits(12) for _ in range(70)]
E = [b.alloc_bits(12) for _ in range(4095)]

mt = ref.baseline.project(b, S, E)
ref.linear_words(b, S, ref.matrix)
et = ref.extraction(b, S)
A, B, undo = ref.synthesize(b, S, et['pole'])

print(f"Synthesize finished. A has {len(A)} words, B has {len(B)} words.")
# In ref.decode: A is C (35 words), B is A_internal (35 words).
# Let's inspect their values in simulator after synthesis!
c = b.finish_circuit()

sim = km.Simulator(batch_size=1)
sim.use_same_registers_as(c)
input_syndromes = to_bits(syndromes, spec.degree)
sim.write_across_shots(km.array([q for reg in S for q in reg]), input_syndromes)
sim.write_across_shots(km.array([bit for reg in E for bit in reg]), to_bits(mbuc, spec.degree))

sim.do(c)

def read_word(reg):
    bits = sim.read_across_shots(km.array(reg)).flatten()
    return sum(int(bit) << i for i, bit in enumerate(bits))

A_vals = [read_word(w) for w in A]
B_vals = [read_word(w) for w in B]

print(f"A values ({len(A_vals)}): {A_vals[:8]}...")
print(f"B values ({len(B_vals)}): {B_vals[:8]}...")

# What are the degrees of A and B?
deg_A = max((i for i, v in enumerate(A_vals) if v != 0), default=0)
deg_B = max((i for i, v in enumerate(B_vals) if v != 0), default=0)
print(f"Degree of A: {deg_A}")
print(f"Degree of B: {deg_B}")
