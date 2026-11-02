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

spec = ProblemSpecDQI.benchmark_instance()
tables = FieldTables(km.GF2Field(spec.degree))
rng = np.random.default_rng(42)

weight_probs = optimal_dqi_weights(spec.m, spec.max_errors, spec.degree, spec.r) ** 2
syndromes, mbuc, phases = sample_shots(spec, tables, rng, 4, weight_probs)

# Let's test a modified synthesize where we profile the effect of each stage of undo:
def custom_synthesize(b, words, pole, truncate_stages=0):
    heads = [words[2*i:2*i+2] for i in range(34)]
    u, v = words[-2:]
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
    
    def undo():
        ref.folds.ug['reclaim'](b, [border]); b.x(border[0])
        # Only run stages that are NOT truncated:
        for idx, (i, aa, bb, qi, p, t) in enumerate(reversed(hist)):
            if idx < truncate_stages:
                # Truncate this stage: how to free t?
                # t has (hm, fm)
                hm, fm = t
                b.free(hm); b.free(fm)
                continue
            if i % 2:
                ref.folds.ug['absorb'](b, heads[i], aa, bb, qi, p, None, 0, ref.cs[i], ref.ks[i], True, t, False)
                ref.ar.mul_xor0(b, heads[i][1], r, border)
            else:
                ref.folds.ug['absorb_even'](b, heads[i], aa, bb, qi, r, ref.cs[i], ref.ks[i], True, t)
        ref.tail_inplace(b, r, border, d, u, v, pole, True, tt); ref.ar.mul_xor0(b, r, border, d)
        for i in reversed(range(1, 34)):
            qi, target = (r, border) if i % 2 else (border, r)
            ref.folds.add_tail(b, heads[i], qi, d, bool(i % 2)); ref.ar.mul_xor0(b, heads[i][1], qi, target)
        b.cx(r, d); b.x(border[0]); b.cx(r, border); b.cx(border, r); b.free(r)
    return C, A, undo

print("Testing custom synthesize with 0 truncation...")
b0 = km.CircuitBuilder()
S0 = [b0.alloc_qubits(12) for _ in range(70)]
pole0 = b0.alloc_qubits(1)[0]
C0, A0, undo0 = custom_synthesize(b0, S0, pole0, 0)
undo0()
b0.free(pole0)
c0 = b0.finish_circuit()
print(f"Truncate 0: Toffolis={c0.operation_statistics().num_toffoli_like}, live qubits={c0.num_qubits}")
