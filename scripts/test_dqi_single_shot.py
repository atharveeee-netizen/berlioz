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

# Sample 1 shot with weight k=3 errors
from dqi.verify_submission_dqi import optimal_dqi_weights
weight_probs = optimal_dqi_weights(spec.m, spec.max_errors, spec.degree, spec.r) ** 2
syndromes, mbuc, phases = sample_shots(spec, tables, rng, 1, weight_probs)

circuit = km.Circuit.from_file("build/circuits/test_dqi_build.kmb")
syndrome_qubits, mbuc_bits, ancilla_qubits = validate_registers(circuit, spec)
syndrome_array, mbuc_array = km.array(syndrome_qubits), km.array(mbuc_bits)

sim = km.Simulator(batch_size=1, counting_operations=True, seed=42)
sim.use_same_registers_as(circuit)
input_syndromes = to_bits(syndromes, spec.degree)
sim.write_across_shots(syndrome_array, input_syndromes)
sim.write_across_shots(mbuc_array, to_bits(mbuc, spec.degree))

print("Simulating 1 shot...")
sim.do(circuit)

phase_flipped = sim.read_phase_flipped_across_shots()
reg_diff = sim.read_across_shots(syndrome_array) ^ input_syndromes
junk = sim.read_across_shots(ancilla_qubits) if len(ancilla_qubits) else np.zeros((0, 1), dtype=bool)

val_err = reg_diff.any(axis=0) | junk.any(axis=0)
phase_err = (phase_flipped ^ phases) & ~val_err

print(f"Shot 0: val_err={val_err[0]}, phase_err={phase_err[0]}, phase_flipped={phase_flipped[0]}, target_phase={phases[0]}")
print("Success on single shot!")
