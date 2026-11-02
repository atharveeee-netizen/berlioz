import sys
from pathlib import Path
import numpy as np

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT / "verifiers"))

from dfthcsos.verify import load_inputs, evaluate_dfthc_angle_words, heuristic_costs, resource_costs
from dfthcsos.scoreinfra.circuits import load_circuits, recover_words_from_circuits

chem_dir = ROOT / "build/ml30_apex_optimum/dfthcsos"
inputs = load_inputs(chem_dir / "submission.npz")
print(f"Loaded chemistry: w.shape={inputs.w.shape}, orbitals={inputs.num_orbitals}")

# Let's inspect the current submission's metrics with evaluate_dfthc_angle_words
from dfthcsos.scoreinfra.dfthc_math import symmetric_from_lower
from dfthcsos.scoreinfra.reference import check_fcidump, load_reference

ref = load_reference(check_fcidump())
w = inputs.w
W = inputs.W
S = inputs.S
beta_1 = inputs.beta_1

circuits = load_circuits(chem_dir)
print(f"Loaded {len(circuits)} circuits")

words, angles_toffoli = recover_words_from_circuits(circuits)
print(f"angles_toffoli = {angles_toffoli}")

# Now let's evaluate words with different brot
from dfthcsos.scoreinfra.dfthc_math import evaluate_dfthc_angle_words

for b in [10, 9, 8, 7]:
    metrics = evaluate_dfthc_angle_words(inputs.ref, w, W, S, beta_1, words, brot=b)
    res = resource_costs(inputs, circuits, b, angles_toffoli)
    pass_acc = (metrics['error_1'] <= 0.020 and metrics['error_2'] <= 0.020 and metrics['gap_in_domain'] and metrics['lambda_eff'] >= 0)
    score = float(metrics['lambda_eff']) * float(res['toffoli']) * int(res['qubits']) if pass_acc else float('inf')
    print(f"brot={b:2d}: e1={metrics['error_1']*1000:7.3f} mHa, e2={metrics['error_2']*1000:7.3f} mHa, lambda={metrics['lambda_eff']:.4f}, Q={res['qubits']}, T={res['toffoli']:,}, Score={score:,.0f}, Status={'PASS' if pass_acc else 'FAIL'}")
