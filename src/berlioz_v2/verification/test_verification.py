#!/usr/bin/env python3
"""
Unit tests for FormalVerifier suite, testing valid operations and ensuring
deliberately-wrong circuits are rejected (Chunk C16 Gate).
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from src.berlioz_v2.verification.formal_verifier import FormalVerifier


def test_exhaustive_boolean_rejection():
    # Valid: identity
    res_valid = FormalVerifier.verify_exhaustive_boolean(lambda x: x ^ 1, lambda x: x ^ 1, num_bits=6)
    assert res_valid.passed, "Valid boolean circuit failed"

    # Deliberately wrong: bit flip at one input
    def faulty_func(x):
        return (x ^ 1) if x != 7 else (x ^ 2)

    res_faulty = FormalVerifier.verify_exhaustive_boolean(faulty_func, lambda x: x ^ 1, num_bits=6)
    assert not res_faulty.passed, "Faulty boolean circuit was incorrectly accepted!"
    assert res_faulty.num_failed == 1


def test_statevector_rejection():
    # Valid: identical state
    v1 = np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)
    v2 = np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)
    res_valid = FormalVerifier.verify_statevector_equivalence(v1, v2)
    assert res_valid.passed, "Valid statevector failed"

    # Deliberately wrong: orthogonal state
    v_bad = np.array([0.0, 1.0, 0.0, 0.0], dtype=complex)
    res_bad = FormalVerifier.verify_statevector_equivalence(v1, v_bad)
    assert not res_bad.passed, "Orthogonal statevector was incorrectly accepted!"


def test_ancilla_cleanup_rejection():
    # Valid: clean ancillae
    res_valid = FormalVerifier.verify_ancilla_cleanup([0, 0, 0, 0])
    assert res_valid.passed, "Clean ancilla check failed"

    # Deliberately wrong: dirty ancilla
    res_bad = FormalVerifier.verify_ancilla_cleanup([0, 1, 0, 0])
    assert not res_bad.passed, "Dirty ancilla was incorrectly accepted!"
    assert res_bad.num_failed == 1


def test_galois_field_rejection():
    # Valid: correct multiplication
    from src.dqi.tower42 import gf_mul
    res_valid = FormalVerifier.verify_galois_field_multiplication(lambda a, b: gf_mul(a, b, 0x1053), degree=12, poly=0x1053, num_random_trials=50)
    assert res_valid.passed, "Valid Galois multiplier failed"

    # Deliberately wrong: unreduced multiplication
    res_bad = FormalVerifier.verify_galois_field_multiplication(lambda a, b: a ^ b, degree=12, poly=0x1053, num_random_trials=50)
    assert not res_bad.passed, "Faulty Galois multiplier was incorrectly accepted!"


def test_fixed_point_rejection():
    # Valid: exact analytical
    res_valid = FormalVerifier.verify_fixed_point_invsqrt(lambda x: 1.0 / (x ** 0.5), num_samples=100)
    assert res_valid.passed, "Exact InvSqrt failed"

    # Deliberately wrong: linear approximation
    res_bad = FormalVerifier.verify_fixed_point_invsqrt(lambda x: 2.0 - x, num_samples=100)
    assert not res_bad.passed, "Faulty linear InvSqrt was incorrectly accepted!"


if __name__ == "__main__":
    test_exhaustive_boolean_rejection()
    test_statevector_rejection()
    test_ancilla_cleanup_rejection()
    test_galois_field_rejection()
    test_fixed_point_rejection()
    print("ALL tests in test_verification.py PASSED (Gate C16 Green).")
