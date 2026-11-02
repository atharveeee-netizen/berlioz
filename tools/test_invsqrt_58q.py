"""ML27 TASK-INV-01: Semantic & Numerical Verification of invsqrt_58q.kmb.

Authors: BERLIOZ Quantum Circuit Synthesis Team
Context: ML27 TASK-INV-01
Date: 2026-11-01
"""

from __future__ import annotations

import math
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kickmix"))
sys.path.insert(0, str(REPO_ROOT / "verifiers"))
sys.path.insert(0, str(REPO_ROOT))

import kickmix as km
import numpy as np
from invsqrt import verify_submission_invsqrt as vinv
from tools.score_calc import C_INVSQRT_REF


def main():
    circuit_path = REPO_ROOT / "build" / "circuits" / "invsqrt_58q.kmb"
    assert circuit_path.exists(), f"Circuit not found at {circuit_path}"

    circ = km.Circuit.from_file(str(circuit_path), format="kmb")
    num_q = circ.num_qubits
    stats = circ.operation_statistics()
    toff = stats.num_toffoli_like
    t_like = stats.num_t_like

    print("=" * 80)
    print("TASK-INV-01: EVALUATING INVSQRT 58Q COMPILED ARTIFACT")
    print("=" * 80)
    print(f"Artifact Path:       {circuit_path}")
    print(f"Active Qubit Count:  {num_q} (Constraint: <= 58)")
    print(f"Toffoli-like Gates:  {toff}")
    print(f"T-like Gates:        {t_like}")

    spec = vinv.ProblemSpecInvSqrt.for_n_p(10)
    x_reg, scratch = vinv.validate_registers(circ, spec)
    print(f"Input Register:      {x_reg} (length {len(x_reg)})")
    print(f"Scratch Register:    length {len(scratch)}")

    # Test on boundary points and sample domain points
    test_xs = np.array([1, 2, 3, 4, 7, 8, 15, 16, 31, 32, 63, 64, 127, 128, 161, 255, 256, 1023, 1024, 3133452], dtype=np.uint64)
    batch_size = len(test_xs)

    sim = km.Simulator(batch_size=batch_size, counting_operations=True, seed=42)
    sim.clear_for_shot()
    sim.write_across_shots(x_reg, vinv.to_bits(test_xs, spec.width))
    sim.do(circ)

    # 1. Register restoration check
    read_x = vinv.from_bits(sim.read_across_shots(x_reg))
    x_restored = np.array_equal(read_x, test_xs)
    print(f"\n[1] Input Register Restoration: {'PASS' if x_restored else 'FAIL'}")

    # 2. Ancilla cleanup check
    dirty = sim.read_across_shots(scratch).any(axis=1) if len(scratch) else np.zeros(batch_size, dtype=bool)
    ancillas_clean = not dirty.any()
    print(f"[2] Ancilla Cleanup to |0>:     {'PASS' if ancillas_clean else f'FAIL ({dirty.sum()} dirty qubits)'}")

    # 3. Phase accuracy check
    target, tol = vinv.reference_values(spec, test_xs)
    theta = np.array([vinv.half_turns_to_units(sim.read_shot_phase(i)) for i in range(batch_size)], dtype=np.uint64)
    error = (theta - target).view(np.int64)
    used = np.abs(error).view(np.uint64)
    within_tol = (used <= tol)
    max_error_ratio = (used / tol).max()
    min_margin = (tol - used).min() if within_tol.all() else -1

    print(f"[3] Phase Accuracy Check:       {'PASS' if within_tol.all() else 'FAIL'}")
    print(f"    Max Error / Tolerance:      {max_error_ratio:.4f}")
    print(f"    Min Margin Slack (units):   {min_margin}")

    for idx, x_val in enumerate(test_xs):
        status_str = "PASS" if used[idx] <= tol[idx] else "FAIL"
        print(f"    x={x_val:7d}: error={error[idx]:+18d}, tol={tol[idx]:18d}, ratio={used[idx]/tol[idx]:.4f} [{status_str}]")

    # 4. Resource & Score computation
    t_equiv = toff + t_like / 4.0
    cost = num_q * t_equiv
    ratio = C_INVSQRT_REF / cost
    print("\n" + "=" * 80)
    print(f"Billed T-Equivalent Cost:   {t_equiv:.2f}")
    print(f"Total Billed Cost:          {cost:.2f}")
    print(f"Official Invsqrt Ratio:     {ratio:.5f}x")
    print(f"Incumbent Ratio:            22.25302x")
    print("=" * 80)


if __name__ == "__main__":
    main()
