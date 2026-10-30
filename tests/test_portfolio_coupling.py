"""Unit tests for chemistry factor loading, Givens gauge compliance, and QROM batching constraints.
SPDX-License-Identifier: Apache-2.0
"""
import unittest
import numpy as np
import sys, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'src/chem'), str(ROOT / 'verifiers')]

import angles_qrom as AQ
import banked_lab as B

class TestPortfolioCoupling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fact_path = ROOT / 'fact/dfthc_r10_b129_c60_brot8.npz'
        if not cls.fact_path.exists():
            raise unittest.SkipTest(f"Missing {cls.fact_path}")
        cls.data = dict(np.load(cls.fact_path))

    def test_tensor_shapes(self):
        """Verify tensor shapes for R=10, B=129, C=60 factorization."""
        self.assertIn('W', self.data)
        self.assertIn('U', self.data)
        self.assertIn('angle_words', self.data)
        self.assertIn('tree_edges', self.data)
        
        W = self.data['W']
        self.assertEqual(W.shape, (10, 129, 60))
        self.assertEqual(self.data['angle_words'].shape, (1366, 75))

    def test_half_open_gauge(self):
        """Verify that the signed half-open gauge condition bit(7) == bit(6) holds exactly."""
        words = self.data['angle_words']
        edges = self.data['tree_edges']
        brot = int(self.data['brot'])
        self.assertEqual(brot, 8)
        
        canonical = AQ.canonical_words(words, edges, brot)
        top = brot - 1
        nxt = brot - 2
        # Check that top bit equals next bit across all 1366 x 75 words
        mismatch = np.any(((canonical >> top) ^ (canonical >> nxt)) & 1)
        self.assertFalse(mismatch, "Half-open gauge condition bit(7) == bit(6) violated!")

    def test_batching_qubit_bounds(self):
        """Verify analytical qubit scaling Q(J) = 20 + 15J and that J=7 is maximal under Q <= 126."""
        # For brot=8, 1366 rows
        max_batch_2 = AQ.max_batch(8, 1366, addr=2)
        self.assertEqual(max_batch_2, 7, "Expected maximal batch size J=7 for addr=2")
        
        max_batch_4 = AQ.max_batch(8, 1366, addr=4)
        self.assertEqual(max_batch_4, 3, "Expected maximal batch size J=3 for addr=4")

    def test_single_circuit_synthesis(self):
        """Generate a single angle circuit for J=7 and verify qubit count is strictly <= 126."""
        words = self.data['angle_words']
        edges = self.data['tree_edges']
        brot = int(self.data['brot'])
        canonical = AQ.canonical_words(words, edges, brot)
        deltas = AQ.batch_deltas(canonical, 7)
        
        # Build first batch
        c, rep = AQ.build2(deltas[0], brot, return_report=True)
        self.assertLessEqual(c.num_qubits, 126, f"Circuit exceeded 126 qubits: {c.num_qubits}")
        self.assertEqual(int(c.operation_statistics().num_t_like), 0, "Angle circuit cannot contain T gates (must be static Clifford+Toffoli)")

if __name__ == '__main__':
    unittest.main()
