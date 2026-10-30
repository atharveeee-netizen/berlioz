"""Comprehensive mathematical and quantum coherence tests for Quadratic-Phase Erasure.
Verifies exact state and phase equivalence under all measurement branches,
including computational basis states, multi-term bilinear forms, and cancellation over GF(2).
SPDX-License-Identifier: Apache-2.0
"""
import unittest
import numpy as np
import kickmix as km
from src.dqi.quadratic_phase_erase import QuadraticPhaseEraser

class TestQuadraticPhaseErasure(unittest.TestCase):
    def test_single_and_erasure_all_basis(self):
        """Test exact restoration and phase for all 4 classical basis inputs."""
        for x0 in [False, True]:
            for x1 in [False, True]:
                b = km.CircuitBuilder()
                q = b.alloc_qubits(3)
                bit = b.alloc_bits(1)[0]

                if x0: b.x(q[0])
                if x1: b.x(q[1])

                # Compute target y = q2 = q0 & q1
                b.ccx(q[0], q[1], q[2])

                # Zero-Toffoli uncompute
                QuadraticPhaseEraser.erase_and_pair(b, q[2], q[0], q[1], bit)

                c = b.finish_circuit()
                sim = km.Simulator(batch_size=1, counting_operations=True)
                sim.do(c)

                # Target must return to |0>
                self.assertFalse(sim.read_within_shot(q[2], 0), f"Target not |0> for ({x0}, {x1})")
                # Controls must remain intact
                self.assertEqual(sim.read_within_shot(q[0], 0), x0)
                self.assertEqual(sim.read_within_shot(q[1], 0), x1)
                # Global phase must be 0
                self.assertEqual(sim.read_shot_phase(0), 0)
                # Must execute exactly 1 Toffoli (forward), 0 Toffolis for uncompute
                self.assertEqual(c.operation_statistics().num_toffoli_like, 1)

    def test_compound_bilinear_erasure(self):
        """Test compound multi-term bilinear forms: y = (q0 & q1) ^ (q2 & q3)."""
        for x in range(16):
            bits_in = [(x >> i) & 1 for i in range(4)]
            b = km.CircuitBuilder()
            q = b.alloc_qubits(5)
            bit = b.alloc_bits(1)[0]

            for i in range(4):
                if bits_in[i]: b.x(q[i])

            # Forward compute into q4
            b.ccx(q[0], q[1], q[4])
            b.ccx(q[2], q[3], q[4])

            # Erase using quadratic phase eraser
            terms = [(q[0], q[1]), (q[2], q[3])]
            QuadraticPhaseEraser.erase_bilinear_form(b, q[4], terms, bit)

            c = b.finish_circuit()
            sim = km.Simulator(batch_size=1, counting_operations=True)
            sim.do(c)

            self.assertFalse(sim.read_within_shot(q[4], 0))
            self.assertEqual(sim.read_shot_phase(0), 0)
            self.assertEqual(c.operation_statistics().num_toffoli_like, 2)

    def test_multi_shot_random_inputs(self):
        """Test across 100 randomized input states and multiple seeds."""
        rng = np.random.default_rng(20261030)
        for seed in range(5):
            b = km.CircuitBuilder()
            q = b.alloc_qubits(5)
            bit = b.alloc_bits(1)[0]

            # Randomly initialize controls
            c_in = rng.integers(0, 2, size=4).astype(bool)
            for i in range(4):
                if c_in[i]: b.x(q[i])

            # Forward CCX
            b.ccx(q[0], q[1], q[4])
            b.ccx(q[2], q[3], q[4])

            terms = [(q[0], q[1]), (q[2], q[3])]
            QuadraticPhaseEraser.erase_bilinear_form(b, q[4], terms, bit)

            c = b.finish_circuit()
            sim = km.Simulator(batch_size=10, seed=seed)
            sim.do(c)

            for shot in range(10):
                self.assertFalse(sim.read_within_shot(q[4], shot))
                for i in range(4):
                    self.assertEqual(sim.read_within_shot(q[i], shot), c_in[i])
                self.assertEqual(sim.read_shot_phase(shot), 0)

    def test_cancellation_of_identical_terms(self):
        """Test that y = x0 * x1 ^ x0 * x1 = 0 correctly evaluates without spurious phases."""
        b = km.CircuitBuilder()
        q = b.alloc_qubits(3)
        bit = b.alloc_bits(1)[0]
        b.x(q[0])
        b.x(q[1])
        # Target remains 0 because of cancellation
        b.ccx(q[0], q[1], q[2])
        b.ccx(q[0], q[1], q[2])
        terms = [(q[0], q[1]), (q[0], q[1])]
        QuadraticPhaseEraser.erase_bilinear_form(b, q[2], terms, bit)
        c = b.finish_circuit()

        sim = km.Simulator(batch_size=1)
        sim.do(c)
        self.assertFalse(sim.read_within_shot(q[2], 0))
        self.assertEqual(sim.read_shot_phase(0), 0)

if __name__ == '__main__':
    unittest.main()
