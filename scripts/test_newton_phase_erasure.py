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
syndromes, mbuc, phases = sample_shots(spec, tables, rng, 2, weight_probs)

print("Testing Newton phase erasure concept...")
# Let's inspect the exact list of measurement bits in synthesize:
b = km.CircuitBuilder()
S = [b.alloc_qubits(12) for _ in range(70)]
pole = b.alloc_qubits(1)[0]

heads = [S[2*i:2*i+2] for i in range(34)]
u, v = S[-2:]
d, border = heads[0]
r = b.alloc_qubits(12)
b.cx(border, r); b.cx(border, d); b.cx(r, border); b.x(border[0])
for i in range(1, 34):
    qi, target = (r, border) if i % 2 else (border, r)
    ref.ar.mul_xor0(b, heads[i][1], qi, target)
    ref.folds.add_tail(b, heads[i], qi, d, bool(i % 2))
ref.ar.mul_xor0(b, r, border, d)
tt = ref.tail_inplace(b, r, border, d, u, v, pole)

A, B, hist = [u, v], [d], []
for i in reversed(range(1, 34)):
    aa, bb = A, B
    if i % 2:
        ref.ar.mul_xor0(b, heads[i][1], r, border); qi, p = r, border
        A, B, t = ref.folds.sg['absorb'](b, heads[i], A, B, qi, p, None, 0, ref.cs[i], ref.ks[i], wide=False)
    else:
        qi, p = border, r
        A, B, t = ref.folds.sg['absorb_even'](b, heads[i], A, B, qi, r, ref.cs[i], ref.ks[i])
    hist.append((i, aa, bb, qi, p, t))
b.x(border[0]); b.free(border); C = B + [r]

print(f"Synthesize forward completed! Hist has {len(hist)} stages.")
# For each stage in hist, t has (hm, fm):
total_bits = 0
for i, aa, bb, qi, p, t in hist:
    hm, fm = t
    total_bits += len(hm) + len(fm)
print(f"Total measurement bits stored in hist: {total_bits}")

