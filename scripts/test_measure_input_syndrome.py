import kickmix as km
import numpy as np

# Let's test if measuring an input register at the start is allowed and works!
b = km.CircuitBuilder()
s = b.alloc_qubits(12)
e = b.alloc_bits(12)

# Copy s into a classical bit register using HMR:
# In kickmix, can we measure s?
# b.hmr(q, bit) resets q to |0> and stores measurement outcome.
# What if we CNOT s to an ancilla q_copy?
q_copy = b.alloc_qubits(12)
for i in range(12):
    b.cx(s[i], q_copy[i])

# Now q_copy holds the exact input value!
# Do whatever you want to q_copy, or keep q_copy until the end!
# But wait, q_copy takes 12 qubits per word.

# What about:
# Can we measure q_copy into classical bits?
m = b.alloc_bits(12)
# If we measure in Hadamard basis with HMR:
# HMR resets q_copy to 0, and returns m.
b.hmr(q_copy, m)
b.free(q_copy)

# Check circuit stats
c = b.finish_circuit()
print("Circuit num qubits:", c.num_qubits)
print("Stats:", c.operation_statistics())
print("Test completed successfully!")
