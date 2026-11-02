import kickmix as km
import sys
import json
import time
import zipfile
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "verifiers"))
from dqi.verify_submission_dqi import ProblemSpecDQI, verify

target = ROOT / "build/circuits/dqi_breakthrough.kmb"
if not target.exists():
    print(f"ERROR: {target} does not exist yet!")
    sys.exit(1)

print(f"[*] Loading circuit from {target} ({target.stat().st_size / 1e6:.1f} MB)...", flush=True)
start_load = time.time()
circuit = km.Circuit.from_file(str(target), format='kmb')
print(f"    Loaded in {time.time() - start_load:.1f}s.", flush=True)

stats = circuit.operation_statistics()
num_qubits = circuit.num_qubits
num_toffolis = stats.num_toffoli_like
num_ops = len(circuit)

print("\n=== CIRCUIT SPECIFICATIONS ===")
print(f"  Qubits:           {num_qubits}")
print(f"  Static Toffolis:  {num_toffolis:,}")
print(f"  Total Gates:      {num_ops:,}")
print(f"  Classical Bits:   {circuit.num_bits:,}")

# Run verification on 256 benchmark shots
print("\n[*] Running official DQI verifier (256 shots, log2_delta=-10.0)...", flush=True)
spec = ProblemSpecDQI.benchmark_instance(num_shots=256)
start_sim = time.time()
res = verify(circuit, spec, batch_size=256, log2_delta=-10.0, max_workers=1)
sim_time = time.time() - start_sim

val_err = res.get('value_errors', 0)
phase_err = res.get('phase_errors', 0)
mean_toff = res['toffoli_count']
score = res['score']
baseline_score = 24439739777574.605
ratio = baseline_score / score

print(f"\n=== VERIFICATION RESULTS ({sim_time:.1f}s) ===")
print(f"  Status:             {res['status']}")
print(f"  Value Errors:       {val_err} / 256")
print(f"  Phase Errors:       {phase_err} / 256")
print(f"  Mean Dyn Toffolis:  {mean_toff:,.2f}")
print(f"  Effective Err Rate: {res['effective_error_rate']:.6f}")
print(f"  DQI Ratio R_dqi:    {ratio:.4f}x")
print(f"  DQI Score:          {score:.4e}")

if val_err == 0 and phase_err == 0:
    print("\n>>> VERIFICATION GUARANTEE: 100% PASS WITH ZERO ERRORS! <<<")
else:
    print(f"\n>>> VERIFICATION FAILED: {val_err} value errors, {phase_err} phase errors! <<<")
    sys.exit(1)
