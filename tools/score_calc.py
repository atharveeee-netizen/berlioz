#!/usr/bin/env python3
"""
tools/score_calc.py — Canonical Scoring and Cost Model for Verifiable Quantum Circuit Compilation
==================================================================================================
Implements:
  - Exact reference costs from the competition evaluation harness
  - Clopper-Pearson one-sided confidence upper bound on binomial error rate at delta = 2^-128
  - Repetition overhead factor R(eps+)
  - Composite geometric mean score S = (R_inv * R_dqi * R_chem)^(1/3)
  - Marginal exchange rates and break-even calculations (breakeven_dT)
  - Built-in test suite
"""

import math
import sys
from scipy.stats import beta

# Canonical Official Reference Costs (Verified from official_eval/evaluator.py)
C_INVSQRT_REF = 2076774.233715282
C_DQI_REF = 24439463583672.93
C_CHEM_REF = 3355599588.3155365

DEFAULT_SHOTS_DQI = 102400
DELTA_CONFIDENCE = 2.0 ** -128  # log2(delta) = -128


def clopper_pearson_upper_bound(k: int, n: int = DEFAULT_SHOTS_DQI, delta: float = DELTA_CONFIDENCE) -> float:
    """
    Computes the exact one-sided Clopper-Pearson upper confidence bound on binomial p
    at significance level delta (i.e. confidence 1 - delta, with delta = 2^-128).
    
    For k failures in n trials:
      If k == 0: eps+ = 1 - delta^(1/n)
      If k > 0:  eps+ is the (1 - delta) quantile of Beta(k + 1, n - k)
    """
    if k < 0 or n <= 0:
        raise ValueError("k must be non-negative and n must be positive.")
    if k == 0:
        return 1.0 - (delta ** (1.0 / n))
    else:
        # Survival function / PPF of Beta distribution: quantile 1 - delta
        # Since delta is tiny (~2.9387e-39), we use beta.isf(delta, k + 1, n - k)
        return float(beta.isf(delta, k + 1, n - k))


def repetition_factor(eps_plus: float) -> float:
    """
    Computes repetition overhead factor R(eps+):
      R(eps+) = ln(2) / [ -ln( 1/2 + 2 * sqrt(eps+) ) ]
    """
    arg = 0.5 + 2.0 * math.sqrt(eps_plus)
    if arg >= 1.0:
        return float("inf")
    return math.log(2.0) / (-math.log(arg))


def dqi_cost(qubits: int, t_mean: float, k_failures: int = 0, n_shots: int = DEFAULT_SHOTS_DQI) -> float:
    """
    Computes DQI candidate cost:
      Cost_DQI = R(eps+) * Q^2 * T_mean
    """
    eps_plus = clopper_pearson_upper_bound(k_failures, n_shots)
    r_factor = repetition_factor(eps_plus)
    return r_factor * (qubits ** 2) * t_mean


def invsqrt_cost(qubits: int, t_equiv: float) -> float:
    """
    Computes Invsqrt candidate cost:
      Cost_inv = Q * T_equiv
    """
    return float(qubits * t_equiv)


def chem_cost(qubits: int, toffolis: float, lambda_eff: float) -> float:
    """
    Computes Chemistry candidate cost:
      Cost_chem = lambda_eff * Q_total * T_total
    """
    return float(lambda_eff * qubits * toffolis)


def composite_score(r_inv: float, r_dqi: float, r_chem: float) -> float:
    """
    Computes composite geometric-mean score:
      S = (R_inv * R_dqi * R_chem)^(1/3)
    """
    return (r_inv * r_dqi * r_chem) ** (1.0 / 3.0)


def composite_from_costs(c_inv: float, c_dqi: float, c_chem: float) -> float:
    """Computes composite score directly from candidate costs."""
    r_inv = C_INVSQRT_REF / c_inv
    r_dqi = C_DQI_REF / c_dqi
    r_chem = C_CHEM_REF / c_chem
    return composite_score(r_inv, r_dqi, r_chem)


