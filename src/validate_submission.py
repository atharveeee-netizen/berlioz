#!/usr/bin/env python3
"""Hardened Submission Package Format and Constraint Validator for Google Quantum AI VQCC.

Verifies all structural, naming, adversarial security, and resource rules before transmission:
- Defense-in-depth: Rejects path traversal (e.g. '..'), absolute paths, symlinks, zip bombs.
- File set: Exactly {invsqrt.kmb, dqi.kmb, dfthcsos/submission.npz} and continuous
  angle_k_0.kmb .. angle_k_{K-1}.kmb.
- Largest qubit or bit ID is strictly below MAX_ID = 2**30 // 1536 = 699,050.
- All quantum and classical registers are non-empty strings.
- All angle circuits have num_qubits <= 128 and strictly 0 T-like gates.
- Total NPZ array memory <= 64 MB (2**26 bytes) with little-endian arrays and correct shapes.
- Exception-safe: Guarantees temporary directory cleanup in all execution branches.

SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import os
import sys
import re
import zipfile
import tempfile
from pathlib import Path
import numpy as np

MAX_ID = 2**30 // 1536  # 699,050
MAX_ZIP_BYTES = 120 * 1024 * 1024        # 120 MB compressed limit
MAX_MEMBER_BYTES = 750 * 1024 * 1024     # 750 MB per member limit (DQI kmb ~544 MB)
MAX_TOTAL_UNCOMPRESSED = 1500 * 1024 * 1024  # 1.5 GB total uncompressed limit
MAX_FILE_COUNT = 50                      # Maximum archive members
ORBITALS = 76

INTEGER_ARRAYS = ('tree_edges', 'angle_words', 'brot', 'kept_indices')
BOOL_ARRAYS = ('one_body_requires_refresh',)
REQUIRED_NPZ_KEYS = ('U', 'W', 'tree_edges')

class ValidationError(Exception):
    """Raised when an archive fails security or specification constraints."""
    pass

def _check_zip_security(zip_file: zipfile.ZipFile) -> list[str]:
    """Inspects zip file headers for path traversal, symlinks, or zip bomb risks without extracting."""
    problems = []
    infolist = zip_file.infolist()
    
    if len(infolist) > MAX_FILE_COUNT:
        problems.append(f"Archive member count ({len(infolist)}) exceeds maximum limit ({MAX_FILE_COUNT})")
        return problems

    total_uncompressed = 0
    seen_names = set()

    for info in infolist:
        name = info.filename
        
        # Check duplicate entries
        if name in seen_names:
            problems.append(f"Duplicate entry in archive: '{name}'")
        seen_names.add(name)

        # Path traversal and absolute path protection
        if '..' in name.split('/') or '..' in name.split('\\'):
            problems.append(f"Path traversal detected in entry: '{name}'")
        if name.startswith('/') or name.startswith('\\') or (len(name) > 1 and name[1] == ':'):
            problems.append(f"Absolute path detected in entry: '{name}'")
        if '\0' in name:
            problems.append(f"Null byte detected in entry name: '{name}'")

        # Symlink check (Unix mode 0o120000)
        mode = info.external_attr >> 16
        if mode & 0o120000 == 0o120000:
            problems.append(f"Symlink detected in archive: '{name}'")

        # Size check
        if info.file_size > MAX_MEMBER_BYTES:
            problems.append(f"Member '{name}' size ({info.file_size:,} bytes) exceeds limit ({MAX_MEMBER_BYTES:,} bytes)")
        total_uncompressed += info.file_size

    if total_uncompressed > MAX_TOTAL_UNCOMPRESSED:
        problems.append(f"Total uncompressed size ({total_uncompressed:,} bytes) exceeds limit ({MAX_TOTAL_UNCOMPRESSED:,} bytes)")

    return problems

def validate_submission(target_path: str | Path, verbose: bool = True) -> bool:
    """Validates that a submission file or directory meets all VQCC competition requirements."""
    target = Path(target_path)
    if not target.exists():
        if verbose:
            print(f"[-] Target does not exist: {target}")
        return False

    temp_dir = None
    problems = []

    try:
        # Load kickmix
        try:
            import kickmix as km
        except ImportError:
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'verifiers'))
            import kickmix as km

        if target.is_file() and target.suffix == '.zip':
            # Check compressed file size
            comp_size = target.stat().st_size
            if comp_size > MAX_ZIP_BYTES:
                problems.append(f"Compressed archive size ({comp_size:,} bytes) exceeds {MAX_ZIP_BYTES:,} bytes")

            # Inspect zip headers for security before extracting
            try:
                with zipfile.ZipFile(target, 'r') as z:
                    sec_problems = _check_zip_security(z)
                    if sec_problems:
                        problems.extend(sec_problems)
                        if verbose:
                            print("[!] Security audit FAILED:")
                            for p in problems:
                                print(f"  - {p}")
                        return False

                    temp_dir = tempfile.TemporaryDirectory()
                    root = Path(temp_dir.name)
                    # Safe extraction of validated members
                    for info in z.infolist():
                        if not info.is_dir():
                            dest_path = root / info.filename
                            dest_path.parent.mkdir(parents=True, exist_ok=True)
                            with z.open(info) as src, open(dest_path, 'wb') as dst:
                                while chunk := src.read(1024 * 1024):
                                    dst.write(chunk)
            except zipfile.BadZipFile as e:
                problems.append(f"Malformed or corrupt ZIP archive: {e}")
                if verbose:
                    print(f"[-] Malformed ZIP: {e}")
                return False
        else:
            root = target

        # 1. Archive Structure check
        files = sorted(str(p.relative_to(root)).replace('\\', '/') for p in root.rglob('*') if p.is_file())
        angles = [f for f in files if re.fullmatch(r'dfthcsos/angle_k_\d+\.kmb', f)]
        num_angles = len(angles)

        if num_angles == 0:
            problems.append("Missing chemistry angle circuits! Expected at least dfthcsos/angle_k_0.kmb")

        expected = {'invsqrt.kmb', 'dqi.kmb', 'dfthcsos/submission.npz'} | {f'dfthcsos/angle_k_{i}.kmb' for i in range(num_angles)}
        
        if set(files) != expected:
            extra = sorted(set(files) - expected)
            missing = sorted(expected - set(files))
            problems.append(f"File structure invalid! Extra: {extra}, Missing: {missing}")

        # 2. Circuit register and ID checks
        for f in [f for f in files if f.endswith('.kmb')]:
            c_path = root / f
            try:
                c = km.Circuit.from_file(str(c_path))
            except Exception as e:
                problems.append(f"Failed to parse Kickmix circuit {f}: {e}")
                continue

            top = max(c.num_qubits, c.num_bits) - 1
            unnamed = [k for k in c.register_data if not isinstance(k, str) or len(k.strip()) == 0]
            
            if top >= MAX_ID:
                problems.append(f"{f}: largest ID {top} >= MAX_ID ({MAX_ID})")
            if unnamed:
                problems.append(f"{f}: unnamed registers {unnamed}")
                
            if f.startswith('dfthcsos/angle_k_'):
                stats = c.operation_statistics()
                if c.num_qubits > 128:
                    problems.append(f"{f}: angle circuit qubits {c.num_qubits} > 128 (Rule limit: 128)")
                if stats.num_t_like > 0:
                    problems.append(f"{f}: angle circuit contains {stats.num_t_like} T-gates (Rule requires exactly 0)")

        # 3. NPZ integrity check
        npz_path = root / 'dfthcsos/submission.npz'
        if npz_path.exists():
            try:
                with np.load(npz_path, allow_pickle=False) as npz:
                    total_bytes = 0
                    for req_key in REQUIRED_NPZ_KEYS:
                        if req_key not in npz.files:
                            problems.append(f"submission.npz missing required array '{req_key}'")

                    for name in npz.files:
                        a = npz[name]
                        total_bytes += a.nbytes
                        kind = np.integer if name in INTEGER_ARRAYS else np.bool_ if name in BOOL_ARRAYS else np.floating
                        if not np.issubdtype(a.dtype, kind):
                            problems.append(f"submission.npz: array '{name}' has unexpected dtype {a.dtype}")
                        little = a.dtype.byteorder in ('<', '|') or (a.dtype.byteorder == '=' and sys.byteorder == 'little')
                        if not little:
                            problems.append(f"submission.npz: array '{name}' is not little-endian")

                    # Shape check on U
                    if 'U' in npz.files:
                        u_shape = np.shape(npz['U'])
                        if len(u_shape) != 3 or u_shape[-1] != ORBITALS:
                            problems.append(f"submission.npz: 'U' shape {u_shape} invalid (must be (R, B, {ORBITALS}))")

                    if total_bytes > 2**26:
                        problems.append(f"submission.npz: total bytes {total_bytes:,} exceeds 64 MB limit")
            except Exception as e:
                problems.append(f"Failed to read submission.npz: {e}")

    except Exception as e:
        problems.append(f"Unexpected validator exception: {e}")
    finally:
        # Guarantee cleanup
        if temp_dir is not None:
            temp_dir.cleanup()

    if problems:
        if verbose:
            print("[!] Validation FAILED with errors:")
            for p in problems:
                print(f"  - {p}")
        return False
    else:
        if verbose:
            print(f"[+] All submission validation checks PASSED for {target_path} ({len(files)} files checked).")
        return True

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'submission.zip'
    valid = validate_submission(target)
    sys.exit(0 if valid else 1)
