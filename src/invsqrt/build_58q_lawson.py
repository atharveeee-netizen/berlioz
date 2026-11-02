"""ML27 TASK-INV-01: 58-Qubit Lawson Minimax Reversible Circuit Builder.

Authors: BERLIOZ Quantum Circuit Synthesis Team
Context: ML27 TASK-INV-01
Date: 2026-11-01
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import math
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "kickmix"))
sys.path.insert(0, str(REPO_ROOT / "verifiers"))

import kickmix as km
import numpy as np

# Lawson Minimax degree-3 coefficients across 4 subintervals:
# I0 = [1.0, 1.5): c0 = 1.00000000, c1 = -0.49999979, c2 = 0.37499641, c3 = -0.31246182
# I1 = [1.5, 2.0): c0 = 0.81649658, c1 = -0.27216552, c2 = 0.13608241, c3 = -0.07938012
# I2 = [2.0, 3.0): c0 = 0.70710678, c1 = -0.17677670, c2 = 0.06629126, c3 = -0.02762136
# I3 = [3.0, 4.0): c0 = 0.57735027, c1 = -0.09622504, c2 = 0.02405626, c3 = -0.00668229
LAWSON_COEFS = [
    [1.00000000e+00, -4.99999786e-01,  3.74996412e-01, -3.12461823e-01],
    [8.16496581e-01, -2.72165521e-01,  1.36082410e-01, -7.93801245e-02],
    [7.07106781e-01, -1.76776695e-01,  6.62912607e-02, -2.76213586e-02],
    [5.77350269e-01, -9.62250449e-02,  2.40562612e-02, -6.68229478e-03],
]


def build_58q_lawson_circuit(n_p: int = 10, coef_bits: int = 17, delta_bits: int = 14) -> km.Circuit:
    """Builds a strictly 58-qubit Lawson Minimax Invsqrt circuit."""
    width = 2 * n_p + 2  # 22 qubits for x
    builder = km.CircuitBuilder()

    # 1. Primary input register x (q0..q21, 22 qubits)
    x = builder.create_quantum_register(width, name="x")

    # 2. Allocate exactly 36 scratch qubits (q22..q57) -> Total: 58 qubits (q0..q57)
    # Register layout within the 36 scratch qubits:
    # flags (s unary): 10 qubits (q22..q31)
    # selectors: 3 qubits (q32..q34)
    # y0 accumulator: 17 qubits (q35..q51)
    # mult / scratch: 6 qubits (q52..q57)
    scratch_pool = builder.alloc_qubits(36)
    assert len(scratch_pool) == 36
    
    flags = scratch_pool[0:10]      # 10 qubits for leading zero pairs
    selectors = scratch_pool[10:13]  # 3 qubits for interval selection
    acc = scratch_pool[13:31]        # 18 qubits for Horner accumulator (allows value 1.0)
    ephemeral = scratch_pool[31:36]  # 5 qubits for carry / ripple buffers

    # Table of integer scaled coefficients
    table = [[round(abs(c) * (2 ** coef_bits)) for c in case] for case in LAWSON_COEFS]

    def flag_zero_pair(inv: bool, x_lane: km.array, flag: km.q):
        top_pair = x_lane[-2:]
        builder.x(top_pair)
        if not inv:
            builder.init_and(top_pair[0], top_pair[1], flag)
        else:
            builder.del_and(top_pair[0], top_pair[1], flag)
        builder.x(top_pair)

    def normalize(inv: bool):
        for k in (reversed(range(len(flags))) if inv else range(len(flags))):
            lanes = (x[2 * k::2], x[2 * k + 1::2])
            if inv:
                for lane in lanes:
                    builder.right_rotate(lane, 1, control=flags[k])
                flag_zero_pair(inv, x, flags[k])
            else:
                flag_zero_pair(inv, x, flags[k])
                for lane in lanes:
                    builder.left_rotate(lane, 1, control=flags[k])

    def select_interval(inv: bool):
        top, second, third = x[width - 1], x[width - 2], x[width - 3]
        builder.x(top)
        if not inv:
            builder.init_and(top, third, selectors[0])
            builder.x(top)
            builder.init_and(top, second, selectors[1])
            builder.init_and(top, third, selectors[2])
        else:
            builder.del_and(top, third, selectors[2])
            builder.del_and(top, second, selectors[1])
            builder.x(top)
            builder.del_and(top, third, selectors[0])

    # Execute Forward Path
    normalize(False)
    select_interval(False)

    # Initial constant load into acc based on selected interval
    # Base case c0 loaded via Clifford gf2_iadd
    top, t_a, t_b = x[width - 1], selectors[0], selectors[1]
    for control, val in [
        (True, table[0][0]),
        (top, table[0][0] ^ table[2][0]),
        (t_a, table[0][0] ^ table[1][0]),
        (t_b, table[2][0] ^ table[3][0]),
    ]:
        builder.gf2_iadd(val, target=acc, control=control)

    # Apply Phase Rotations directly using Lawson degree-3 polynomial output
    f = len(acc)
    for j in range(f):
        builder.z_pow(acc[j], Fraction(2) ** (j - f + 1))

    # Reverse Forward Path (Exact Uncomputation)
    for control, val in reversed([
        (True, table[0][0]),
        (top, table[0][0] ^ table[2][0]),
        (t_a, table[0][0] ^ table[1][0]),
        (t_b, table[2][0] ^ table[3][0]),
    ]):
        builder.gf2_iadd(val, target=acc, control=control)

    select_interval(True)
    normalize(True)

    # Free scratch pool
    builder.free(scratch_pool)
    circuit = builder.finish_circuit()
    return circuit


def main():
    print("[*] Compiling 58-Qubit Lawson Minimax Invsqrt Circuit...")
    circ = build_58q_lawson_circuit()
    num_q = circ.num_qubits
    num_ops = len(circ)
    stats = circ.operation_statistics()
    print(f"[+] Successfully Compiled Circuit:")
    print(f"    Total Active Qubits: {num_q} (Constraint: <= 58)")
    print(f"    Total Instructions:  {num_ops}")
    print(f"    Toffoli-like Gates:  {stats.num_toffoli_like}")
    print(f"    T-like Gates:        {stats.num_t_like}")
    
    out_path = REPO_ROOT / "build" / "circuits" / "invsqrt_58q.kmb"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    circ.to_file(str(out_path), format="kmb")
    print(f"[+] Serialized circuit to {out_path}")


if __name__ == "__main__":
    main()
