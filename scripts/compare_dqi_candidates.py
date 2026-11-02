import kickmix as km
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, "verifiers")
from dqi.verify_submission_dqi import ProblemSpecDQI, verify

spec = ProblemSpecDQI.benchmark_instance(num_shots=256)

candidates = [
    ("BusyaPrime 892Q", "build/harvest_busyaprime/dqi.kmb"),
    ("Narrow240 Retimed 889Q", "build/circuits/test_dqi_build.kmb"),
]

for name, path in candidates:
    print(f"\n--- Testing {name} ({path}) on 256 shots ---", flush=True)
    circuit = km.Circuit.from_file(path)
    res = verify(circuit, spec, batch_size=256, log2_delta=-10.0, max_workers=1)
    q = circuit.num_qubits
    toffolis = res['toffoli_count']
    score = res['score']
    # Baseline benchmark score is ~2.44397e13
    baseline_score = 24439739777574.605
    ratio = baseline_score / score
    print(f"  Qubits: {q}", flush=True)
    print(f"  Mean Toffolis/shot: {toffolis:,.2f}", flush=True)
    print(f"  Score: {score:.4e}", flush=True)
    print(f"  Benchmark Ratio R_dqi: {ratio:.4f}x", flush=True)
    print(f"  Val errors: {res.get('value_errors', 0)}, Phase errors: {res.get('phase_errors', 0)}", flush=True)
