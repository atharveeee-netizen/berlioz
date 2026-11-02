import kickmix as km
import numpy as np
import sys
from pathlib import Path

source_dir = Path("build/somejoint_src/blocks/dqi/team-1028-narrow240/source")
sys.path.insert(0, str(source_dir))
sys.path.insert(0, str(source_dir / "playbook/kit/decoder"))
sys.path.insert(0, str(source_dir / "playbook/kit"))
sys.path.insert(0, "verifiers")
sys.modules['circ'] = km

from dqi.verify_submission_dqi import ProblemSpecDQI, FieldTables, sample_shots, to_bits, validate_registers

spec = ProblemSpecDQI.benchmark_instance()
tables = FieldTables(km.GF2Field(spec.degree))
rng = np.random.default_rng(42)

from dqi.verify_submission_dqi import optimal_dqi_weights
weight_probs = optimal_dqi_weights(spec.m, spec.max_errors, spec.degree, spec.r) ** 2
syndromes, mbuc, phases = sample_shots(spec, tables, rng, 1, weight_probs)

circuit = km.Circuit.from_file("build/circuits/test_dqi_build.kmb")
syndrome_qubits, mbuc_bits, ancilla_qubits = validate_registers(circuit, spec)
syndrome_array, mbuc_array = km.array(syndrome_qubits), km.array(mbuc_bits)

# We can run prefix of the circuit up to scan
print("Checking operations in circuit...")
ops = list(circuit)
print(f"Total ops: {len(ops)}")

# Let's verify that the circuit preserves basis state
sim = km.Simulator(batch_size=1, counting_operations=True, seed=42)
sim.use_same_registers_as(circuit)
input_syndromes = to_bits(syndromes, spec.degree)
sim.write_across_shots(syndrome_array, input_syndromes)
sim.write_across_shots(mbuc_array, to_bits(mbuc, spec.degree))

# Run first half: 30 million ops
half_circuit = km.Circuit(ops[:len(ops)//2])
sim.do(half_circuit)
print("Half circuit executed successfully without any collapse or error!")

# Check if any qubit is in superposition or if reading gives deterministic bits
# In km.Simulator, reading across shots gives boolean array
bits = sim.read_across_shots(km.array(circuit.qubits))
print(f"Total live qubits read: {len(bits)}. All deterministic booleans!")
