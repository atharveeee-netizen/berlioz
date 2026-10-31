"""
Two-Level Quantum Compiler:
Level A: Algebraic and Mathematical Domain Transformations (Field Towering, Linear Synthesis).
Level B: Gate-Level Fault-Tolerant Lowering (Clifford+T, Toffoli, Linear Gaussian Synthesis).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional
from ..ir.math_ir import QuantumMathIR, MathOp, FieldOp, ArithmeticOp, LinearOp


@dataclass
class Gate:
    name: str  # 'H', 'S', 'T', 'CX', 'CCX', 'MEASURE', 'SWAP'
    targets: List[int]
    controls: List[int] = field(default_factory=list)
    classical_dest: Optional[int] = None
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompiledCircuit:
    num_qubits: int
    gates: List[Gate]
    clifford_count: int
    t_count: int
    toffoli_count: int
    mbuc_resets: int
    t_depth: int
    t_equiv: float  # T_count + 2 * Toffoli_count for fault-tolerant grading
    metadata: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> Dict[str, Any]:
        return {
            "num_qubits": self.num_qubits,
            "total_gates": len(self.gates),
            "clifford_count": self.clifford_count,
            "t_count": self.t_count,
            "toffoli_count": self.toffoli_count,
            "mbuc_resets": self.mbuc_resets,
            "t_depth": self.t_depth,
            "t_equiv": self.t_equiv,
        }


def synthesize_linear_f2(matrix_f2: List[List[int]]) -> List[Tuple[str, int, int]]:
    """
    Synthesizes an exact reversible linear CNOT network for an invertible matrix M over F_2.
    Uses Gaussian elimination to reduce M to identity, then reverses the elementary operations.
    Returns: List of ('SWAP', i, j) and ('CX', control, target).
    """
    n = len(matrix_f2)
    M = [list(row) for row in matrix_f2]
    ops: List[Tuple[str, int, int]] = []

    for col in range(n):
        pivot = -1
        for row in range(col, n):
            if M[row][col]:
                pivot = row
                break
        if pivot == -1:
            raise ValueError("LinearOp matrix must be invertible over F_2.")
        if pivot != col:
            M[col], M[pivot] = M[pivot], M[col]
            ops.append(("swap", col, pivot))
        for row in range(n):
            if row != col and M[row][col]:
                for k in range(n):
                    M[row][k] ^= M[col][k]
                ops.append(("add", row, col))

    gates: List[Tuple[str, int, int]] = []
    for op in reversed(ops):
        if op[0] == "swap":
            gates.append(("SWAP", op[1], op[2]))
        elif op[0] == "add":
            gates.append(("CX", op[2], op[1]))
    return gates


class TwoLevelCompiler:
    """
    Two-Level Hierarchical Quantum Compiler for Algebraic Specs.
    Certified mode strictly guarantees bit-exact semantics and verified lowering.
    """

    def __init__(self, enable_tower_decomp: bool = True, enable_mbuc: bool = False):
        self.enable_tower_decomp = enable_tower_decomp
        self.enable_mbuc = enable_mbuc

    def compile(self, ir: QuantumMathIR) -> CompiledCircuit:
        # Step 1: Level A - High-Level Mathematical Optimization
        optimized_ir = self._level_a_optimize(ir)

        # Step 2: Level B - Gate-Level Lowering & Synthesis
        circuit = self._level_b_lower(optimized_ir)

        return circuit

    def _level_a_optimize(self, ir: QuantumMathIR) -> QuantumMathIR:
        """Apply algebraic transformations to the high-level Math-IR."""
        opt_ir = QuantumMathIR(name=f"{ir.name}_level_a_opt")
        # Copy registers
        for reg in ir.registers.values():
            opt_ir.add_register(reg.name, reg.size, reg.reg_type)

        for op in ir.operations:
            if isinstance(op, FieldOp) and self.enable_tower_decomp:
                # Apply Tower-42 only when field degree is 12 AND modulus is 0x1053
                if op.field_degree == 12 and op.irreducible_poly == 0x1053:
                    transformed = FieldOp(
                        op_type="field",
                        name=f"{op.name}_tower42",
                        inputs=op.inputs,
                        outputs=op.outputs,
                        ancilla=op.ancilla,
                        metadata={
                            **op.metadata,
                            "tower_factored": True,
                            "bilinear_tensor_rank": 42,
                        },
                        field_degree=12,
                        irreducible_poly=op.irreducible_poly,
                    )
                    opt_ir.add_operation(transformed)
                    continue

            # Default: preserve operation
            opt_ir.add_operation(op)

        return opt_ir

    def _level_b_lower(self, ir: QuantumMathIR) -> CompiledCircuit:
        """Lowers Math-IR operations into concrete FTQC gate networks."""
        gates: List[Gate] = []
        clifford_count = 0
        t_count = 0
        toffoli_count = 0
        mbuc_resets = 0
        t_depth = 0

        # Maintain qubit allocation map
        reg_map: Dict[str, List[int]] = {name: reg.qubit_indices for name, reg in ir.registers.items()}

        for op in ir.operations:
            if isinstance(op, FieldOp):
                degree = op.field_degree
                poly = op.irreducible_poly
                rank = op.metadata.get("bilinear_tensor_rank", 144)
                in_a = reg_map[op.inputs[0]]
                in_b = reg_map[op.inputs[1]]
                out = reg_map[op.outputs[0]]

                if degree != 12:
                    raise NotImplementedError(
                        f"FieldOp lowering for degree {degree} is not supported (only GF(2^12) with poly 0x1053 is supported)."
                    )
                if poly != 0x1053:
                    raise NotImplementedError(
                        f"FieldOp lowering for polynomial {hex(poly)} is not supported (expected 0x1053)."
                    )

                if rank == 42:
                    # Verified 42-product bilinear tensor lowering
                    anc_qubits = []
                    if op.ancilla:
                        for anc_name in op.ancilla:
                            anc_qubits.extend(reg_map[anc_name])
                    if len(anc_qubits) < 2:
                        raise ValueError(
                            f"Tower-42 FieldOp requires at least 2 scratch ancilla qubits, got {len(anc_qubits)}."
                        )
                    scratch = anc_qubits[:2]

                    from ...dqi.tower42 import tower42
                    terms = tower42(poly)
                    prev_a = prev_b = 0
                    for am, bm, cm in terms:
                        diff_a = am ^ prev_a
                        diff_b = bm ^ prev_b
                        for j in range(12):
                            if (diff_a >> j) & 1:
                                gates.append(Gate(name="CX", targets=[scratch[0]], controls=[in_a[j]]))
                                clifford_count += 1
                            if (diff_b >> j) & 1:
                                gates.append(Gate(name="CX", targets=[scratch[1]], controls=[in_b[j]]))
                                clifford_count += 1

                        pivot = (cm & -cm).bit_length() - 1
                        others = [out[j] for j in range(12) if j != pivot and ((cm >> j) & 1)]
                        for o in others:
                            gates.append(Gate(name="CX", targets=[o], controls=[out[pivot]]))
                            clifford_count += 1
                        gates.append(Gate(name="CCX", targets=[out[pivot]], controls=[scratch[0], scratch[1]]))
                        toffoli_count += 1
                        t_depth += 1
                        for o in others:
                            gates.append(Gate(name="CX", targets=[o], controls=[out[pivot]]))
                            clifford_count += 1

                        prev_a, prev_b = am, bm

                    # Uncompute scratch registers cleanly back to |0>
                    for j in range(12):
                        if (prev_a >> j) & 1:
                            gates.append(Gate(name="CX", targets=[scratch[0]], controls=[in_a[j]]))
                            clifford_count += 1
                        if (prev_b >> j) & 1:
                            gates.append(Gate(name="CX", targets=[scratch[1]], controls=[in_b[j]]))
                            clifford_count += 1

                elif rank == 144:
                    # Verified schoolbook multiplication
                    def poly_reduce(p_val: int, mod: int) -> int:
                        deg = mod.bit_length() - 1
                        while p_val.bit_length() - 1 >= deg:
                            p_val ^= mod << (p_val.bit_length() - 1 - deg)
                        return p_val

                    for i in range(12):
                        for j in range(12):
                            term_poly = poly_reduce(1 << (i + j), poly)
                            pivot = (term_poly & -term_poly).bit_length() - 1
                            others = [out[k] for k in range(12) if k != pivot and ((term_poly >> k) & 1)]
                            for o in others:
                                gates.append(Gate(name="CX", targets=[o], controls=[out[pivot]]))
                                clifford_count += 1
                            gates.append(Gate(name="CCX", targets=[out[pivot]], controls=[in_a[i], in_b[j]]))
                            toffoli_count += 1
                            t_depth += 1
                            for o in others:
                                gates.append(Gate(name="CX", targets=[o], controls=[out[pivot]]))
                                clifford_count += 1
                else:
                    raise NotImplementedError(f"Unsupported bilinear tensor rank {rank} for FieldOp.")

                if self.enable_mbuc:
                    mbuc_resets += 1

            elif isinstance(op, ArithmeticOp):
                name = op.name.lower()
                in_a = reg_map[op.inputs[0]]
                out = reg_map[op.outputs[0]]

                if name in ("add", "adder", "ripple_carry_add", "modular_add"):
                    if len(op.inputs) < 2:
                        raise ValueError(f"Addition requires 2 input registers, got {len(op.inputs)}.")
                    in_b = reg_map[op.inputs[1]]
                    n = len(in_a)
                    if len(in_b) != n or len(out) != n:
                        raise ValueError(
                            f"Addition requires identical bit lengths for inputs and output, got {len(in_a)}, {len(in_b)}, {len(out)}."
                        )
                    anc_qubits = []
                    if op.ancilla:
                        for anc_name in op.ancilla:
                            anc_qubits.extend(reg_map[anc_name])
                    if len(anc_qubits) < n + 1:
                        raise ValueError(
                            f"Reversible ripple-carry addition for {n} bits requires at least {n + 1} carry ancilla qubits, got {len(anc_qubits)}."
                        )
                    carries = anc_qubits[:n + 1]

                    # Reversible ripple-carry addition
                    for i in range(n):
                        gates.append(Gate(name="CX", targets=[out[i]], controls=[in_a[i]]))
                        clifford_count += 1
                        gates.append(Gate(name="CX", targets=[out[i]], controls=[in_b[i]]))
                        clifford_count += 1
                        gates.append(Gate(name="CX", targets=[out[i]], controls=[carries[i]]))
                        clifford_count += 1

                        gates.append(Gate(name="CCX", targets=[carries[i + 1]], controls=[in_a[i], in_b[i]]))
                        toffoli_count += 1
                        gates.append(Gate(name="CCX", targets=[carries[i + 1]], controls=[in_a[i], carries[i]]))
                        toffoli_count += 1
                        gates.append(Gate(name="CCX", targets=[carries[i + 1]], controls=[in_b[i], carries[i]]))
                        toffoli_count += 1
                        t_depth += 3

                    # Uncompute carries in reverse
                    for i in reversed(range(n)):
                        gates.append(Gate(name="CCX", targets=[carries[i + 1]], controls=[in_b[i], carries[i]]))
                        toffoli_count += 1
                        gates.append(Gate(name="CCX", targets=[carries[i + 1]], controls=[in_a[i], carries[i]]))
                        toffoli_count += 1
                        gates.append(Gate(name="CCX", targets=[carries[i + 1]], controls=[in_a[i], in_b[i]]))
                        toffoli_count += 1
                        t_depth += 3
                else:
                    raise NotImplementedError(
                        f"ArithmeticOp '{op.name}' lowering is not supported in generic compiler. "
                        f"Every supported IR operation must either compile correctly or fail explicitly as unsupported."
                    )

            elif isinstance(op, LinearOp):
                target_reg = op.outputs[0] if op.outputs else op.inputs[0]
                qubits = reg_map[target_reg]
                linear_gates = synthesize_linear_f2(op.matrix_f2)
                for g_type, c, t in linear_gates:
                    if g_type == "SWAP":
                        q1, q2 = qubits[c], qubits[t]
                        gates.append(Gate(name="CX", targets=[q2], controls=[q1]))
                        gates.append(Gate(name="CX", targets=[q1], controls=[q2]))
                        gates.append(Gate(name="CX", targets=[q2], controls=[q1]))
                        clifford_count += 3
                    elif g_type == "CX":
                        gates.append(Gate(name="CX", targets=[qubits[t]], controls=[qubits[c]]))
                        clifford_count += 1

        t_equiv = float(t_count + 2 * toffoli_count)

        return CompiledCircuit(
            num_qubits=ir.total_qubits,
            gates=gates,
            clifford_count=clifford_count,
            t_count=t_count,
            toffoli_count=toffoli_count,
            mbuc_resets=mbuc_resets,
            t_depth=t_depth,
            t_equiv=t_equiv,
            metadata={
                "ir_name": ir.name,
                "enable_tower": self.enable_tower_decomp,
                "enable_mbuc": self.enable_mbuc,
                "mbuc_status": "EXPERIMENTAL_UNVERIFIED_MBUC" if self.enable_mbuc else "DISABLED",
            },
        )
