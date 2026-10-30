#!/usr/bin/env python3
"""Submission package format and constraint validator for Google Quantum AI VQCC.
Verifies all structural, naming, and resource rules before transmission to Kaggle:
- Exactly {invsqrt.kmb, dqi.kmb, dfthcsos/submission.npz} and continuous angle_k_0 .. angle_k_{K-1}.kmb.
- Largest qubit or bit ID is below 2**30 // 1536 = 699,050.
- All registers are named strings.
- All angle circuits have num_qubits <= 128 and 0 T-gates.
- Total NPZ array memory <= 64 MB (2**26 bytes) with little-endian arrays.
SPDX-License-Identifier: Apache-2.0
"""
import os, sys, re, zipfile, tempfile
from pathlib import Path
import numpy as np

MAX_ID = 2**30 // 1536  # 699,050
INTEGER_ARRAYS = ('tree_edges', 'angle_words', 'brot', 'kept_indices')
BOOL_ARRAYS = ('one_body_requires_refresh',)

def validate_submission(target_path):
    target = Path(target_path)
    if not target.exists():
        print(f"[-] Target does not exist: {target}")
        return False
        
    temp_dir = None
    if target.is_file() and target.suffix == '.zip':
        temp_dir = tempfile.TemporaryDirectory()
        with zipfile.ZipFile(target, 'r') as z:
            z.extractall(temp_dir.name)
        root = Path(temp_dir.name)
    else:
        root = target

    try:
        import kickmix as km
    except ImportError:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'verifiers'))
        import kickmix as km

    problems = []
    files = sorted(str(p.relative_to(root)).replace('\\', '/') for p in root.rglob('*') if p.is_file())
    
    # 1. Structure check
    angles = [f for f in files if re.fullmatch(r'dfthcsos/angle_k_\d+\.kmb', f)]
    num_angles = len(angles)
    expected = {'invsqrt.kmb', 'dqi.kmb', 'dfthcsos/submission.npz'} | {f'dfthcsos/angle_k_{i}.kmb' for i in range(num_angles)}
    
    if set(files) != expected:
        extra = sorted(set(files) - expected)
        missing = sorted(expected - set(files))
        problems.append(f"File structure invalid! Extra: {extra}, Missing: {missing}")

    # 2. Circuit register and ID checks
    for f in [f for f in files if f.endswith('.kmb')]:
        c = km.Circuit.from_file(str(root / f))
        top = max(c.num_qubits, c.num_bits) - 1
        unnamed = [k for k in c.register_data if not isinstance(k, str)]
        
        if top >= MAX_ID:
            problems.append(f"{f}: largest ID {top} >= MAX_ID ({MAX_ID})")
        if unnamed:
            problems.append(f"{f}: unnamed registers {unnamed}")
            
        if f.startswith('dfthcsos/angle_k_'):
            stats = c.operation_statistics()
            if c.num_qubits > 128:
                problems.append(f"{f}: angle circuit qubits {c.num_qubits} > 128")
            if stats.num_t_like > 0:
                problems.append(f"{f}: angle circuit contains {stats.num_t_like} T-gates (must be 0)")

    # 3. NPZ integrity check
    npz_path = root / 'dfthcsos/submission.npz'
    if npz_path.exists():
        with np.load(npz_path, allow_pickle=False) as npz:
            total_bytes = 0
            for name in npz.files:
                a = npz[name]
                total_bytes += a.nbytes
                kind = np.integer if name in INTEGER_ARRAYS else np.bool_ if name in BOOL_ARRAYS else np.floating
                if not np.issubdtype(a.dtype, kind):
                    problems.append(f"submission.npz: array '{name}' has unexpected dtype {a.dtype}")
                little = a.dtype.byteorder in ('<', '|') or (a.dtype.byteorder == '=' and sys.byteorder == 'little')
                if not little:
                    problems.append(f"submission.npz: array '{name}' is not little-endian")
            if total_bytes > 2**26:
                problems.append(f"submission.npz: total bytes {total_bytes:,} exceeds 64 MB limit")

    if temp_dir is not None:
        temp_dir.cleanup()

    if problems:
        print("[!] Validation FAILED with errors:")
        for p in problems:
            print(f"  - {p}")
        return False
    else:
        print(f"[+] All submission validation checks PASSED for {target_path} ({len(files)} files checked).")
        return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <SUBMISSION_DIR_OR_ZIP>")
        sys.exit(1)
    ok = validate_submission(sys.argv[1])
    sys.exit(0 if ok else 1)
