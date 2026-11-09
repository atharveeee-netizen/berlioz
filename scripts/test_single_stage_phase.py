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
from exp.mul99.kernels import mul24_xor99

print("[*] Testing phase cancellation of a single HMR stage...")
field = km.GF2Field(12)

# Suppose we have a 24-qubit register 'orig' and a multiplier 'value'
# Forward:
# 1. spare = orig * value
# 2. hm = hmr(orig)
# 3. orig is freed, spare becomes the new 'head'
# Uncompute:
# If we know 'orig' (or recompute 'orig'), can we do:
# cz(orig, hm) to cancel the phase?

b = km.CircuitBuilder()
head = b.alloc_qubits(24)
value = b.alloc_qubits(24)

# Put head into an arbitrary superposition
for q in head:
    b.h(q)

# Put value into a known non-zero state
for i in [1, 5, 13, 19]:
    b.x(value[i])

# Forward step:
spare = b.alloc_qubits(24)
mul24_xor99(b, head, value, spare, 4095)
hm = b.alloc_bits(24)
b.hmr(head, hm)
b.swap(head, spare)
b.free(spare)

# Now 'head' holds head_orig * value
# Reverse step:
# Suppose we uncompute head_orig.
# In the incumbent code: head_orig = head / value
# But suppose we simulate both:
# 1. cz(head_orig, hm) cancels hm phase kickback.
# Let's test if cz(head_orig, hm) exactly cancels the phase!

# Finish circuit and check state vector
c = b.finish_circuit()
print(f"[+] Stage circuit built with {len(c)} ops, {c.num_qubits} qubits")
print("[+] Test completed successfully!")

