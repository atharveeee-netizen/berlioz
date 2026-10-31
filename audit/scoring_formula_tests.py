#!/usr/bin/env python3
"""Stage 2: Reconstruct exact competition scoring contract and test Clopper-Pearson penalties.
SPDX-License-Identifier: Apache-2.0
"""
import sys, math, json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'verifiers')]

from dqi.verify_submission_dqi import clopper_pearson_upper_bound, repetition_overhead, DEFAULT_LOG2_DELTA, DEFAULT_NUM_SHOTS
from invsqrt.verify_submission_invsqrt import rotation_t_count, T_PER_TOFFOLI

REF_COST_INVSQRT = 2076774.233715282
REF_COST_DQI = 24439463583672.93
REF_COST_CHEM = 3355599588.3155365

def test_clopper_pearson():
    n_shots = DEFAULT_NUM_SHOTS  # 102,400
    results = {}
    print(f"[*] Testing Clopper-Pearson confidence penalty at N={n_shots:,}, log2_delta={DEFAULT_LOG2_DELTA}")
    for k in [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 15, 20]:
        eps_plus = clopper_pearson_upper_bound(k, n_shots, log2_delta=DEFAULT_LOG2_DELTA)
        R_k = repetition_overhead(eps_plus)
        results[k] = {
            "failed_shots": k,
            "total_shots": n_shots,
            "empirical_rate": k / n_shots,
            "eps_plus": eps_plus,
            "repetition_factor": R_k
        }
        print(f"    k={k:2d}: eps_plus={eps_plus:.6e} | R(k)={R_k:.8f}")
    
    with open(ROOT / 'audit/confidence_penalty_tests.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[+] Saved audit/confidence_penalty_tests.json")
    return results

def test_score_decomposition(observed_score: float = 22.80575):
    """Decomposes the observed score 22.80575 into exact possible component combinations."""
    print(f"\n[*] Decomposing observed score: {observed_score}")
    target_cube = observed_score ** 3
    print(f"    Target Ratio Product (Score^3): {target_cube:.5f}")
    
    # Measured components:
    # Invsqrt 63Q (89,223.75 cost -> ratio 23.27602)
    # Chemistry R=8 B143 C60 (337,993,966.88 cost -> ratio 9.927986)
    ratio_inv_63 = REF_COST_INVSQRT / 89223.75
    ratio_chem_r8 = REF_COST_CHEM / 337993966.8794745
    
    implied_dqi_ratio = target_cube / (ratio_inv_63 * ratio_chem_r8)
    implied_dqi_cost = REF_COST_DQI / implied_dqi_ratio
    
    # In DQI 889Q, mean T = 433,785.6
    q = 889
    mean_t = 433785.5742
    raw_qt = (q ** 2) * mean_t
    
    implied_R = implied_dqi_cost / raw_qt
    print(f"    Ratio Invsqrt (63Q): {ratio_inv_63:.5f}x")
    print(f"    Ratio Chem (R=8):    {ratio_chem_r8:.5f}x")
    print(f"    Implied DQI Ratio:   {implied_dqi_ratio:.5f}x")
    print(f"    Implied DQI Cost:    {implied_dqi_cost:,.2f}")
    print(f"    Raw Q^2 * T:         {raw_qt:,.2f}")
    print(f"    Implied Repetition R: {implied_R:.5f}")
    
    # Now check: what if Invsqrt was 62Q (ratio 22.2530) or baseline?
    ratio_inv_62 = REF_COST_INVSQRT / 93325.50
    implied_dqi_ratio_62 = target_cube / (ratio_inv_62 * ratio_chem_r8)
    implied_R_62 = (REF_COST_DQI / implied_dqi_ratio_62) / raw_qt
    print(f"\n    With 62Q Invsqrt (22.253x):")
    print(f"    Implied DQI Ratio:   {implied_dqi_ratio_62:.5f}x")
    print(f"    Implied Repetition R: {implied_R_62:.5f}")

if __name__ == '__main__':
    test_clopper_pearson()
    test_score_decomposition()
