"""
=============================================================================
TURINGIRL QUANTUM: QUADRATIC-PHASE ERASURE (BLOCK 3)
Zero-Toffoli Uncomputation of Bilinear & Quadratic Registers via HMR + CZ
=============================================================================
"""

import kickmix as km

class QuadraticPhaseEraser:
    """
    Erases intermediate quadratic / bilinear registers using X-basis Measurement
    and Reset (HMR) combined with a Clifford CZ phase correction network.
    
    Theorem:
    If target bit y is a degree-2 Boolean function in surviving register wires x:
        y = sum_{(i,j) in E} x_i * x_j  (mod 2)
    Then executing HMR(y -> b) followed by controlled CZ(x_i, x_j) for all (i,j) in E
    restores y cleanly to |0> with identity phase transformation across all computational
    basis inputs, incurring EXACTLY ZERO Toffoli-like gate cost.
    """

    @staticmethod
    def erase_and_pair(builder: km.CircuitBuilder, target_qubit: km.q, x0: km.q, x1: km.q, bit_reg: km.b):
        """
        Erases an AND-target y = x0 * x1 with zero Toffolis.
        """
        builder.hmr(target_qubit, bit_reg)
        builder.push_condition(bit_reg)
        builder.cz(x0, x1)
        builder.pop_condition()

    @staticmethod
    def erase_bilinear_form(builder: km.CircuitBuilder, target_qubit: km.q, terms: list[tuple[km.q, km.q]], bit_reg: km.b):
        """
        Erases an arbitrary bilinear form y = sum_{(i,j)} x_i * x_j with zero Toffolis.
        """
        builder.hmr(target_qubit, bit_reg)
        builder.push_condition(bit_reg)
        for q_i, q_j in terms:
            builder.cz(q_i, q_j)
        builder.pop_condition()
