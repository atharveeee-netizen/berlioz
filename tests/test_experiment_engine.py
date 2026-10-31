"""Unit tests for the Masterloop 20 Experiment Engine.
Verifies candidate evaluation, ledger recording, promotion rules, and vault preservation.
SPDX-License-Identifier: Apache-2.0
"""
import unittest
import tempfile
import json
from pathlib import Path
from research.masterloop20.experiment_engine import ExperimentEngine


class TestExperimentEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)
        # Create minimal incumbent_metrics.json
        ml20 = self.workspace / "research" / "masterloop20"
        ml20.mkdir(parents=True, exist_ok=True)
        with open(ml20 / "incumbent_metrics.json", "w") as f:
            json.dump({
                "scores": {"official_composite_score": 23.17767},
                "candidate_metrics": {
                    "invsqrt": {"qubits": 62, "t_equiv": 1622.7},
                    "dqi": {"qubits": 889, "mean_toffolis": 427471.2},
                    "chemistry": {"qubits": 430, "toffolis": 16266.0, "lambda_eff": 48.2992},
                }
            }, f)
        self.engine = ExperimentEngine(workspace_root=self.workspace)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_rejection_when_score_lower(self):
        # Worse candidate (higher Toffolis)
        res = self.engine.record_run(
            experiment_id="TEST-01",
            task="dqi",
            hypothesis="Higher Toffolis should be rejected",
            params={"variant": "worse"},
            artifact_path=None,
            metrics={"qubits": 889, "t_mean": 500000.0, "failures": 0},
            verifier_mode="full"
        )
        self.assertFalse(res["promoted"])
        self.assertLess(res["composite_score"], 23.17767)

    def test_rejection_when_quick_mode(self):
        # Better candidate (lower Toffolis), but quick mode!
        res = self.engine.record_run(
            experiment_id="TEST-02",
            task="dqi",
            hypothesis="Better score in quick mode must not promote",
            params={"variant": "tower42"},
            artifact_path=None,
            metrics={"qubits": 889, "t_mean": 409711.0, "failures": 0},
            verifier_mode="quick"
        )
        self.assertFalse(res["promoted"])
        self.assertGreater(res["composite_score"], 23.17767)
        self.assertIn("not full verification mode", res["reason"])

    def test_promotion_when_full_mode_and_better(self):
        # Better candidate with full verification mode
        res = self.engine.record_run(
            experiment_id="TEST-03",
            task="dqi",
            hypothesis="Better score with full verification mode must promote",
            params={"variant": "tower42_verified"},
            artifact_path=None,
            metrics={"qubits": 889, "t_mean": 409711.0, "failures": 0},
            verifier_mode="full"
        )
        self.assertTrue(res["promoted"])
        self.assertGreater(res["composite_score"], 23.17767)


if __name__ == "__main__":
    unittest.main()
