"""Unit tests for the authoritative score engine (Masterloop 20 Phase 2).
Verifies Clopper-Pearson bounds, repetition factors, cost formulas, and composite score geometric mean.
SPDX-License-Identifier: Apache-2.0
"""
import unittest
import math
from research.masterloop20.score_engine import (
    clopper_pearson_upper_bound,
    repetition_factor,
    compute_dqi_cost,
    compute_invsqrt_cost,
    compute_chem_cost,
    compute_composite_score,
    AuthoritativeScoreEngine,
    C_INVSQRT_REF,
    C_DQI_REF,
    C_CHEM_REF,
)


class TestScoreEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AuthoritativeScoreEngine()

    def test_clopper_pearson_zero_failures(self):
        # 102,400 shots, delta = 2^-128
        eps = clopper_pearson_upper_bound(0, 102400)
        self.assertAlmostEqual(eps, 8.6605873e-4, places=10)

    def test_repetition_factor_zero_failures(self):
        eps = clopper_pearson_upper_bound(0, 102400)
        r = repetition_factor(eps)
        self.assertAlmostEqual(r, 1.19126046, places=8)

    def test_invsqrt_cost_formula(self):
        c = compute_invsqrt_cost(qubits=62, t_equiv=1622.72)
        self.assertAlmostEqual(c, 100608.64, places=2)

    def test_chem_cost_formula(self):
        c = compute_chem_cost(qubits=430, toffolis=16266.0, lambda_eff=48.2992)
        self.assertAlmostEqual(c, 337822958.496, places=2)

    def test_dqi_cost_formula(self):
        c, eps, r = compute_dqi_cost(qubits=889, t_mean=427471.2, k=0, n_shots=102400)
        expected = r * (889 ** 2) * 427471.2
        self.assertAlmostEqual(c, expected, places=4)

    def test_composite_score_reproduction(self):
        inv_m = {"qubits": 62, "t_equiv": 1622.72030097}
        dqi_m = {"qubits": 889, "t_mean": 427471.2, "failures": 0, "shots": 102400}
        chem_m = {"qubits": 430, "toffolis": 16266.0, "lambda_eff": 48.29920925}
        res = self.engine.evaluate_portfolio(inv_m, dqi_m, chem_m)
        self.assertAlmostEqual(res["composite_score"], 23.17767, places=4)

    def test_reject_missing_metrics(self):
        inv_m = {"qubits": 62}  # Missing t_equiv
        dqi_m = {"qubits": 889, "t_mean": 427471.2}
        chem_m = {"qubits": 430, "toffolis": 16266.0, "lambda_eff": 48.2992}
        with self.assertRaises(KeyError):
            self.engine.evaluate_portfolio(inv_m, dqi_m, chem_m)


if __name__ == "__main__":
    unittest.main()
