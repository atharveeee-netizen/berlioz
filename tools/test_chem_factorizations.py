"""Track C: Comparative Analysis of Chemistry Factorizations.
Evaluates:
1. Current R=9 candidate (fact/fact_candidate_ml27.npz)
2. Low-rank R=10 factorization (fact/dfthc_r10_b129_c60_brot8.npz)
Measures: lambda_eff, error_1, error_2, Lambda, E_gap, state prep Toffolis, and Q_total.
"""
import sys
import numpy as np

sys.path.insert(0, 'verifiers')
from dfthcsos.verify import load_inputs, evaluate_words, heuristic_costs

def evaluate_factorization_file(path):
    z = np.load(path)
    inputs = load_inputs(path)
    brot = int(z['brot'])
    edges = z['tree_edges']
    words = z['angle_words']
    
    metrics = evaluate_words(words, inputs, brot=brot, tree_edges=edges)
    
    R, B, N = z['U'].shape[0], z['U'].shape[1], z['U'].shape[2]
    C = z['W'].shape[2]
    
    # State prep costs using SpinFreeData_V1
    heur = heuristic_costs(R=R, B=B, C=C, N=N, brot=brot, keep_bits=16)
    
    return {
        "file": path,
        "R": R,
        "B": B,
        "C": C,
        "N": N,
        "brot": brot,
        "num_addresses": N + R * B,
        "error_1_mHa": metrics["error_1"] * 1000.0,
        "error_2_mHa": metrics["error_2"] * 1000.0,
        "Lambda": metrics["Lambda"],
        "lambda_eff": metrics["lambda_eff"],
        "gap_in_domain": metrics["gap_in_domain"],
        "outer_state_prep_toffoli": heur["outer_toffoli"],
        "inner_state_prep_toffoli": heur["inner_toffoli"],
        "givens_rotations_toffoli": heur["givens_toffoli"],
        "state_prep_toffoli": heur["toffoli"],
        "heuristic_qubits": heur["qubits"],
    }

if __name__ == "__main__":
    print("=== TRACK C: CHEMISTRY FACTORIZATION AUDIT ===")
    for path in ['fact/fact_candidate_ml27.npz', 'fact/dfthc_r10_b129_c60_brot8.npz']:
        res = evaluate_factorization_file(path)
        print(f"\n[{res['file']}]")
        print(f"  Shape: (R={res['R']}, B={res['B']}, C={res['C']}, N={res['N']})")
        print(f"  Addresses: {res['num_addresses']}")
        print(f"  Error 1:   {res['error_1_mHa']:.6f} mHa (Threshold: <= 20.0)")
        print(f"  Error 2:   {res['error_2_mHa']:.8f} mHa (Threshold: <= 20.0)")
        print(f"  Lambda:    {res['Lambda']:.4f}")
        print(f"  lambda_eff:{res['lambda_eff']:.6f}")
        print(f"  Gap Valid: {res['gap_in_domain']}")
        print(f"  State Prep Toffolis: {res['state_prep_toffoli']:,}")
        print(f"  Base Qubits:         {res['heuristic_qubits']}")
