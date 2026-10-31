"""
Mathematical Intermediate Representation (Math-IR) for quantum arithmetic and circuit synthesis.
Preserves high-level algebraic semantics (finite-field arithmetic, modular structures,
polynomial series) before lowering into fault-tolerant Clifford+T or Toffoli networks.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
import json


@dataclass
class Register:
    """Logical quantum or classical register."""
    name: str
    size: int
    reg_type: str = "quantum"  # 'quantum', 'ancilla', 'dirty', 'classical'
    qubit_indices: List[int] = field(default_factory=list)


@dataclass
class MathOp:
    """Base class for mathematical operations in Math-IR."""
    op_type: str
    name: str
    inputs: List[str]
    outputs: List[str]
    ancilla: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "op_type": self.op_type,
            "name": self.name,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "ancilla": self.ancilla,
            "metadata": self.metadata,
        }


@dataclass
class FieldOp(MathOp):
    """Finite-field algebraic operation (e.g., GF(2^k))."""
    field_degree: int = 12
    irreducible_poly: int = 0x1053  # Standard x^12 + x^6 + x^4 + x + 1

    def __post_init__(self):
        self.op_type = "field"
        self.metadata.update({
            "degree": self.field_degree,
            "poly": hex(self.irreducible_poly),
        })


@dataclass
class ArithmeticOp(MathOp):
    """Elementary and modular arithmetic operation (add, multiply, divsteps, invsqrt)."""
    precision_bits: int = 16
    modulus: Optional[int] = None

    def __post_init__(self):
        self.op_type = "arithmetic"
        self.metadata.update({
            "precision": self.precision_bits,
            "modulus": self.modulus,
        })


@dataclass
class LinearOp(MathOp):
    """Linear reversible boolean transformation over F_2."""
    matrix_f2: List[List[int]] = field(default_factory=list)

    def __post_init__(self):
        self.op_type = "linear"
        self.metadata["dim"] = len(self.matrix_f2)


class QuantumMathIR:
    """High-level quantum mathematical program representation."""

    def __init__(self, name: str = "berlioz_ir_program"):
        self.name: str = name
        self.registers: Dict[str, Register] = {}
        self.operations: List[MathOp] = []
        self._next_qubit_idx: int = 0

    def add_register(self, name: str, size: int, reg_type: str = "quantum") -> Register:
        if name in self.registers:
            raise ValueError(f"Register '{name}' already declared.")
        indices = list(range(self._next_qubit_idx, self._next_qubit_idx + size))
        self._next_qubit_idx += size
        reg = Register(name=name, size=size, reg_type=reg_type, qubit_indices=indices)
        self.registers[name] = reg
        return reg

    def add_operation(self, op: MathOp) -> None:
        # Validate that referenced registers exist
        all_refs = op.inputs + op.outputs + op.ancilla
        for r in all_refs:
            if r not in self.registers:
                raise KeyError(f"Operation references unknown register: '{r}'")
        self.operations.append(op)

    @property
    def total_qubits(self) -> int:
        return sum(reg.size for reg in self.registers.values() if reg.reg_type != "classical")

    @property
    def ancilla_qubits(self) -> int:
        return sum(reg.size for reg in self.registers.values() if reg.reg_type in ("ancilla", "dirty"))

    def summary(self) -> Dict[str, Any]:
        op_counts: Dict[str, int] = {}
        for op in self.operations:
            op_counts[op.op_type] = op_counts.get(op.op_type, 0) + 1
        return {
            "name": self.name,
            "total_qubits": self.total_qubits,
            "ancilla_qubits": self.ancilla_qubits,
            "num_operations": len(self.operations),
            "op_breakdown": op_counts,
            "registers": {name: {"size": r.size, "type": r.reg_type} for name, r in self.registers.items()},
        }

    def to_json(self) -> str:
        data = {
            "name": self.name,
            "registers": [
                {"name": r.name, "size": r.size, "reg_type": r.reg_type, "indices": r.qubit_indices}
                for r in self.registers.values()
            ],
            "operations": [op.to_dict() for op in self.operations],
        }
        return json.dumps(data, indent=2)
