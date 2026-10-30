"""Mathematical unit test for Inversionless Berlekamp-Massey over GF(2^12).
Verifies that Reformulated Inversionless Berlekamp-Massey (RiBM) correctly finds
the error locator polynomial Lambda(x) without any field inversions.
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

    def inversionless_bm(self, syndromes):
        """Reformulated Inversionless Berlekamp-Massey (RiBM) algorithm over GF(2^12).
        Returns the error locator polynomial coefficients Lambda."""
        gf = self.field
        Lambda = [1] + [0] * self.max_errors
        B = [1] + [0] * self.max_errors
        gamma = 1
        k = 0

        for r in range(len(syndromes)):
            # Discrepancy delta_r = sum_{j=0}^r Lambda_j * S_{r-j}
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

    def test_single_error(self):
        """Test locator roots for a single error."""
        pos = [42]
        val = [123]
        S = self.compute_syndromes(pos, val)
        Lambda = self.inversionless_bm(S)
        self.assertEqual(len(Lambda), 2)
        root = self.field.pow(self.alpha, (4095 - pos[0]) % 4095)
        val_at_root = Lambda[0] ^ self.field.mul(Lambda[1], root)
        self.assertEqual(val_at_root, 0, "Root condition failed for single error")

    def test_random_errors(self):
        """Test locator roots for random error patterns up to t=35."""
        rng = np.random.default_rng(20261030)
        for num_err in [2, 5, 10, 20, 35]:
            positions = rng.choice(4095, size=num_err, replace=False).tolist()
            values = rng.integers(1, 4096, size=num_err).tolist()
            S = self.compute_syndromes(positions, values)
            Lambda = self.inversionless_bm(S)
            self.assertEqual(len(Lambda) - 1, num_err)
            
            for p in positions:
                x = self.field.pow(self.alpha, (4095 - p) % 4095)
                res = 0
                x_pow = 1
                for coeff in Lambda:
                    if coeff != 0:
                        res ^= self.field.mul(coeff, x_pow)
                    x_pow = self.field.mul(x_pow, x)
                self.assertEqual(res, 0, f"Error at pos {p} was not a root of Lambda!")

if __name__ == '__main__':
    unittest.main()
