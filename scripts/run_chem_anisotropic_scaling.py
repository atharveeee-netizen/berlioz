"""Run anisotropic weight scaling on active chemistry factor to minimize lambda_eff.
SPDX-License-Identifier: Apache-2.0
"""
import sys, time, gc
from dataclasses import replace
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'verifiers'))

from dfthcsos import verify as V

def main():
    chem_dir = ROOT / 'build/ml29_apex/dfthcsos'
    npz_path = chem_dir / 'submission.npz'
    print(f'[*] Loading {npz_path}...')
    with np.load(npz_path, allow_pickle=False) as z:
        factor = {k: np.array(z[k]) for k in z.files}
        
    words, edges = factor['angle_words'], factor['tree_edges']
    brot = int(factor['brot']) if 'brot' in factor else int(words.max()).bit_length()
    base_inputs = V.load_inputs(factor)
    w0 = np.asarray(factor['W'], float)
    H0 = np.asarray(factor['H2_I'], float)
    
    def metrics(sw, sh):
        w = w0 * sw
        inp = replace(base_inputs, w=w, W=H0 * sh - w.sum(axis=1))
        m = V.evaluate_words(inp, words, edges, brot)
        return dict(sw=sw, sh=sh, ok=bool(V.passes_accuracy(m)), lam=float(m['lambda_eff']),
                    e1=float(m['error_1']), e2=float(m['error_2']), gap=float(m['E_gap']))

    t0 = time.time()
    m_base = metrics(1.0, 1.0)
    print(f"[+] Base evaluation in {time.time()-t0:.2f}s: lambda_eff={m_base['lam']:.6f}, e1={1e3*m_base['e1']:.3f} mHa, e2={1e3*m_base['e2']:.3f} mHa, E_gap={m_base['gap']:.6f}, valid={m_base['ok']}")

    print('[*] Exploring coarse grid around (1.0, 1.0)...')
    trials = [m_base]
    grid = np.array([-400, -200, -100, -50, -25, 0, 25, 50, 100, 200, 400], float)
    for x in grid:
        for y in grid:
            if x == 0 and y == 0: continue
            trials.append(metrics(1 + x * 1e-6, 1 + y * 1e-6))
            
    feas = [t for t in trials if t['ok']]
    best = min(feas, key=lambda t: t['lam'])
    print(f"[+] Coarse best: s_W={best['sw']:.9f}, s_H={best['sh']:.9f}, lambda_eff={best['lam']:.6f} (base {m_base['lam']:.6f})")

    # Fine grid
    cx, cy = (best['sw'] - 1) * 1e6, (best['sh'] - 1) * 1e6
    for x in np.linspace(cx - 20, cx + 20, 11):
        for y in np.linspace(cy - 20, cy + 20, 11):
            trials.append(metrics(1 + x * 1e-6, 1 + y * 1e-6))
            
    feas = [t for t in trials if t['ok']]
    best = min(feas, key=lambda t: t['lam'])
    delta_lam = m_base['lam'] - best['lam']
    print(f"[+] Fine best: s_W={best['sw']:.9f}, s_H={best['sh']:.9f}, lambda_eff={best['lam']:.6f}, delta={delta_lam:+.6f}, e2={1e3*best['e2']:.3f} mHa")

    if delta_lam > 1e-7:
        print(f"[★] Found improved weight scaling! Saving updated submission.npz...")
        new_factor = dict(factor)
        new_factor['W'] = w0 * best['sw']
        new_factor['H2_I'] = H0 * best['sh']
        out_npz = chem_dir / 'submission_scaled.npz'
        np.savez(out_npz, **new_factor)
        print(f"[+] Saved {out_npz}")
    else:
        print("[i] Active weights are already optimal under anisotropic scaling.")

if __name__ == '__main__':
    main()
