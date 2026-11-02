import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "verifiers"))
import numpy as np
from dfthcsos.verify import load_inputs, evaluate_words

candidates = [
    'fact/fact_candidate_ml27.npz',
    'fact/r8_champion/submission.npz',
    'fact/dfthc_r10_b129_c60_brot8.npz',
    'build/dfthcsos/test_lam.npz',
]

for path in candidates:
    try:
        data = np.load(path)
        inp = load_inputs(path)
        words = data['angle_words']
        edges = data['tree_edges']
        brot = int(data['brot']) if 'brot' in data else 8
        res = evaluate_words(inp, words, edges, brot)
        u_shape = inp.params['U'].shape
        w_shape = inp.params['W'].shape
        print(f"=== {path} ===")
        print(f"  Rank R: {u_shape[0]}, B: {u_shape[1]}, C: {w_shape[2]}")
        print(f"  error_1: {res['error_1']:.6f}, error_2: {res['error_2']:.6f}, lambda_eff: {res['lambda_eff']:.4f}, E_gap: {res['E_gap']:.6f}")
    except Exception as e:
        print(f"=== {path} FAILED: {e} ===")
