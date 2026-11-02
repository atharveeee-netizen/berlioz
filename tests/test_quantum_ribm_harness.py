"""Step 2 Unit Verification Harness: Reversible Quantum RiBM & Normalization.
Framework: Syzygy Spec-Driven Development Standard (v1.0.0)
Evidence Class: E2 (Local Quantum Simulation in km.Simulator)

Verifies:
1. Exact scalar inversion & polynomial normalization circuit.
2. 100% clean ancilla restoration to |0> across all scratch registers.
3. Zero relative phase errors across all 16 simulator shots.

SPDX-License-Identifier: Apache-2.0
"""
import sys
import unittest
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / 'src/dqi')]

import kickmix as km
import numpy as np
from src.dqi.quantum_ribm_synthesis import QuantumRiBMSynthesizer

class TestQuantumRiBMHarness(unittest.TestCase):
    def setUp(self):
        self.degree = 12
        self.field = km.GF2Field(self.degree)
        self.synth = QuantumRiBMSynthesizer(degree=self.degree)

    def test_scalar_normalization_circuit(self):
        """Tests that normalizing a 3-term polynomial by scalar c leaves zero junk and zero phase drift."""
        random.seed(20261102)
        np.random.seed(20261102)
        batch_size = 16

        for trial in range(5):
            val_c = random.randint(1, 4095)
            val_p0 = random.randint(1, 4095)
            val_p1 = random.randint(1, 4095)

            builder = km.CircuitBuilder()
            c_reg = builder.alloc_qubits(self.degree)
            inv_c_reg = builder.alloc_qubits(self.degree)
            p0_reg = builder.alloc_qubits(self.degree)
            p1_reg = builder.alloc_qubits(self.degree)

            # Load values into registers
            for b in range(self.degree):
                if (val_c >> b) & 1: builder.x(c_reg[b])
                if (val_p0 >> b) & 1: builder.x(p0_reg[b])
                if (val_p1 >> b) & 1: builder.x(p1_reg[b])

            # Apply scalar normalization: p0 <- p0 * c^-1, p1 <- p1 * c^-1
            target_polys = [[p0_reg, p1_reg]]
            self.synth.build_scalar_normalization(builder, c_reg, inv_c_reg, target_polys)

            # Verify mathematically expected values
            inv_c_expected = self.field.invert(val_c)
            p0_norm_expected = self.field.mul(val_p0, inv_c_expected)
            p1_norm_expected = self.field.mul(val_p1, inv_c_expected)

            # Uncompute inputs to test perfect reversible restoration
            for b in range(self.degree):
                if (val_c >> b) & 1: builder.x(c_reg[b])
                if (p0_norm_expected >> b) & 1: builder.x(p0_reg[b])
                if (p1_norm_expected >> b) & 1: builder.x(p1_reg[b])

            circuit = builder.finish_circuit()

            sim = km.Simulator(batch_size=batch_size, counting_operations=True, seed=42 + trial)
            sim.use_same_registers_as(circuit)
            sim.do(circuit)

            all_qubits = km.array([*c_reg, *inv_c_reg, *p0_reg, *p1_reg])
            junk = sim.read_across_shots(all_qubits).any()
            phase_err = sim.read_phase_flipped_across_shots().any()

            self.assertFalse(junk, f"Trial {trial}: Found dirty qubits after normalization uncomputation!")
            self.assertFalse(phase_err, f"Trial {trial}: Phase flip detected in quantum state!")

        print("[+] TestQuantumRiBMHarness: All 5 randomized trials PASSED with 0 value/phase errors.")

if __name__ == '__main__':
    unittest.main()
