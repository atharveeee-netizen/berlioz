"""Master Portfolio Synthesis and Packaging Script for R=10 J=7 Chemistry Exploration.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import os
import sys
import time
import zipfile
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'src/chem'), str(ROOT / 'src/dqi'), str(ROOT / 'verifiers'), str(ROOT / 'src')]

import angles_qrom as AQ
import banked_lab as B
from validate_submission import validate_submission

def build_chemistry_r10(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    fact_path = ROOT / 'fact/dfthc_r10_b129_c60_brot8.npz'
    if not fact_path.exists():
        raise FileNotFoundError(f"Missing factorization matrix: {fact_path}")
    
    data = dict(np.load(fact_path))
    words = data['angle_words']
    edges = data['tree_edges']
    brot = int(data['brot'])
    
    print(f"[*] Processing R=10 factor ({words.shape[0]} addresses, brot={brot})...")
    canonical = AQ.canonical_words(words, edges, brot)
    
    # Batch size J = 7 (11 circuits, Q=124 <= 126)
    J = 7
    deltas = AQ.batch_deltas(canonical, J)
    K = len(deltas)
    print(f"[*] Generating {K} angle circuits for J={J}...")
    
    t0 = time.time()
    for k in range(K):
        c, rep = B.build_qroam2(deltas[k], brot, mode="linear", return_report=True)
        assert c.num_qubits <= 126, f"Circuit exceeded 126 qubits: {c.num_qubits}"
        c.to_file(str(out_dir / f'angle_k_{k}.kmb'), format='kmb')
    print(f"[+] Chemistry angle circuits generated in {time.time()-t0:.2f}s")
    
    save_keys = ('U', 'W', 'H2_I', 'H1_I', 'Hsym_lower', 'tree_edges')
    np.savez(out_dir / 'submission.npz', **{k: data[k] for k in save_keys if k in data})
    print(f"[+] Saved {out_dir}/submission.npz")

def assemble_submission(output_zip_path: Path, invsqrt_path: Path, dqi_path: Path, chem_dir: Path):
    """Atomically builds and validates portfolio zip."""
    if not invsqrt_path.is_file():
        raise FileNotFoundError(f"Missing invsqrt: {invsqrt_path}")
    if not dqi_path.is_file():
        raise FileNotFoundError(f"Missing dqi: {dqi_path}")
    if not chem_dir.is_dir():
        raise FileNotFoundError(f"Missing chem directory: {chem_dir}")

    tmp_zip = output_zip_path.with_suffix('.tmp.zip')
    if tmp_zip.exists():
        tmp_zip.unlink()

    try:
        print(f"[*] Assembling portfolio into {tmp_zip}...")
        with zipfile.ZipFile(tmp_zip, 'w', zipfile.ZIP_DEFLATED) as z:
            z.write(invsqrt_path, 'invsqrt.kmb')
            z.write(dqi_path, 'dqi.kmb')
            for p in sorted(os.listdir(chem_dir)):
                z.write(chem_dir / p, f'dfthcsos/{p}')
                
        if not validate_submission(tmp_zip, verbose=True):
            raise RuntimeError(f"Assembled package failed validation: {tmp_zip}")
            
        if output_zip_path.exists():
            output_zip_path.unlink()
        tmp_zip.rename(output_zip_path)
        print(f"[+] Packaging complete and verified! Archive: {output_zip_path} ({output_zip_path.stat().st_size:,} bytes)")
    finally:
        if tmp_zip.exists():
            tmp_zip.unlink()

if __name__ == '__main__':
    chem_out = ROOT / 'build/dfthcsos_r10'
    build_chemistry_r10(chem_out)
