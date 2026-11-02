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

field = km.GF2Field(12)

# Berlekamp-Massey in python to get exact Lambda and Omega for this shot:
def berlekamp_massey(S):
    C = [1]; B = [1]; L = 0; m = 1; b_val = 1
    for n in range(len(S)):
        d = S[n]
        for i in range(1, L + 1):
            if i < len(C): d = field.add(d, field.mul(C[i], S[n - i]))
        if d == 0: m += 1
        elif 2 * L <= n:
            T = list(C); inv_b = field.pow(b_val, 4093); scale = field.mul(d, inv_b)
            while len(C) < len(B) + m: C.append(0)
            for i, coeff in enumerate(B): C[i + m] = field.add(C[i + m], field.mul(scale, coeff))
            L = n + 1 - L; B = T; b_val = d; m = 1
        else:
            inv_b = field.pow(b_val, 4093); scale = field.mul(d, inv_b)
            while len(C) < len(B) + m: C.append(0)
            for i, coeff in enumerate(B): C[i + m] = field.add(C[i + m], field.mul(scale, coeff))
            m += 1
    Omega = [0] * len(C)
    for i in range(len(Omega)):
        val = 0
        for j in range(i + 1):
            if j < len(C) and (i - j) < len(S): val = field.add(val, field.mul(C[j], S[i - j]))
        Omega[i] = val
    return C, Omega

Lambda_expected, Omega_expected = berlekamp_massey(syndromes[0].tolist())
print(f"BM Lambda ({len(Lambda_expected)}): {Lambda_expected[:6]}")
print(f"BM Omega ({len(Omega_expected)}): {Omega_expected[:6]}")

# Now build circuit up to unconvert
b = km.CircuitBuilder()
S = [b.alloc_qubits(12) for _ in range(70)]
E = [b.alloc_bits(12) for _ in range(4095)]

mt = ref.baseline.project(b, S, E)
ref.linear_words(b, S, ref.matrix)
et = ref.extraction(b, S)
A, B, undo = ref.synthesize(b, S, et['pole'])
ct = ref.convert_safe(b, A, B, monic_root=True)
ref.baseline.scan(b, A, B, E, skip_points=ref.baseline.SELECTED, node_polynomial=ref.Pscan)
ref.convert_safe(b, A, B, True, phase_token=ct)

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

print(f"Circuit A ({len(A_vals)} words): {A_vals[:6]}")
print(f"Circuit B ({len(B_vals)} words): {B_vals[:6]}")

