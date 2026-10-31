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
  - Failure-price table generation across k failures
  - Built-in test suite
"""

import math
import sys
from typing import Dict, Any, List, Tuple
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
    at significance level delta (confidence 1 - delta, with delta = 2^-128).
    
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
        return float(beta.isf(delta, k + 1, n - k))


def R_eps_plus(k: int, N: int = DEFAULT_SHOTS_DQI, delta: float = DELTA_CONFIDENCE) -> float:
    """Canonical alias for Clopper-Pearson failure probability upper bound."""
    return clopper_pearson_upper_bound(k, N, delta)


def repetition_factor(eps_plus: float) -> float:
    """
    Computes repetition overhead factor R(eps+):
      R(eps+) = ln(2) / [ -ln( 1/2 + 2 * sqrt(eps+) ) ]
    """
    arg = 0.5 + 2.0 * math.sqrt(eps_plus)
    if arg >= 1.0:
        return float("inf")
    return math.log(2.0) / (-math.log(arg))


def R(k: int, N: int = DEFAULT_SHOTS_DQI, delta: float = DELTA_CONFIDENCE) -> float:
    """Computes R(eps+(k)) repetition penalty factor directly for k failures."""
    return repetition_factor(R_eps_plus(k, N, delta))


def dqi_cost(qubits: int, t_mean: float, k: int = 0, n_shots: int = DEFAULT_SHOTS_DQI) -> float:
    """
    Computes DQI candidate cost:
      Cost_DQI = R(eps+) * Q^2 * T_mean
    """
    eps_plus = R_eps_plus(k, n_shots)
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


def composite(r_inv: float, r_dqi: float, r_chem: float) -> float:
    """
    Computes composite geometric-mean score:
      S = (R_inv * R_dqi * R_chem)^(1/3)
    """
    return (r_inv * r_dqi * r_chem) ** (1.0 / 3.0)


def composite_score(r_inv: float, r_dqi: float, r_chem: float) -> float:
    """Alias for composite()."""
    return composite(r_inv, r_dqi, r_chem)


def composite_from_costs(c_inv: float, c_dqi: float, c_chem: float) -> float:
    """Computes composite score directly from candidate costs."""
    r_inv = C_INVSQRT_REF / c_inv
    r_dqi = C_DQI_REF / c_dqi
    r_chem = C_CHEM_REF / c_chem
    return composite(r_inv, r_dqi, r_chem)


def breakeven_dT(q_old: int, q_new: int, t_old: float) -> float:
    """
    Computes maximum allowable increase in Toffolis (delta_T_max) when reducing
    register width from q_old to q_new in DQI, such that cost does not increase:
      dT_max = T_old * [ (Q_old / Q_new)^2 - 1 ]
    """
    ratio_sq = (float(q_old) / float(q_new)) ** 2
    return t_old * (ratio_sq - 1.0)


def exchange_rates(
    qubits_dqi: int = 889,
    t_dqi: float = 427471.2,
    k_dqi: int = 0,
    q_inv: int = 62,
    t_inv: float = 1622.7,
    q_chem: int = 430,
    t_chem: float = 16266.0,
    lambda_chem: float = 48.2992,
) -> Dict[str, Any]:
    """Calculates canonical exchange rates and marginal prices across all benchmarks."""
    c_inv = invsqrt_cost(q_inv, t_inv)
    c_dqi = dqi_cost(qubits_dqi, t_dqi, k_dqi)
    c_chem = chem_cost(q_chem, t_chem, lambda_chem)
    s = composite_from_costs(c_inv, c_dqi, c_chem)

    delta_s_per_pct = s * ((1.01 ** (1.0 / 3.0)) - 1.0)
    return {
        "current_composite": s,
        "score_gain_per_1pct_single_ratio": delta_s_per_pct,
        "dqi_1_qubit_toffoli_equiv": (2.0 / qubits_dqi) * t_dqi,
        "dqi_break_even_889_to_880": breakeven_dT(qubits_dqi, 880, t_dqi),
        "dqi_break_even_889_to_860": breakeven_dT(qubits_dqi, 860, t_dqi),
        "dqi_break_even_889_to_840": breakeven_dT(qubits_dqi, 840, t_dqi),
        "dqi_break_even_889_to_740": breakeven_dT(qubits_dqi, 740, t_dqi),
        "invsqrt_1_qubit_toffoli_equiv": t_inv,
        "chem_1_qubit_toffoli_equiv": t_chem * (1.0 / q_chem),
    }


def failure_price_table(k_values: List[int] = [0, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]) -> List[Dict[str, Any]]:
    """Generates failure penalty table for DQI across error counts k."""
    r0 = R(0)
    table = []
    for k in k_values:
        eps = R_eps_plus(k)
        rk = repetition_factor(eps)
        pct_increase = ((rk / r0) - 1.0) * 100.0
        table.append({
            "k": k,
            "eps_plus": eps,
            "R_factor": rk,
            "cost_penalty_pct": pct_increase,
        })
    return table


def run_tests():
    """Validates the canonical scoring module against all established mathematical truths."""
    print("[*] Running score_calc.py test suite...")

    # 1. Test k=0 Clopper-Pearson bound
    eps_0 = R_eps_plus(0)
    expected_eps_0 = 8.660587301657926e-4
    assert abs(eps_0 - expected_eps_0) < 1e-9, f"eps_0 mismatch: got {eps_0}, expected {expected_eps_0}"

    # 2. Test k=0 Repetition factor R(0)
    r_0 = repetition_factor(eps_0)
    expected_r_0 = 1.1912604648115832
    assert abs(r_0 - expected_r_0) < 1e-8, f"R(0) mismatch: got {r_0}, expected {expected_r_0}"

    # 3. Test k=1 Clopper-Pearson bound
    eps_1 = R_eps_plus(1)
    assert 9.10e-4 < eps_1 < 9.11e-4, f"eps_1 mismatch: got {eps_1}, expected ~9.1042e-4"

    # 4. Test baseline composite reproduction (23.060808)
    s_ml16 = composite(20.64208447, 59.8423, 9.9280)
    assert abs(s_ml16 - 23.060808) < 1e-5, f"s_ml16 mismatch: got {s_ml16}, expected 23.060808"

    # 5. Test new SOTA composite reproduction (23.17767)
    c_inv_sota = invsqrt_cost(62, 1622.72030097)
    c_dqi_sota = dqi_cost(889, 427471.2, 0)
    c_chem_sota = chem_cost(430, 16266.0, 48.29920925)
    s_sota = composite_from_costs(c_inv_sota, c_dqi_sota, c_chem_sota)
    assert abs(s_sota - 23.17767) < 1e-3, f"s_sota mismatch: got {s_sota}"

    print("[+] ALL score_calc.py TESTS PASSED!")
    print(f"    R(0) = {r_0:.8f}")
    print(f"    eps+(k=0) = {eps_0:.8e}")
    print(f"    eps+(k=1) = {eps_1:.8e}")
    print(f"    ML16 Composite S = {s_ml16:.6f}")
    print(f"    Certified SOTA Composite S = {s_sota:.5f}")


if __name__ == "__main__":
    run_tests()
    rates = exchange_rates()
    print("\n[*] Canonical Exchange Rates:")
    for k, v in rates.items():
        print(f"    {k}: {v}")
