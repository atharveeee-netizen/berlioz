import kickmix as km
import numpy as np
import sys
from pathlib import Path

source_dir = Path("build/somejoint_src/blocks/dqi/team-1028-narrow240/source")
sys.path.insert(0, str(source_dir))
sys.path.insert(0, str(source_dir / "playbook/kit/decoder"))
sys.path.insert(0, str(source_dir / "playbook/kit"))
sys.modules['circ'] = km

from exp.decoder.common import *

# Let's test GF(2^12) multiplication circuit:
b = km.CircuitBuilder()
x = b.alloc_qubits(12)
y = b.alloc_qubits(12)
z = b.alloc_qubits(12)

# Set x = 5, y = 7
for i in ar.bits(5): b.x(x[i])
for i in ar.bits(7): b.x(y[i])

# Multiply: z ^= x * y
ar.mul_xor0(b, x, y, z)

c = b.finish_circuit()
stats = c.operation_statistics()
print("mul_xor0 stats:", stats)
print("Toffolis for 1 multiplication:", stats.num_toffoli_like)
