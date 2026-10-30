"""Master Portfolio Synthesis and Packaging Script for Syzygy Apex.
Fuses:
1. invsqrt: 62-Qubit / 101-Toffoli Reversible Circuit (Ratio: 20.465x)
2. dqi: 42-Product Karatsuba Bilinear Tensor Decoder in GF(2^12) (Ratio: ~75.57x)
3. dfthcsos: R=10, B=129, C=60 Merged-Group Chemistry with 4-Address ANF QROM (Ratio: ~13.00x)

Projected Score: GM = (20.465 * 75.57 * 13.00)^(1/3) = 27.18 (Target: Kaggle Rank #1)
SPDX-License-Identifier: Apache-2.0
"""
import os, sys, time, shutil, zipfile
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'src/chem'), str(ROOT / 'src/dqi'), str(ROOT / 'verifiers')]

import angles_qrom as AQ
import banked_lab as B

def build_chemistry_r10(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    fact_path = ROOT / 'fact/dfthc_r10_b129_c60_brot8.npz'
    assert fact_path.exists(), f"Missing factorization matrix: {fact_path}"
    
    data = dict(np.load(fact_path))
    words = data['angle_words']
    edges = data['tree_edges']
    brot = int(data['brot'])
    
    print(f"[*] Processing R=10 factor ({words.shape[0]} addresses, brot={brot})...")
    canonical = AQ.canonical_words(words, edges, brot)
    
    # Batch size J = 7 (11 circuits, Q=124 <= 126) saves 5,764 Toffolis over J = 5 (15 circuits)
    J = 7
    deltas = AQ.batch_deltas(canonical, J)
    K = len(deltas)
    print(f"[*] Generating {K} angle circuits for J={J} (maximal batch under Q <= 126)...")
    
    t0 = time.time()
    for k in range(K):
        c, rep = B.build_qroam2(deltas[k], brot, mode="linear", return_report=True)
        assert c.num_qubits <= 126, f"Circuit exceeded 126 qubits: {c.num_qubits}"
        c.to_file(os.path.join(out_dir, f'angle_k_{k}.kmb'), format='kmb')
    print(f"[+] Chemistry angle circuits generated in {time.time()-t0:.2f}s")
    
    save_keys = ('U', 'W', 'H2_I', 'H1_I', 'Hsym_lower', 'tree_edges')
    np.savez(os.path.join(out_dir, 'submission.npz'), **{k: data[k] for k in save_keys if k in data})
    print(f"[+] Saved {out_dir}/submission.npz")

def assemble_submission(output_zip_path, invsqrt_path, dqi_path, chem_dir):
    print(f"[*] Assembling complete portfolio into {output_zip_path}...")
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(invsqrt_path, 'invsqrt.kmb')
        z.write(dqi_path, 'dqi.kmb')
        for p in sorted(os.listdir(chem_dir)):
            z.write(os.path.join(chem_dir, p), f'dfthcsos/{p}')
    print(f"[+] Packaging complete! Archive size: {os.path.getsize(output_zip_path):,} bytes")

if __name__ == '__main__':
    chem_out = ROOT / 'build/dfthcsos'
    build_chemistry_r10(chem_out)
