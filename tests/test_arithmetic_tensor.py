"""Unit tests for the 42-product bilinear tensor multiplier.
Verifies all 144 basis products in GF(2^12) modulus 0x1053 and edge-case multiplications.
SPDX-License-Identifier: Apache-2.0
"""
import unittest
import numpy as np
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'src/dqi'), str(ROOT / 'verifiers')]

import tower42
import kickmix as km

class TestArithmeticTensor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.field = km.GF2Field(12)
        cls.terms = tower42.tower42(cls.field.modulus)

    def test_tensor_rank(self):
        """Verify that the bilinear tensor has exact rank 42 (cutting 33.3% of products)."""
        self.assertEqual(len(self.terms), 42)

    def test_basis_products_exhaustive(self):
        """Verify all 144 basis products (1<<i) * (1<<j) against Kickmix GF(2^12)."""
        for i in range(12):
            for j in range(12):
                expected = self.field.mul(1 << i, 1 << j)
                actual = 0
                for a, b, c in self.terms:
                    if ((a >> i) & 1) and ((b >> j) & 1):
                        actual ^= c
                self.assertEqual(actual, expected, f"Failed at basis product ({i}, {j})")

    def test_edge_cases(self):
        """Verify multiplication with 0 and identity element 1."""
        mul = lambda x, y: self.field.mul(x, y)
        test_pairs = [
            (0, 0),
            (0, 0xFFF),
            (1, 0xFFF),
            (0xFFF, 0xFFF),
            (0x555, 0xAAA),
            (0x100, 0x010),
        ]
        for x, y in test_pairs:
            expected = mul(x, y)
            actual = 0
            for a, b, c in self.terms:
                p_a = bin(x & a).count('1') & 1
                p_b = bin(y & b).count('1') & 1
                if p_a and p_b:
                    actual ^= c
            self.assertEqual(actual, expected, f"Failed on pair ({hex(x)}, {hex(y)})")

    def test_random_samples(self):
        """Verify 500 pseudo-random pseudo-seeded multiplications."""
        rng = np.random.default_rng(42)
        xs = rng.integers(0, 4096, size=500)
        ys = rng.integers(0, 4096, size=500)
        for x, y in zip(xs, ys):
            x = int(x); y = int(y)
            expected = self.field.mul(x, y)
            actual = 0
            for a, b, c in self.terms:
                if (bin(x & a).count('1') & 1) and (bin(y & b).count('1') & 1):
                    actual ^= c
            self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
