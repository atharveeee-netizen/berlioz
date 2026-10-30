import json
import os
import unittest
from fractions import Fraction
import numpy as np
import kickmix as km

class TestPriceBook(unittest.TestCase):
    def setUp(self):
        self.results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
        os.makedirs(self.results_dir, exist_ok=True)
        self.pricebook_path = os.path.join(self.results_dir, "pricebook.json")

    def test_gate_marginal_costs(self):
        pricebook = {}

        # 1. Clifford Gates: X, CX, CZ, SWAP
        b = km.CircuitBuilder()
        q = b.alloc_qubits(3)
        b.x(q[0])
        b.cx(q[0], q[1])
        b.cz(q[0], q[1])
        b.swap(q[1], q[2])
        c_clifford = b.finish_circuit()
        stats_clifford = c_clifford.operation_statistics()
        pricebook["clifford_ops"] = {
            "num_toffoli_like": stats_clifford.num_toffoli_like,
            "num_t_like": stats_clifford.num_t_like,
            "num_non_clifford": stats_clifford.num_non_clifford,
            "num_instructions": stats_clifford.num_instructions
        }
        self.assertEqual(stats_clifford.num_toffoli_like, 0)
        self.assertEqual(stats_clifford.num_t_like, 0)

        # 2. Toffoli-like: CCX vs CCZ
        b = km.CircuitBuilder()
        q = b.alloc_qubits(3)
        b.ccx(q[0], q[1], q[2])
        c_ccx = b.finish_circuit()
        stats_ccx = c_ccx.operation_statistics()
        pricebook["ccx"] = {
            "num_toffoli_like": stats_ccx.num_toffoli_like,
            "num_t_like": stats_ccx.num_t_like,
            "num_instructions": stats_ccx.num_instructions
        }
        self.assertEqual(stats_ccx.num_toffoli_like, 1)

        b = km.CircuitBuilder()
        q = b.alloc_qubits(3)
        b.ccz(q[0], q[1], q[2])
        c_ccz = b.finish_circuit()
        stats_ccz = c_ccz.operation_statistics()
        pricebook["ccz"] = {
            "num_toffoli_like": stats_ccz.num_toffoli_like,
            "num_t_like": stats_ccz.num_t_like,
            "num_instructions": stats_ccz.num_instructions
        }
        self.assertEqual(stats_ccz.num_toffoli_like, 1)

        # 3. Z_POW Clifford Hierarchy
        # Level 1/2: Z (Clifford)
        b = km.CircuitBuilder()
        q = b.alloc_qubits(1)
        b.z_pow(q[0], Fraction(1, 2))
        stats_z = b.finish_circuit().operation_statistics()
        pricebook["z_pow_half"] = {
            "num_toffoli_like": stats_z.num_toffoli_like,
            "num_t_like": stats_z.num_t_like,
            "num_non_clifford": stats_z.num_non_clifford
        }
        self.assertEqual(stats_z.num_toffoli_like, 0)
        self.assertEqual(stats_z.num_t_like, 0)

        # Level 1/4: T (T-gate)
        b = km.CircuitBuilder()
        q = b.alloc_qubits(1)
        b.z_pow(q[0], Fraction(1, 4))
        stats_t = b.finish_circuit().operation_statistics()
        pricebook["z_pow_quarter_T"] = {
            "num_toffoli_like": stats_t.num_toffoli_like,
            "num_t_like": stats_t.num_t_like,
            "num_non_clifford": stats_t.num_non_clifford
        }
        self.assertEqual(stats_t.num_toffoli_like, 0)
        self.assertEqual(stats_t.num_t_like, 1)

        # Level Arbitrary: Rotation (Level >= 4)
        b = km.CircuitBuilder()
        q = b.alloc_qubits(1)
        b.z_pow(q[0], Fraction(1, 16))
        stats_rot = b.finish_circuit().operation_statistics()
        pricebook["z_pow_one_sixteenth_rotation"] = {
            "num_toffoli_like": stats_rot.num_toffoli_like,
            "num_t_like": stats_rot.num_t_like,
            "num_non_clifford": stats_rot.num_non_clifford,
            "z_pow_hierarchy": dict(stats_rot.z_pow_clifford_hierarchy_counts)
        }
        self.assertEqual(stats_rot.num_toffoli_like, 0)
        self.assertEqual(stats_rot.num_t_like, 0)
        self.assertEqual(stats_rot.num_non_clifford, 1)

        # 4. Conditional Gate Execution in Simulation
        b = km.CircuitBuilder()
        q = b.alloc_qubits(3)
        c_bits = b.alloc_bits(1)
        b.push_condition(c_bits[0])
        b.ccx(q[0], q[1], q[2])
        b.pop_condition()
        c_cond = b.finish_circuit()

        # Shot where condition is False (0)
        sim_false = km.Simulator(1, counting_operations=True)
        sim_false.do(c_cond)
        stats_false = sim_false.operation_statistics()

        # Shot where condition is True (1)
        sim_true = km.Simulator(1, counting_operations=True)
        sim_true.write_across_shots(c_bits, np.array([[True]]))
        sim_true.do(c_cond)
        stats_true = sim_true.operation_statistics()

        pricebook["conditional_execution"] = {
            "static_circuit_toffoli_like": c_cond.operation_statistics().num_toffoli_like,
            "simulated_toffoli_when_false": stats_false.num_toffoli_like,
            "simulated_toffoli_when_true": stats_true.num_toffoli_like,
            "price_gap_verdict": "Dynamic execution: gates gated behind false conditions cost 0 in simulator"
        }
        self.assertEqual(c_cond.operation_statistics().num_toffoli_like, 1)
        self.assertEqual(stats_false.num_toffoli_like, 0)
        self.assertEqual(stats_true.num_toffoli_like, 1)

        with open(self.pricebook_path, "w", encoding="utf-8") as f:
            json.dump(pricebook, f, indent=2)

        print("\n[+] Block 1 Price-Book verified and saved to:", self.pricebook_path)
        print(json.dumps(pricebook, indent=2))

if __name__ == '__main__':
    unittest.main()
