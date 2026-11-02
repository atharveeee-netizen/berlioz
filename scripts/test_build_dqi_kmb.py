import kickmix as km
import sys
from pathlib import Path

sys.path.insert(0, "verifiers")
from dqi.verify_submission_dqi import ProblemSpecDQI, verify

circuit = km.Circuit.from_file("build/dqi.kmb")
spec = ProblemSpecDQI.benchmark_instance(num_shots=256)
print("Evaluating build/dqi.kmb on 256 shots...")
res = verify(circuit, spec, batch_size=256, log2_delta=-10.0, max_workers=1)

q = circuit.num_qubits
t = res['toffoli_count']
score = res['score']
baseline_score = 24439739777574.605
ratio = baseline_score / score

print(f"Results for build/dqi.kmb:")
print(f"  Qubits: {q}")
print(f"  Mean Toffolis: {t:,.2f}")
print(f"  Score: {score:.4e}")
print(f"  Benchmark Ratio R_dqi: {ratio:.4f}x")
print(f"  Val errors: {res.get('value_errors', 0)}, Phase errors: {res.get('phase_errors', 0)}")
