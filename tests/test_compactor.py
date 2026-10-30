import unittest
import numpy as np
import kickmix as km
from src.dqi.tower42 import tower42
from src.dqi.compactor import PooledTowerBuilder

class TestCompactor(unittest.TestCase):
    def test_pooled_multiplication_correctness(self):
        field = km.GF2Field(12)
        terms = tower42(field.modulus)

        for a, b in [(1, 1), (0xABC, 0x123), (4095, 2)]:
            expected = field.mul(a, b)

            builder_raw = km.CircuitBuilder()
            builder = PooledTowerBuilder(builder_raw, km, terms, field, pool_size=4)

            lhs = builder.alloc_qubits(12)
            rhs = builder.alloc_qubits(12)
            target = builder.alloc_qubits(12)

            for j in range(12):
                if (a >> j) & 1: builder.x(lhs[j])
                if (b >> j) & 1: builder.x(rhs[j])

            builder.ixor_gf2_mul(lhs, rhs, target=target, field=field)

            c = builder.finish_circuit()
            sim = km.Simulator(1, counting_operations=True)
            sim.do(c)

            res = sum(int(sim.read_within_shot(target[j], 0)) << j for j in range(12))
            self.assertEqual(res, expected, f"Multiplication error for {hex(a)} * {hex(b)}: got {hex(res)}, expected {hex(expected)}")
            self.assertEqual(c.operation_statistics().num_toffoli_like, 42)

if __name__ == '__main__':
    unittest.main()
