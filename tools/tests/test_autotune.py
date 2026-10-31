#!/usr/bin/env python3
"""
tools/tests/test_autotune.py — Unit tests for Autotuner and Pareto archiving (Chunk C10 Gate)
"""

import os
import sys
import json
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from tools.autotune import Autotuner


def test_autotune_deterministic_pareto():
    param_grid = {
        "horner_degree": [3, 4, 5],
        "precision_bits": [14, 16, 18],
    }

    t0 = time.time()
    # Run 1
    tuner1 = Autotuner(
        benchmark="invsqrt",
        param_grid=param_grid,
        pareto_file="audit/ml16/pareto_test1.jsonl",
        checkpoint_file="audit/ml16/test_checkpoint1.json",
        seed=42,
    )
    p1 = tuner1.run()
    elapsed = time.time() - t0
    assert elapsed < 10.0, f"Autotune took {elapsed:.2f}s (exceeded 10s budget)"
    assert len(p1) > 0, "Pareto front 1 is empty"

    # Run 2 with same seed
    tuner2 = Autotuner(
        benchmark="invsqrt",
        param_grid=param_grid,
        pareto_file="audit/ml16/pareto_test2.jsonl",
        checkpoint_file="audit/ml16/test_checkpoint2.json",
        seed=42,
    )
    p2 = tuner2.run()

    # Determinism check
    assert len(p1) == len(p2), f"Pareto size mismatch: {len(p1)} vs {len(p2)}"
    for r1, r2 in zip(p1, p2):
        assert r1["params"] == r2["params"]
        assert abs(r1["cost"] - r2["cost"]) < 1e-6

    # Clean up test files
    for path in [
        "audit/ml16/pareto_test1.jsonl",
        "audit/ml16/test_checkpoint1.json",
        "audit/ml16/pareto_test2.jsonl",
        "audit/ml16/test_checkpoint2.json",
    ]:
        if os.path.exists(path):
            os.remove(path)

    print("ALL tests in test_autotune.py PASSED (Gate C10 Green).")


if __name__ == "__main__":
    test_autotune_deterministic_pareto()
