"""
Adversarial Stress Testing & Property-Based Shrinking Suite for Berlioz 2.0.
Generates pathological inputs, edge cases, and discovers failure boundaries.
"""

from dataclasses import dataclass, field
from typing import Callable, List, Dict, Any, Optional, Tuple
import random


@dataclass
class AdversarialSuiteReport:
    suite_name: str
    total_stress_cases: int
    passed_cases: int
    vulnerabilities_found: int
    minimal_counterexample: Optional[Any] = None
    vulnerability_log: List[str] = field(default_factory=list)


class AdversarialStressTester:
    """Property-based fuzzing and stress testing harness."""

    def __init__(self, seed: int = 1337):
        random.seed(seed)
        self.seed = seed

    def stress_test_boolean_inversion(
        self,
        invert_func: Callable[[int], int],
        bit_width: int = 16,
        trials: int = 2000,
    ) -> AdversarialSuiteReport:
        """
        Stress tests reversible modular or field inversion across adversarial boundaries.
        """
        passed = 0
        vulns = 0
        minimal_fail = None
        log = []

        # 1. Pathological boundary vectors
        boundaries = [
            0,
            1,
            (1 << bit_width) - 1,
            1 << (bit_width - 1),
            (1 << (bit_width // 2)) - 1,
            0x55555555 & ((1 << bit_width) - 1),
            0xAAAAAAAA & ((1 << bit_width) - 1),
        ]

        for val in boundaries:
            try:
                # Reversibility test: invert(invert(x)) == x
                res = invert_func(invert_func(val))
                if res != val:
                    vulns += 1
                    log.append(f"Boundary involution failure at val={hex(val)}: got {hex(res)}")
                    minimal_fail = val
                else:
                    passed += 1
            except Exception as e:
                vulns += 1
                log.append(f"Exception at boundary val={hex(val)}: {str(e)}")
                minimal_fail = val

        # 2. Randomized high Hamming weight fuzzing
        for _ in range(trials):
            # Biased generation towards sparse or dense bit patterns
            if random.random() < 0.5:
                # Sparse (Hamming weight 1 or 2)
                val = (1 << random.randint(0, bit_width - 1)) | (1 << random.randint(0, bit_width - 1))
            else:
                # Dense (all ones with 1 or 2 zeros)
                val = ((1 << bit_width) - 1) ^ (1 << random.randint(0, bit_width - 1))

            try:
                res = invert_func(invert_func(val))
                if res != val:
                    vulns += 1
                    if minimal_fail is None or bin(val).count("1") < bin(minimal_fail).count("1"):
                        minimal_fail = val
                    log.append(f"Inversion failure at fuzzed input={hex(val)}")
                else:
                    passed += 1
            except Exception as e:
                vulns += 1
                log.append(f"Exception at input={hex(val)}: {str(e)}")

        return AdversarialSuiteReport(
            suite_name=f"{bit_width}-bit Reversible Inversion Stress",
            total_stress_cases=passed + vulns,
            passed_cases=passed,
            vulnerabilities_found=vulns,
            minimal_counterexample=minimal_fail,
            vulnerability_log=log[:10],  # Keep top 10 logs
        )
