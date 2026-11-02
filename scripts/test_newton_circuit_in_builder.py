import kickmix as km
import numpy as np
import sys
from pathlib import Path

source_dir = Path("build/somejoint_src/blocks/dqi/team-1028-narrow240/source")
sys.path.insert(0, str(source_dir))
sys.path.insert(0, str(source_dir / "playbook/kit/decoder"))
sys.path.insert(0, str(source_dir / "playbook/kit"))
sys.modules['circ'] = km

from exp.decoder.common import ar

field = km.GF2Field(12)

# Verify on a 4-word toy case first to test the circuit logic:
b = km.CircuitBuilder()

# 4 syndrome words, each 12 bits
# Suppose Lambda = [1, L1, L2], Omega = [O0, O1]
# We have 2 words of Omega: W_Omega = [b.alloc_qubits(12) for _ in range(2)]
# and 2 words of Lambda: W_Lambda = [b.alloc_qubits(12) for _ in range(2)]

W_Omega = [b.alloc_qubits(12) for _ in range(2)]
W_Lambda = [b.alloc_qubits(12) for _ in range(2)]

# Set initial values in W_Omega and W_Lambda:
# e.g. L1 = 3, L2 = 5, O0 = 7, O1 = 11
for i in ar.bits(7): b.x(W_Omega[0][i])
for i in ar.bits(11): b.x(W_Omega[1][i])
for i in ar.bits(3): b.x(W_Lambda[0][i])
for i in ar.bits(5): b.x(W_Lambda[1][i])

# Recurrence:
# S0 = O0 = W_Omega[0] (already holds O0!)
# S1 = O1 ^ (L1 * S0)
# XOR L1 * S0 into W_Omega[1]:
ar.mul_xor0(b, W_Lambda[0], W_Omega[0], W_Omega[1])

# Finish circuit
c = b.finish_circuit()

sim = km.Simulator(batch_size=1)
sim.use_same_registers_as(c)
sim.do(c)

def read_word(reg):
    bits = sim.read_across_shots(km.array(reg)).flatten()
    return sum(int(bit) << i for i, bit in enumerate(bits))

s0 = read_word(W_Omega[0])
s1 = read_word(W_Omega[1])

expected_s0 = 7
expected_s1 = field.add(11, field.mul(3, 7))

print(f"S0: got {s0}, expected {expected_s0} -> MATCH: {s0 == expected_s0}")
print(f"S1: got {s1}, expected {expected_s1} -> MATCH: {s1 == expected_s1}")
