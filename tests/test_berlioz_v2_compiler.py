"""Unit tests for Berlioz 2.0 Math-IR, Two-Level Compiler, Phase Polynomials, and Formal Verifier.
Verifies compiler correctness, tensor lowering, reversibility, ancilla cleanup, and error boundaries.
SPDX-License-Identifier: Apache-2.0
"""
import unittest
import numpy as np

from src.berlioz_v2.ir.math_ir import QuantumMathIR, FieldOp, ArithmeticOp, LinearOp, Register
from src.berlioz_v2.compiler.two_level_compiler import TwoLevelCompiler, synthesize_linear_f2
from src.berlioz_v2.phase_optimizer.phase_poly import PhasePolynomialOptimizer, PauliCorrection
from src.berlioz_v2.verification.formal_verifier import FormalVerifier, simulate_circuit_boolean, simulate_circuit_unitary
from src.berlioz_v2.discovery.arch_generator import ArchitectureGenerator


class TestBerliozV2Compiler(unittest.TestCase):
    def setUp(self):
        self.compiler = TwoLevelCompiler(enable_tower_decomp=True, enable_mbuc=False)

    def test_math_ir_validation_unknown_register(self):
        ir = QuantumMathIR("test_unknown")
        ir.add_register("a", 12)
        with self.assertRaises(KeyError):
            ir.add_operation(FieldOp(name="gf", inputs=["a", "nonexistent"], outputs=["a"]))

    def test_math_ir_validation_field_degree_mismatch(self):
        ir = QuantumMathIR("test_degree_mismatch")
        ir.add_register("a", 10)
        ir.add_register("b", 12)
        ir.add_register("out", 12)
        with self.assertRaises(ValueError):
            ir.add_operation(FieldOp(name="gf", inputs=["a", "b"], outputs=["out"], field_degree=12))

    def test_math_ir_validation_linear_non_square(self):
        ir = QuantumMathIR("test_linear_non_square")
        ir.add_register("x", 3)
        with self.assertRaises(ValueError):
            ir.add_operation(LinearOp(name="lin", inputs=["x"], outputs=["x"], matrix_f2=[[1, 0, 1], [0, 1]]))

    def test_two_level_compiler_tower42_circuit_equivalence(self):
        ir = QuantumMathIR("tower42_comp")
        ir.add_register("a", 12, "quantum")
        ir.add_register("b", 12, "quantum")
        ir.add_register("out", 12, "quantum")
        ir.add_register("scratch", 4, "ancilla")
        ir.add_operation(FieldOp(
            name="gf_mul",
            inputs=["a", "b"],
            outputs=["out"],
            ancilla=["scratch"],
            field_degree=12,
            irreducible_poly=0x1053,
            metadata={"bilinear_tensor_rank": 42}
        ))
        circuit = self.compiler.compile(ir)
        self.assertEqual(circuit.toffoli_count, 42)
        self.assertEqual(circuit.num_qubits, 40)

        in_a = ir.registers["a"].qubit_indices
        in_b = ir.registers["b"].qubit_indices
        out = ir.registers["out"].qubit_indices
        anc = ir.registers["scratch"].qubit_indices

        res = FormalVerifier.verify_compiled_galois_field(
            circuit, in_a, in_b, out, anc, degree=12, poly=0x1053, num_trials=60
        )
        self.assertTrue(res.passed, f"Tower-42 verification failed: {res.failure_details}")

    def test_two_level_compiler_schoolbook_gf_circuit(self):
        ir = QuantumMathIR("schoolbook_comp")
        ir.add_register("a", 12, "quantum")
        ir.add_register("b", 12, "quantum")
        ir.add_register("out", 12, "quantum")
        ir.add_operation(FieldOp(
            name="gf_naive",
            inputs=["a", "b"],
            outputs=["out"],
            field_degree=12,
            irreducible_poly=0x1053,
            metadata={"bilinear_tensor_rank": 144}
        ))
        compiler_naive = TwoLevelCompiler(enable_tower_decomp=False)
        circuit = compiler_naive.compile(ir)
        self.assertEqual(circuit.toffoli_count, 144)

        in_a = ir.registers["a"].qubit_indices
        in_b = ir.registers["b"].qubit_indices
        out = ir.registers["out"].qubit_indices

        res = FormalVerifier.verify_compiled_galois_field(
            circuit, in_a, in_b, out, [], degree=12, poly=0x1053, num_trials=30
        )
        self.assertTrue(res.passed, f"Schoolbook verification failed: {res.failure_details}")

    def test_two_level_compiler_linear_synthesis(self):
        M = [
            [1, 0, 1, 0],
            [0, 1, 1, 0],
            [1, 1, 0, 1],
            [0, 0, 1, 1]
        ]
        ir = QuantumMathIR("lin_comp")
        ir.add_register("x", 4, "quantum")
        ir.add_operation(LinearOp(name="linear_test", inputs=["x"], outputs=["x"], matrix_f2=M))

        circuit = self.compiler.compile(ir)
        qubits = ir.registers["x"].qubit_indices
        res = FormalVerifier.verify_compiled_linear_matrix(circuit, M, qubits)
        self.assertTrue(res.passed, f"Linear synthesis verification failed: {res.failure_details}")

    def test_two_level_compiler_ripple_carry_adder(self):
        n = 4
        ir = QuantumMathIR("adder_comp")
        ir.add_register("a", n, "quantum")
        ir.add_register("b", n, "quantum")
        ir.add_register("out", n, "quantum")
        ir.add_register("carries", n + 1, "ancilla")
        ir.add_operation(ArithmeticOp(
            name="ripple_carry_add",
            inputs=["a", "b"],
            outputs=["out"],
            ancilla=["carries"],
            precision_bits=n
        ))
        circuit = self.compiler.compile(ir)
        in_a = ir.registers["a"].qubit_indices
        in_b = ir.registers["b"].qubit_indices
        out = ir.registers["out"].qubit_indices
        carries = ir.registers["carries"].qubit_indices

        res = FormalVerifier.verify_compiled_adder(circuit, in_a, in_b, out, carries, n_bits=n)
        self.assertTrue(res.passed, f"Adder verification failed: {res.failure_details}")

    def test_two_level_compiler_explicit_failure_unsupported(self):
        ir = QuantumMathIR("fail_arithmetic")
        ir.add_register("a", 4)
        ir.add_register("out", 4)
        ir.add_operation(ArithmeticOp(name="arbitrary_unsupported", inputs=["a"], outputs=["out"]))
        with self.assertRaises(NotImplementedError):
            self.compiler.compile(ir)

    def test_phase_polynomial_optimizer_mbuc_pauli_feedforward(self):
        opt = PhasePolynomialOptimizer(num_qubits=4)
        # Add a linear parity phase term: exp(i * pi * (x_1 ^ x_2))
        opt.add_term([1, 2], angle_mult_pi_over_4=4)
        # Measure ancilla qubit 2 with data qubit 1
        res = opt.apply_mbuc_uncomputation(ancilla_mask=(1 << 2), allow_experimental_mbuc=False)
        self.assertTrue(res.is_exact_clifford)
        self.assertEqual(len(res.corrections), 1)
        corr = res.corrections[0]
        self.assertEqual(corr.target_qubit, 1)
        self.assertEqual(corr.pauli, "Z")
        self.assertEqual(corr.condition_meas_qubit, 2)

    def test_phase_polynomial_optimizer_non_linear_mbuc_rejection(self):
        opt = PhasePolynomialOptimizer(num_qubits=4)
        # Non-linear phase term: exp(i * pi/4 * (x_0 ^ x_1 ^ x_2))
        opt.add_term([0, 1, 2], angle_mult_pi_over_4=1)
        # Measuring ancilla 2 should fail under certified mode without experimental flag
        with self.assertRaises(ValueError):
            opt.apply_mbuc_uncomputation(ancilla_mask=(1 << 2), allow_experimental_mbuc=False)

    def test_architecture_discovery(self):
        gen = ArchitectureGenerator(random_seed=42)
        field_cands = gen.generate_field_mult_candidates(field_degree=12)
        self.assertGreaterEqual(len(field_cands), 3)
        arith_cands = gen.generate_arithmetic_candidates(precision_bits=8)
        self.assertGreaterEqual(len(arith_cands), 1)


if __name__ == "__main__":
    unittest.main()
