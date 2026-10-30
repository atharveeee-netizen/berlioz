"""Comprehensive mathematical verification for Inversionless Berlekamp-Massey over GF(2^12).
Proves equivalence with standard inversion-based Berlekamp-Massey across:
- Zero errors (t=0)
- Single error (t=1)
- Boundary positions (0, 4094) and values (1, 4095)
- Error patterns up to maximum capacity t=35
- Direct polynomial proportionality: Lambda_ribm(x) == c * Lambda_std(x)
SPDX-License-Identifier: Apache-2.0
"""
import unittest
import numpy as np
import kickmix as km

class TestInversionlessBM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.field = km.GF2Field(12)
        cls.alpha = cls.field.primitive_element
        cls.n_syndromes = 70
        cls.max_errors = 35

    def compute_syndromes(self, error_positions, error_values):
        syndromes = [0] * self.n_syndromes
        for i in range(self.n_syndromes):
            s = 0
            for pos, val in zip(error_positions, error_values):
                p = self.field.pow(self.alpha, (i + 1) * pos)
                prod = self.field.mul(val, p)
                s ^= prod
            syndromes[i] = s
        return syndromes

    def standard_bm_with_inversion(self, syndromes):
        """Standard Berlekamp-Massey algorithm using explicit field inversion."""
        gf = self.field
        Lambda = [1]
        B = [1]
        L = 0
        m = 1
        b_val = 1

        for r in range(len(syndromes)):
            # Discrepancy delta_r = sum_{j=0}^L Lambda[j] * S[r - j]
            delta = syndromes[r]
            for j in range(1, len(Lambda)):
                if (r - j) >= 0:
                    delta ^= gf.mul(Lambda[j], syndromes[r - j])

            if delta == 0:
                m += 1
            else:
                # factor = delta * b_val^{-1}
                inv_b = gf.invert(b_val)
                factor = gf.mul(delta, inv_b)
                
                # new_Lambda = Lambda - factor * x^m * B
                shift_B = [0] * m + B
                max_len = max(len(Lambda), len(shift_B))
                new_Lambda = [0] * max_len
                for i in range(max_len):
                    c1 = Lambda[i] if i < len(Lambda) else 0
                    c2 = gf.mul(factor, shift_B[i]) if i < len(shift_B) else 0
                    new_Lambda[i] = c1 ^ c2

                if 2 * L <= r:
                    B = list(Lambda)
                    b_val = delta
                    L = r + 1 - L
                    m = 1
                else:
                    m += 1
                Lambda = new_Lambda

        return Lambda

    def ribm(self, syndromes):
        """Reformulated Inversionless Berlekamp-Massey (RiBM) algorithm over GF(2^12)."""
        gf = self.field
        Lambda = [1] + [0] * self.max_errors
        B = [1] + [0] * self.max_errors
        gamma = 1
        k = 0

        for r in range(len(syndromes)):
            delta = 0
            for j in range(len(Lambda)):
                if Lambda[j] != 0 and (r - j) >= 0:
                    delta ^= gf.mul(Lambda[j], syndromes[r - j])

            Lambda_new = [0] * (self.max_errors + 1)
            for i in range(self.max_errors + 1):
                t1 = gf.mul(gamma, Lambda[i]) if Lambda[i] != 0 else 0
                t2 = 0
                if i > 0 and B[i - 1] != 0 and delta != 0:
                    t2 = gf.mul(delta, B[i - 1])
                Lambda_new[i] = t1 ^ t2

            if delta != 0 and k >= 0:
                B = list(Lambda)
                gamma = delta
                k = -k - 1
            else:
                B = [0] + B[:-1]
                k = k + 1

            Lambda = Lambda_new

        deg = self.max_errors
        while deg > 0 and Lambda[deg] == 0:
            deg -= 1
        return Lambda[:deg + 1]

    def test_zero_errors(self):
        """Zero errors must produce Lambda(x) = 1."""
        S = [0] * self.n_syndromes
        Lambda = self.ribm(S)
        self.assertEqual(len(Lambda), 1)
        self.assertNotEqual(Lambda[0], 0)

    def test_single_error_boundaries(self):
        """Test boundary positions 0 and 4094 and values 1 and 4095."""
        for pos in [0, 1, 4094]:
            for val in [1, 2, 4095]:
                S = self.compute_syndromes([pos], [val])
                Lambda_ribm = self.ribm(S)
                Lambda_std = self.standard_bm_with_inversion(S)

                self.assertEqual(len(Lambda_ribm), 2)
                self.assertEqual(len(Lambda_std), 2)

                # Verify root: alpha^{-pos}
                root = self.field.pow(self.alpha, (4095 - pos) % 4095)
                val_root = Lambda_ribm[0] ^ self.field.mul(Lambda_ribm[1], root)
                self.assertEqual(val_root, 0)

                # Verify proportionality: Lambda_ribm == c * Lambda_std
                c = self.field.div(Lambda_ribm[0], Lambda_std[0])
                for j in range(len(Lambda_ribm)):
                    self.assertEqual(Lambda_ribm[j], self.field.mul(c, Lambda_std[j]))

    def test_random_patterns_up_to_capacity(self):
        """Compare RiBM against standard BM for random error patterns across 10 random seeds."""
        for seed in range(10):
            rng = np.random.default_rng(20261030 + seed)
            for num_err in [2, 5, 10, 20, 30, 35]:
                positions = rng.choice(4095, size=num_err, replace=False).tolist()
                values = rng.integers(1, 4096, size=num_err).tolist()
                S = self.compute_syndromes(positions, values)

                Lambda_ribm = self.ribm(S)
                Lambda_std = self.standard_bm_with_inversion(S)

                # Verify degrees match
                self.assertEqual(len(Lambda_ribm) - 1, num_err, f"RiBM degree mismatch for num_err={num_err}")
                self.assertEqual(len(Lambda_std) - 1, num_err, f"Std degree mismatch for num_err={num_err}")

                # Verify proportionality
                c = self.field.div(Lambda_ribm[0], Lambda_std[0])
                for j in range(len(Lambda_ribm)):
                    expected_coeff = self.field.mul(c, Lambda_std[j])
                    self.assertEqual(Lambda_ribm[j], expected_coeff)

                # Verify every error location is a root
                for p in positions:
                    x = self.field.pow(self.alpha, (4095 - p) % 4095)
                    res = 0
                    x_pow = 1
                    for coeff in Lambda_ribm:
                        if coeff != 0:
                            res ^= self.field.mul(coeff, x_pow)
                        x_pow = self.field.mul(x_pow, x)
                    self.assertEqual(res, 0, f"Error at pos {p} was not a root of Lambda_ribm!")

if __name__ == '__main__':
    unittest.main()