def breakeven_dT(q_old: int, q_new: int, t_old: float) -> float:
    """
    Computes the maximum allowable increase in Toffolis (delta_T_max) when reducing
    register width from q_old to q_new in DQI, such that cost does not increase:
      dT_max = T_old * [ (Q_old / Q_new)^2 - 1 ]
    """
    ratio_sq = (float(q_old) / float(q_new)) ** 2
    return t_old * (ratio_sq - 1.0)


def exchange_rates_summary(current_s: float = 23.17767):
    """
    Returns marginal exchange rates:
    - +1% on any ratio = +0.333% on score (about +0.077 score points at S=23.18)
    - DQI: 1 qubit ~= 976 Toffolis ~= 0.225% cost
    """
    delta_s_per_pct = current_s * ((1.01 ** (1.0 / 3.0)) - 1.0)
    return {
        "current_composite": current_s,
        "score_gain_per_1pct_single_ratio": delta_s_per_pct,
        "dqi_break_even_889_to_880": breakeven_dT(889, 880, 427471.2),
        "dqi_break_even_889_to_860": breakeven_dT(889, 860, 427471.2),
        "dqi_break_even_889_to_840": breakeven_dT(889, 840, 427471.2),
        "dqi_break_even_889_to_740": breakeven_dT(889, 740, 427471.2),
    }


def run_tests():
    """Validates the canonical scoring module against all established mathematical truths."""
    print("[*] Running score_calc.py test suite...")
    
    # 1. Test k=0 Clopper-Pearson bound
    eps_0 = clopper_pearson_upper_bound(0, DEFAULT_SHOTS_DQI)
    expected_eps_0 = 8.660587301657926e-4
    assert abs(eps_0 - expected_eps_0) < 1e-9, f"eps_0 mismatch: got {eps_0}, expected {expected_eps_0}"
    
    # 2. Test k=0 Repetition factor R(0)
    r_0 = repetition_factor(eps_0)
    expected_r_0 = 1.1912604648115832
    assert abs(r_0 - expected_r_0) < 1e-8, f"R(0) mismatch: got {r_0}, expected {expected_r_0}"
    
    # 3. Test k=1 Clopper-Pearson bound
    eps_1 = clopper_pearson_upper_bound(1, DEFAULT_SHOTS_DQI)
    assert 9.10e-4 < eps_1 < 9.11e-4, f"eps_1 mismatch: got {eps_1}, expected ~9.1042e-4"
    
    # 4. Test baseline composite reproduction (23.06062 / 23.0608)
    # Using baseline values
    c_inv_base = 62 * 1622.7203009737732
    c_dqi_base = r_0 * (889 ** 2) * 433794.0703125
    c_chem_base = 48.323649398441965 * 430 * 16266.0
    s_base = composite_from_costs(c_inv_base, c_dqi_base, c_chem_base)
    assert abs(s_base - 23.06061967) < 1e-4, f"s_base mismatch: got {s_base}"
    
    # 5. Test new SOTA composite reproduction (23.17767)
    c_dqi_sota = r_0 * (889 ** 2) * 427471.2
    c_chem_sota = 48.299209254045124 * 430 * 16266.0
    s_sota = composite_from_costs(c_inv_base, c_dqi_sota, c_chem_sota)
    assert abs(s_sota - 23.17767) < 1e-3, f"s_sota mismatch: got {s_sota}"
    
    # 6. Test breakeven dT
    dt_880 = breakeven_dT(889, 880, 433794.0)
    assert 8800.0 < dt_880 < 9200.0, f"dt_880 mismatch: {dt_880}"
    
    print("[+] ALL score_calc.py TESTS PASSED!")
    print(f"    R(0) = {r_0:.8f}")
    print(f"    eps+(k=0) = {eps_0:.8e}")
    print(f"    eps+(k=1) = {eps_1:.8e}")
    print(f"    Baseline Composite = {s_base:.5f}")
    print(f"    Certified SOTA Composite = {s_sota:.5f}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        run_tests()
        rates = exchange_rates_summary()
        print("\n[*] Canonical Exchange Rates:")
        for k, v in rates.items():
            print(f"    {k}: {v}")
