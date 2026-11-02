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

from dqi.verify_submission_dqi import ProblemSpecDQI, FieldTables, sample_shots, optimal_dqi_weights
from exp.decoder.common import ar, gf

spec = ProblemSpecDQI.benchmark_instance()
tables = FieldTables(km.GF2Field(spec.degree))
rng = np.random.default_rng(42)

weight_probs = optimal_dqi_weights(spec.m, spec.max_errors, spec.degree, spec.r) ** 2
syndromes, mbuc, phases = sample_shots(spec, tables, rng, 10, weight_probs)

field = km.GF2Field(12)

# Berlekamp-Massey in Python to get Lambda and Omega for the test shots:
def berlekamp_massey(S):
    # S has length 70
    # Returns Lambda (degree <= 35) and Omega (degree <= 34)
    C = [1]
    B = [1]
    L = 0
    m = 1
    b_val = 1
    for n in range(len(S)):
        # discrepancy d
        d = S[n]
        for i in range(1, L + 1):
            if i < len(C):
                d = field.add(d, field.mul(C[i], S[n - i]))
        if d == 0:
            m += 1
        elif 2 * L <= n:
            T = list(C)
            inv_b = field.pow(b_val, 4093)
            scale = field.mul(d, inv_b)
            # C = C + scale * x^m * B
            while len(C) < len(B) + m:
                C.append(0)
            for i, coeff in enumerate(B):
                C[i + m] = field.add(C[i + m], field.mul(scale, coeff))
            L = n + 1 - L
            B = T
            b_val = d
            m = 1
        else:
            inv_b = field.pow(b_val, 4093)
            scale = field.mul(d, inv_b)
            while len(C) < len(B) + m:
                C.append(0)
            for i, coeff in enumerate(B):
                C[i + m] = field.add(C[i + m], field.mul(scale, coeff))
            m += 1
    
    # Omega(x) = S(x) * C(x) mod x^70
    Omega = [0] * len(C)
    for i in range(len(Omega)):
        val = 0
        for j in range(i + 1):
            if j < len(C) and (i - j) < len(S):
                val = field.add(val, field.mul(C[j], S[i - j]))
        Omega[i] = val
    return C, Omega

print("Testing Newton LFSR recurrence against real syndromes:")
all_passed = True
for shot_idx in range(10):
    S_orig = syndromes[shot_idx].tolist()
    Lambda, Omega = berlekamp_massey(S_orig)
    
    # Now reconstruct S using Newton LFSR:
    # S_i = Omega_i ^ sum_{j=1}^t Lambda_j * S_{i-j}
    t = len(Lambda) - 1
    S_rec = [0] * 70
    for i in range(70):
        val = Omega[i] if i < len(Omega) else 0
        for j in range(1, min(i, t) + 1):
            val = field.add(val, field.mul(Lambda[j], S_rec[i - j]))
        S_rec[i] = val
    
    match = (S_rec == S_orig)
    if not match:
        all_passed = False
        print(f"Shot {shot_idx}: MISMATCH! deg(Lambda)={t}")
    else:
        print(f"Shot {shot_idx}: EXACT MATCH (deg Lambda = {t})")

print(f"All tests passed: {all_passed}")
