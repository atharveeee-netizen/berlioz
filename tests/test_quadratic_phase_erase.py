import unittest
import kickmix as km
from src.dqi.quadratic_phase_erase import QuadraticPhaseEraser

class TestQuadraticPhaseErasure(unittest.TestCase):
    def test_single_and_erasure(self):
        for x0 in [False, True]:
            for x1 in [False, True]:
                b = km.CircuitBuilder()
                q = b.alloc_qubits(3)
                bits = b.alloc_bits(1)

                if x0: b.x(q[0])
                if x1: b.x(q[1])

                # Compute target y = q2 = q0 * q1
                b.ccx(q[0], q[1], q[2])

                # Zero-Toffoli uncompute
                QuadraticPhaseEraser.erase_and_pair(b, q[2], q[0], q[1], bits[0])

                c = b.finish_circuit()
                sim = km.Simulator(1, counting_operations=True)
                sim.do(c)

                # Assert target is cleanly |0> and phase kickback is 0
                self.assertFalse(sim.read_within_shot(q[2], 0), f"Qubit q2 not |0> for inputs ({x0}, {x1})")
                self.assertEqual(sim.read_shot_phase(0), 0, f"Nonzero phase for inputs ({x0}, {x1})")

                # Verify Toffoli cost: exactly 1 (forward only), uncompute cost is 0
                self.assertEqual(c.operation_statistics().num_toffoli_like, 1)

    def test_compound_bilinear_erasure(self):
        # y = (q0 * q1) ^ (q2 * q3)
        for x in range(16):
            bits_in = [(x >> i) & 1 for i in range(4)]
            b = km.CircuitBuilder()
            q = b.alloc_qubits(5)
            bits = b.alloc_bits(1)

            for i in range(4):
                if bits_in[i]: b.x(q[i])

            # Forward compute into q4
            b.ccx(q[0], q[1], q[4])
            b.ccx(q[2], q[3], q[4])

            # Erase using quadratic phase eraser
            terms = [(q[0], q[1]), (q[2], q[3])]
            QuadraticPhaseEraser.erase_bilinear_form(b, q[4], terms, bits[0])

            c = b.finish_circuit()
            sim = km.Simulator(1, counting_operations=True)
            sim.do(c)

            self.assertFalse(sim.read_within_shot(q[4], 0))
            self.assertEqual(sim.read_shot_phase(0), 0)
            self.assertEqual(c.operation_statistics().num_toffoli_like, 2) # only 2 forward Toffolis, 0 uncompute!

if __name__ == '__main__':
    unittest.main()
