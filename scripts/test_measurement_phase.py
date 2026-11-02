import kickmix as km
import numpy as np

# Test 1: Phase applied before measurement
b = km.CircuitBuilder()
q_in = b.alloc_qubits(1)[0]
q_anc = b.alloc_qubits(1)[0]
c_bit = b.alloc_bits(1)[0]

# Initial basis state: q_in = 1
# Apply phase: Z on q_in -> gives phase -1
b.z(q_in)

# Compute ancilla: CX(q_in, q_anc) -> q_anc = 1
b.cx(q_in, q_anc)

# Measure q_anc in Hadamard basis (HMR) or Z basis
m = b.alloc_bits(1)[0]
b.hmr(q_anc, m)
# When measuring |1> in H basis: |1> = (|0> - |1>)/sqrt(2)
# HMR outcomes are random +1/-1 with phase kickback!
# To restore phase kickback:
b.cz(q_in, m) # if needed

c = b.finish_circuit()

sim = km.Simulator(batch_size=1, counting_operations=True, seed=42)
sim.use_same_registers_as(c)
sim.write_across_shots(km.array([q_in]), np.array([[True]]))
sim.do(c)

print("Phase flipped:", sim.read_phase_flipped_across_shots())
print("Test 1 completed!")
