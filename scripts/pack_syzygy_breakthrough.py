#!/usr/bin/env python3
"""Syzygy Packaging Harness for Breakthrough Submission (Masterloop 35).
Packages verified Ehan 62Q + Breakthrough DQI + v34 Chemistry.
SPDX-License-Identifier: MIT / Apache-2.0
"""

import os
import sys
import zipfile
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

INV_PATH = ROOT / "audit/archive_round1_invsqrt/invsqrt_ehan_bce2948f.kmb"
if not INV_PATH.exists():
    INV_PATH = ROOT / "build/harvest_busyaprime/invsqrt.kmb"

DQI_PATH = ROOT / "build/circuits/dqi_breakthrough.kmb"
CHEM_DIR = ROOT / "build/ml30_apex_optimum/dfthcsos"
OUT_ZIP = ROOT / "build/submission.zip"

print("[*] Packaging Masterloop 35 Breakthrough Submission...")
print(f"    Invsqrt:   {INV_PATH} (SHA-256 {hashlib.sha256(open(INV_PATH, 'rb').read()).hexdigest()[:16]})")
print(f"    DQI:       {DQI_PATH} (SHA-256 {hashlib.sha256(open(DQI_PATH, 'rb').read()).hexdigest()[:16]})")
print(f"    Chemistry: {CHEM_DIR}")

# Create zip with exactly 18 files
OUT_ZIP.parent.mkdir(parents=True, exist_ok=True)
if OUT_ZIP.exists():
    OUT_ZIP.unlink()

with zipfile.ZipFile(OUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    zf.write(INV_PATH, "invsqrt.kmb")
    zf.write(DQI_PATH, "dqi.kmb")
    
    # 16 chemistry files
    npz_path = CHEM_DIR / "submission.npz"
    zf.write(npz_path, "dfthcsos/submission.npz")
    for k in range(15):
        kmb_path = CHEM_DIR / f"angle_k_{k}.kmb"
        zf.write(kmb_path, f"dfthcsos/angle_k_{k}.kmb")

print(f"[+] Successfully wrote {OUT_ZIP} ({OUT_ZIP.stat().st_size / 1e6:.2f} MB)")

# Verify with official validator
import subprocess
print("[*] Validating archive with src/validate_submission.py...")
res = subprocess.run([sys.executable, "src/validate_submission.py", str(OUT_ZIP)], capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print(res.stderr)
assert res.returncode == 0, "Validation failed!"
print("[+] Validation PASSED: 18/18 compliant with zero faults!")
