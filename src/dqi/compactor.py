"""
=============================================================================
TURINGIRL QUANTUM: DQI WIRE COMPACTOR & ANCILLA POOL (STAGE 7 PROTOTYPE)
Dynamic wire pool reuse to reduce peak live qubits Q in GF(2^12) decoders
=============================================================================
"""

import kickmix as km
from src.dqi.tower42 import FullTowerBuilder, order_terms

class PooledTowerBuilder(FullTowerBuilder):
    """
    Enhanced FullTowerBuilder with an integrated scratch wire pool.
    Instead of allowing transient operations (ixor_gf2_mul, del_product) to
    allocate fresh wire indices from the CircuitBuilder, operations draw from
    a dedicated, reusable local ancilla pool.
    """
    def __init__(self, builder, km_mod, terms, field, pool_size: int = 16):
        super().__init__(builder, km_mod, terms, field)
        self.raw_builder = builder
        self._pool_size = pool_size
        self._pool = None
        self._pool_in_use = False

    def _ensure_pool(self):
        if self._pool is None:
            self._pool = self.raw_builder.alloc_qubits(self._pool_size)

    def borrow_scratch(self, count: int):
        self._ensure_pool()
        if not self._pool_in_use and count <= self._pool_size:
            self._pool_in_use = True
            return self._pool[:count], True
        # Fallback to standard allocation if pool is already in use
        return self.raw_builder.alloc_qubits(count), False

    def return_scratch(self, wires, from_pool: bool):
        if from_pool:
            self._pool_in_use = False
        else:
            self.raw_builder.free(wires)

    def ixor_gf2_mul(self, lhs, rhs, *, target, field, control=True, tensor=None):
        b, km = self.raw, self.km
        if field.degree != 12 or field.modulus != self.modulus or isinstance(lhs, int) or isinstance(rhs, int):
            return b.ixor_gf2_mul(lhs, rhs, target=target, field=field, control=control)
        if control is False:
            return
        assert len(lhs) == len(rhs) == len(target) == 12
        assert not (set(target) & (set(lhs) | set(rhs)))
        masked = None
        if control is not True:
            masked = b.alloc_qubits(12)
            b.init_and(control, lhs, masked)
            original_lhs, lhs = lhs, masked

        # Borrow 2 scratch qubits from pool
        scratch, from_pool = self.borrow_scratch(2)
        previous_a = previous_b = 0
        for am, bm, cm in (self.terms if tensor is None else tensor):
            left = km.array([lhs[j] for j in range(12) if ((am ^ previous_a) >> j) & 1])
            right = km.array([rhs[j] for j in range(12) if ((bm ^ previous_b) >> j) & 1])
            b.cx(left, scratch[0])
            b.cx(right, scratch[1])
            pivot = (cm & -cm).bit_length() - 1
            others = km.array([target[j] for j in range(12) if j != pivot and (cm >> j) & 1])
            if len(others):
                b.cx(target[pivot], others)
            b.ccx(scratch[0], scratch[1], target[pivot])
            if len(others):
                b.cx(target[pivot], others)
            previous_a, previous_b = am, bm
        b.cx(km.array([rhs[j] for j in range(12) if (previous_b >> j) & 1]), scratch[1])
        b.cx(km.array([lhs[j] for j in range(12) if (previous_a >> j) & 1]), scratch[0])
        self.return_scratch(scratch, from_pool)

        if masked is not None:
            b.del_and(control, original_lhs, masked)
            b.free(masked)
        self.replacements += 1
