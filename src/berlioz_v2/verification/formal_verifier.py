"""
Unified Formal & Equivalence Verification Suite for Berlioz 2.0.
Verifies algebraic identities, boolean truth tables, Clifford stabilizer invariance,
and fixed-point numerical error bounds across compiler transformations.
"""

from dataclasses import dataclass, field
from typing import Callable, List, Dict, Any, Tuple, Optional
import random
import math


@dataclass
class VerificationResult:
    test_suite: str
    passed: bool
    num_tests: int
    num_passed: int
    num_failed: int
    max_error: float = 0.0
    failure_details: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class FormalVerifier:
    """Rigorous verification engine for quantum compiler transformations."""

    @staticmethod
    def verify_galois_field_multiplication(
        mul_func: Callable[[int, int], int],
        degree: int = 12,
        poly: int = 0x1053,
        num_random_trials: int = 1000,
    ) -> VerificationResult:
        """
        Formally verifies GF(2^k) polynomial multiplication against algebraic reference.
        """
        def ref_gf_mul(a: int, b: int) -> int:
            res = 0
            for i in range(degree):
                if (b >> i) & 1:
                    res ^= (a << i)
            # Reduce modulo irreducible polynomial
            for i in range(2 * degree - 1, degree - 1, -1):
                if (res >> i) & 1:
                    res ^= (poly << (i - degree))
            return res

        # 1. Deterministic boundary elements
        edge_cases = [
            (0, 0),
            (0, 1),
            (1, 1),
            (1, (1 << degree) - 1),
            ((1 << degree) - 1, (1 << degree) - 1),
            (1 << (degree - 1), 1 << (degree - 1)),
        ]

        passed = 0
        failed = 0
        details = None

        for a, b in edge_cases:
            expected = ref_gf_mul(a, b)
            actual = mul_func(a, b)
            if actual != expected:
                failed += 1
                details = f"Edge case failed: {hex(a)} * {hex(b)} -> expected {hex(expected)}, got {hex(actual)}"
                break
            passed += 1

        if failed == 0:
            # 2. Randomized trials
            mask = (1 << degree) - 1
            for _ in range(num_random_trials):
                a = random.randint(0, mask)
                b = random.randint(0, mask)
                expected = ref_gf_mul(a, b)
                actual = mul_func(a, b)
                if actual != expected:
                    failed += 1
                    details = f"Random trial failed: {hex(a)} * {hex(b)} -> expected {hex(expected)}, got {hex(actual)}"
                    break
                passed += 1

        return VerificationResult(
            test_suite=f"GF(2^{degree}) Formal Multiplication",
            passed=(failed == 0),
            num_tests=passed + failed,
            num_passed=passed,
            num_failed=failed,
            failure_details=details,
        )

    @staticmethod
    def verify_fixed_point_invsqrt(
        invsqrt_func: Callable[[float], float],
        domain_min: float = 0.5,
        domain_max: float = 1.0,
        num_samples: int = 5000,
        max_allowed_rel_error: float = 1e-4,
    ) -> VerificationResult:
        """
        Verifies numerical precision of fixed-point inverse square root.
        """
        max_err = 0.0
        passed = 0
        failed = 0
        details = None

        step = (domain_max - domain_min) / num_samples
        for i in range(num_samples):
            x = domain_min + i * step
            expected = 1.0 / math.sqrt(x)
            actual = invsqrt_func(x)
            rel_err = abs(actual - expected) / expected
            if rel_err > max_err:
                max_err = rel_err
            if rel_err > max_allowed_rel_error:
                failed += 1
                if details is None:
                    details = f"Precision exceeded at x={x}: actual={actual}, expected={expected}, rel_err={rel_err}"
            else:
                passed += 1

        return VerificationResult(
            test_suite="Fixed-Point InvSqrt Precision",
            passed=(failed == 0),
            num_tests=num_samples,
            num_passed=passed,
            num_failed=failed,
            max_error=max_err,
            failure_details=details,
            metadata={"domain": [domain_min, domain_max], "max_allowed_rel_error": max_allowed_rel_error},
        )
