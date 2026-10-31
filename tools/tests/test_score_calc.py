#!/usr/bin/env python3
"""
tools/tests/test_score_calc.py — Strict Unit Tests for Canonical Scorer (Chunk C0 Gate)
"""

import math
import sys
import os

# Add parent directory to path so tools module can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from tools.score_calc import (
    composite,
    R_eps_plus,
    repetition_factor,
    R,
    dqi_cost,
    invsqrt_cost,
    chem_cost,
    breakeven_dT,
    exchange_rates,
    failure_price_table,
)


def test_reproduction_constants():
    # 1. Must reproduce R(0) = 1.19126046
    eps_0 = R_eps_plus(0)
    r_0 = R(0)
    assert abs(r_0 - 1.19126046) < 1e-7, f"R(0) mismatch: {r_0}"

    # 2. Must reproduce R_eps_plus(k=1) = 9.1042e-4
    eps_1 = R_eps_plus(1)
    assert abs(eps_1 - 9.1042e-4) < 1e-6, f"eps_1 mismatch: {eps_1}"

    # 3. Must reproduce S = 23.060808 from ML16 inputs
    # R_inv = 20.64208447, R_dqi = 59.8423, R_chem = 9.9280
    s_ml16 = composite(20.64208447, 59.8423, 9.9280)
    assert abs(s_ml16 - 23.060808) < 1e-6, f"s_ml16 mismatch: {s_ml16}"


def test_failure_price_table():
    # 4. Must reproduce k=0..1000 failure-price table
    table = failure_price_table([0, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000])
    table_dict = {row["k"]: row["cost_penalty_pct"] for row in table}

    # Verified penalty increments vs k=0
    assert abs(table_dict[0] - 0.0) < 1e-5
    assert 0.40 < table_dict[1] < 0.50, f"k=1 penalty: {table_dict[1]}"
    assert 0.80 < table_dict[2] < 0.90, f"k=2 penalty: {table_dict[2]}"
    assert 1.70 < table_dict[5] < 1.95, f"k=5 penalty: {table_dict[5]}"
    assert 3.00 < table_dict[10] < 3.35, f"k=10 penalty: {table_dict[10]}"
    assert 5.00 < table_dict[20] < 5.60, f"k=20 penalty: {table_dict[20]}"
    assert 9.50 < table_dict[50] < 11.00, f"k=50 penalty: {table_dict[50]}"
    assert 15.50 < table_dict[100] < 17.50, f"k=100 penalty: {table_dict[100]}"
    assert 25.00 < table_dict[200] < 28.50, f"k=200 penalty: {table_dict[200]}"


def test_breakeven_and_exchange():
    dt_880 = breakeven_dT(889, 880, 427471.2)
    assert 8500.0 < dt_880 < 9000.0

    rates = exchange_rates()
    assert "score_gain_per_1pct_single_ratio" in rates
    assert rates["score_gain_per_1pct_single_ratio"] > 0.07


if __name__ == "__main__":
    test_reproduction_constants()
    test_failure_price_table()
    test_breakeven_and_exchange()
    print("ALL tests in test_score_calc.py PASSED (Gate C0 Green).")
