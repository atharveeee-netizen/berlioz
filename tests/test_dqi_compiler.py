"""Unit tests for the modular 42-product DQI synthesizer.
SPDX-License-Identifier: Apache-2.0
"""
import unittest
import sys, os, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'src/dqi'), str(ROOT / 'verifiers')]

import kickmix as km
from build_dqi import build_42product_dqi

class TestDQICompiler(unittest.TestCase):
    def test_mini_dqi_synthesis(self):
        """Verify that build_42product_dqi correctly synthesizes a small instance without leaks."""
        with tempfile.TemporaryDirectory() as td:
            out_file = Path(td) / "mini_dqi.kmb"
            circuit = build_42product_dqi(str(out_file), n_syndromes=2, n_codeword=4, degree=12)
            self.assertTrue(out_file.exists())
            self.assertGreater(out_file.stat().st_size, 0)
            
            # Verify circuit loaded back from file
            loaded = km.Circuit.from_file(str(out_file))
            self.assertEqual(loaded.num_qubits, circuit.num_qubits)
            self.assertGreater(loaded.operation_statistics().num_toffoli_like, 0)
            
            # Verify all registers are named strings
            for reg_name in loaded.register_data:
                self.assertIsInstance(reg_name, str)

if __name__ == '__main__':
    unittest.main()
