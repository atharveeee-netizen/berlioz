import kickmix as km
import sys
from pathlib import Path

source_dir = Path("build/somejoint_src/blocks/dqi/team-1028-narrow240/source")
sys.path.insert(0, str(source_dir))
sys.path.insert(0, str(source_dir / "playbook/kit/decoder"))
sys.path.insert(0, str(source_dir / "playbook/kit"))
sys.modules['circ'] = km

from final_decoder import decode as ref

for trunc in [0, 5, 10, 15, 20, 25, 30, 33]:
    b = km.CircuitBuilder()
    S = [b.alloc_qubits(12) for _ in range(70)]
    pole = b.alloc_qubits(1)[0]
    
    # Run synthesize
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
    
    # Count forward Toffolis
    c_fwd = b.finish_circuit()
    t_fwd = c_fwd.operation_statistics().num_toffoli_like
    
    # Now continue in another builder to measure remaining undo Toffolis
    b_undo = km.CircuitBuilder()
    # Reclaim border
    b_undo.alloc_qubits(12) # dummy border
    
    stage_toffolis = []
    for idx, (i, aa, bb, qi, p, t) in enumerate(reversed(hist)):
        b_stage = km.CircuitBuilder()
        # Measure 1 stage
        pass
    print(f"Forward Toffolis: {t_fwd}")
    break

