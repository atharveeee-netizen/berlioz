"""Run rotation calibration on staged invsqrt.kmb circuit.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import gc
import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'verifiers'))
sys.path.insert(0, str(ROOT / 'src/invsqrt'))

import kickmix as km
from invsqrt import verify_submission_invsqrt as IV
import calibrate_rotations as CR

def main():
    spec = IV.ProblemSpecInvSqrt.for_n_p(10)
    inv_path = ROOT / 'build/ml29_apex/invsqrt.kmb'
    print(f'[*] Reading {inv_path}...')
    c_base = km.Circuit.from_file(str(inv_path), format='kmb')
    t0 = time.time()
    rep0 = IV.verify(c_base, spec, max_workers=4)
    score0 = rep0['score']
    print(f'[+] Base verification in {time.time()-t0:.1f}s: score {score0:.3f}, Q {rep0["num_qubits"]}, Toffoli {rep0["toffoli_count"]:.2f}, rotations {rep0.get("rotation_count")}')

    text = str(c_base)
    del c_base
    gc.collect()

    lines, rots = CR.parse_kmx(text)
    counted = [j for j, r in enumerate(rots) if r['counted']]
    print(f'[+] Parsed circuit: {len(rots)} Z_POW gates, {len(counted)} synthesized')

    t0 = time.time()
    print('[*] Simulating all inputs...')
    xs, err, tol, bits, Q = CR.collect(km, IV, spec, text, rots, batch=32768)
    print(f'[+] Simulation over all {len(xs):,} inputs completed in {time.time()-t0:.1f}s')

    t0 = time.time()
    rows = CR.search(err, tol, bits, rots, rep0, IV.rotation_t_count, max_drop=8)
    print(f'[+] Search completed in {time.time()-t0:.1f}s')
    for r in rows:
        print(f'  Drop {r["drop"]}: margin={r["margin"]:.4g}, estimated={r["estimate"]:.3f}, fitted={r["fitted"]}')

    base_est = rows[0]['estimate']
    best = min((r for r in rows if r['fitted'] and r['margin'] > 0), key=lambda r: r['estimate'], default=None)
    if best is None or best['estimate'] >= base_est:
        print('[-] No candidate beats baseline estimate.')
    else:
        print(f'[+] Found better candidate: drop {best["drop"]}, margin {best["margin"]:.4g}, estimated {best["estimate"]:.3f} (base: {base_est:.3f})')
        deltas = {j: int(v) for j, v in enumerate(best['deltas']) if j not in best['dropped']}
        new_text = CR.rewrite(lines, rots, deltas, set(best['dropped']))
        cand_path = ROOT / 'build/ml29_apex/invsqrt_cal.kmb'
        cand_c = km.Circuit(new_text)
        cand_c.to_file(str(cand_path), format='kmb')
        print(f'[+] Saved candidate to {cand_path}')

        t0 = time.time()
        rep_cand = IV.verify(cand_c, spec, max_workers=4)
        print(f'[+] Verification of calibrated circuit ({time.time()-t0:.1f}s): {rep_cand["status"]} score {rep_cand["score"]:.3f}')
        if rep_cand['status'] == 'PASS' and rep_cand['score'] < score0:
            print(f'[★] SUCCESS! Calibrated invsqrt reduced score: {score0:.3f} -> {rep_cand["score"]:.3f} (gain: {score0 - rep_cand["score"]:.3f})')
        else:
            print('[-] Did not beat base verified score.')

if __name__ == '__main__':
    main()
