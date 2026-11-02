import kickmix as km
import numpy as np

# Test HMR phase kickback cancellation:
# Suppose we have an ancilla qubit a initialized to |0>.
# We do some operations, then measure a with HMR into bit m.
# If we do b.z(m), what does that do to the state?
b = km.CircuitBuilder()
q = b.alloc_qubits(1)[0]
m = b.alloc_bits(1)[0]

b.hmr(q, m)
# In Kickmix, b.z(m) applies a Z gate to the classical bit m, which flips global phase by (-1)^m!
b.z(m)
b.free(m)
b.free(q)

c = b.finish_circuit()
sim = km.Simulator(batch_size=10, seed=42)
sim.use_same_registers_as(c)
sim.do(c)
phase = sim.read_phase_flipped_across_shots()
print("Phase with b.z(m):", phase)

