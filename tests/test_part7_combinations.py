"""Unit tests for ML26 Part 7: Cross-Direction Combinations & Interaction Analysis.

Authors: BERLIOZ Discovery Agent
Context: BERLIOZ MASTERLOOP 26 - PART 7
Date: 2026-10-31
"""

import math
from pathlib import Path
import sys
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ml26.combination_evaluator import CrossDirectionEvaluator, CombinationResult


class TestCrossDirectionCombinations(unittest.TestCase):
    """Rigorous test suite for ML26 Part 7 combinations."""

    @classmethod
    def setUpClass(cls):
        cls.evaluator = CrossDirectionEvaluator()
        cls.results = {r.combination_id: r for r in cls.evaluator.run_all()}

    def test_all_ten_combinations_evaluated(self):
        """Ensure all 10 required combinations are present."""
        expected_ids = [f"COMB-{i:02d}" for i in range(1, 11)]
        self.assertEqual(sorted(self.results.keys()), sorted(expected_ids))

    def test_incompatible_combinations_rejected(self):
        """Verify that fundamentally incompatible combinations are rejected/disqualified."""
        # COMB-04: Additive FFT + MBUC (Bilinear non-Clifford phase kickback)
        c4 = self.results["COMB-04"]
        self.assertEqual(c4.compatibility, "MATHEMATICALLY_INCOMPATIBLE")
        self.assertEqual(c4.semantic_status, "FAIL")
        self.assertEqual(c4.compilation_status, "REJECTED_PHASE_DRIFT")
        self.assertTrue(math.isinf(c4.total_cost))

        # COMB-05: Projective Decoding + Pebbling (Non-unitary collapse)
        c5 = self.results["COMB-05"]
        self.assertEqual(c5.compatibility, "MATHEMATICALLY_INCOMPATIBLE")
        self.assertEqual(c5.semantic_status, "FAIL")
        self.assertEqual(c5.compilation_status, "REJECTED_REVERSIBILITY")
        self.assertTrue(math.isinf(c5.total_cost))

        # COMB-06: R=10 + 5-Word QROM (Q=135 > 128 hard cap)
        c6 = self.results["COMB-06"]
        self.assertEqual(c6.compatibility, "PHYSICALLY_INCOMPATIBLE")
        self.assertEqual(c6.semantic_status, "REJECTED")
        self.assertEqual(c6.compilation_status, "REJECTED_PHYSICAL_LIMIT")
        self.assertEqual(c6.qubits, 135)
        self.assertGreater(c6.qubits, 128)
        self.assertTrue(math.isinf(c6.total_cost))

        # COMB-09: Invsqrt Estrin (Q=86 > 64 hard ceiling)
        c9 = self.results["COMB-09"]
        self.assertEqual(c9.compatibility, "REVERSIBLY_INCOMPATIBLE")
        self.assertEqual(c9.qubits, 86)
        self.assertGreater(c9.qubits, 64)

    def test_superadditive_synergistic_combinations(self):
        """Verify successful superadditive combinations."""
        # COMB-08: Chem 5-word + ANF
        c8 = self.results["COMB-08"]
        self.assertEqual(c8.compatibility, "FULLY_COMPATIBLE")
        self.assertEqual(c8.compilation_status, "COMPILED_OK")
        self.assertLessEqual(c8.qubits, 430)
        self.assertAlmostEqual(c8.measured_combined_ratio, 9.93301, places=3)
        self.assertEqual(c8.coupling_type, "SUPERADDITIVE")

        # COMB-10: Invsqrt Lawson + Workspace Reclamation
        c10 = self.results["COMB-10"]
        self.assertEqual(c10.compatibility, "FULLY_COMPATIBLE")
        self.assertEqual(c10.compilation_status, "COMPILED_OK")
        self.assertEqual(c10.qubits, 58)
        self.assertGreater(c10.measured_combined_ratio, 22.0)
        self.assertEqual(c10.coupling_type, "SUPERADDITIVE")

    def test_subadditive_combinations_measured(self):
        """Verify that subadditive combinations are properly measured and not summed."""
        # COMB-01: RiBM + Projective
        c1 = self.results["COMB-01"]
        self.assertEqual(c1.coupling_type, "SUBADDITIVE")
        self.assertLess(c1.measured_combined_ratio, 1.0)
        self.assertLess(c1.measured_combined_ratio, c1.projected_independent_ratio)

        # COMB-02: RiBM + Additive FFT
        c2 = self.results["COMB-02"]
        self.assertEqual(c2.coupling_type, "CATASTROPHICALLY_SUBADDITIVE")
        self.assertLess(c2.measured_combined_ratio, 10.0)
        self.assertLess(c2.measured_combined_ratio, c2.projected_independent_ratio)

        # COMB-03: RiBM + Pebbling (In-Place Dominance: Q=1120 > 918)
        c3 = self.results["COMB-03"]
        self.assertEqual(c3.qubits, 1120)
        self.assertGreater(c3.qubits, 918)

        # COMB-07: Chem R=10 Truncated
        c7 = self.results["COMB-07"]
        self.assertEqual(c7.compilation_status, "COMPILED_OK")
        self.assertLessEqual(c7.qubits, 431)
        self.assertLess(c7.measured_combined_ratio, 9.933)  # Less than R=8 champion

    def test_anti_additive_law(self):
        """Verify that naive independent projected savings are NOT naively achieved."""
        for cid, res in self.results.items():
            if res.coupling_type in ("SUBADDITIVE", "CATASTROPHICALLY_SUBADDITIVE", "INCOMPATIBLE"):
                self.assertLess(
                    res.measured_combined_ratio,
                    res.projected_independent_ratio,
                    f"Combination {cid} violated anti-additive check: measured {res.measured_combined_ratio} >= projected {res.projected_independent_ratio}"
                )


if __name__ == "__main__":
    unittest.main()
