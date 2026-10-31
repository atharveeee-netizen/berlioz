#!/usr/bin/env python3
"""Master Autonomous Synthesis, Packaging, and Verification for Portfolio Submission Slots.

Packages candidate components, validates against all 5 Kaggle rules using the hardened validator,
computes deterministic input and output SHA-256 digests, and generates build/submissions/manifest.json.
Contains zero external sibling dependencies and zero user-specific paths.

SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import os
import sys
import shutil
import zipfile
import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / 'verifiers'), str(ROOT / 'src')]
from validate_submission import validate_submission

SUBMISSIONS_DIR = ROOT / 'build/submissions'
SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)

# Self-contained repository-relative component paths
INVSQRT_62Q = ROOT / 'fact/components/invsqrt_62q.kmb'
if not INVSQRT_62Q.exists():
    INVSQRT_62Q = ROOT / 'build/invsqrt.kmb'

INVSQRT_63Q = ROOT / 'fact/components/invsqrt_63q.kmb'
if not INVSQRT_63Q.exists():
    INVSQRT_63Q = ROOT / 'build/invsqrt.kmb'

DQI_889Q = ROOT / 'build/dqi.kmb'
DQI_877Q = ROOT / 'build/dqi_877q.kmb'
if not DQI_877Q.exists():
    DQI_877Q = DQI_889Q

CHEM_R8_CHAMPION = ROOT / 'fact/r8_champion'
CHEM_V44 = ROOT / 'fact/components/yoyobar_v44'
if not CHEM_V44.exists():
    CHEM_V44 = CHEM_R8_CHAMPION

def sha256_of_file(path: Path) -> str:
    """Computes SHA-256 digest of a file."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

def package_submission(output_zip: Path, invsqrt_path: Path, dqi_path: Path, chem_dir: Path):
    """Atomically packs exactly {invsqrt.kmb, dqi.kmb, dfthcsos/submission.npz, dfthcsos/angle_k_*.kmb}."""
    if not invsqrt_path.is_file():
        raise FileNotFoundError(f"Missing required invsqrt circuit: {invsqrt_path}")
    if not dqi_path.is_file():
        raise FileNotFoundError(f"Missing required DQI circuit: {dqi_path}")
    if not (chem_dir / 'submission.npz').is_file():
        raise FileNotFoundError(f"Missing required chemistry submission.npz in {chem_dir}")
    
    angles = sorted(chem_dir.glob('angle_k_*.kmb'), key=lambda p: int(p.stem.split('_')[-1]))
    if len(angles) == 0:
        raise ValueError(f"No chemistry angle circuits found in {chem_dir}")
    
    tmp_zip = output_zip.with_suffix('.tmp.zip')
    if tmp_zip.exists():
        tmp_zip.unlink()
        
    try:
        with zipfile.ZipFile(tmp_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=1) as z:
            z.write(invsqrt_path, 'invsqrt.kmb')
            z.write(dqi_path, 'dqi.kmb')
            z.write(chem_dir / 'submission.npz', 'dfthcsos/submission.npz')
            for a in angles:
                z.write(a, f'dfthcsos/{a.name}')
                
        # Validate temporary archive before final placement
        if not validate_submission(tmp_zip, verbose=True):
            raise RuntimeError(f"Packaged archive failed structural validation: {tmp_zip}")
            
        # Atomic replace
        if output_zip.exists():
            output_zip.unlink()
        tmp_zip.rename(output_zip)
        print(f"[+] Atomically packaged and verified {output_zip.name} ({output_zip.stat().st_size:,} bytes)")
    finally:
        if tmp_zip.exists():
            tmp_zip.unlink()

def build_and_verify_all():
    """Builds, validates, and generates manifest for available portfolio slots."""
    portfolios = [
        {
            "slot": 1,
            "name": "submission_slot1_chem_champion.zip",
            "desc": "Syzygy Apex Chem Champion (62Q Invsqrt + 889Q DQI + R=8 Chem)",
            "invsqrt": INVSQRT_62Q,
            "dqi": DQI_889Q,
            "chem": CHEM_R8_CHAMPION
        },
        {
            "slot": 2,
            "name": "submission_slot2_peak_ratio.zip",
            "desc": "Syzygy Peak-Ratio Apex (63Q Invsqrt + 889Q DQI + R=8 Chem)",
            "invsqrt": INVSQRT_63Q,
            "dqi": DQI_889Q,
            "chem": CHEM_R8_CHAMPION
        },
        {
            "slot": 3,
            "name": "submission_slot3_lowqubit_877.zip",
            "desc": "Syzygy Low-Qubit Explorer (62Q Invsqrt + 877Q DQI + R=8 Chem)",
            "invsqrt": INVSQRT_62Q,
            "dqi": DQI_877Q,
            "chem": CHEM_R8_CHAMPION
        },
        {
            "slot": 4,
            "name": "submission_slot4_v44_ensemble.zip",
            "desc": "Syzygy Robustness Ensemble (63Q Invsqrt + 889Q DQI + v44 Chem)",
            "invsqrt": INVSQRT_63Q,
            "dqi": DQI_889Q,
            "chem": CHEM_V44
        }
    ]

    manifest = {}

    for p in portfolios:
        slot = p["slot"]
        zip_path = SUBMISSIONS_DIR / p["name"]
        print(f"\n=======================================================")
        print(f"[*] Processing Slot {slot}: {p['desc']}")
        print(f"    Invsqrt: {p['invsqrt']}")
        print(f"    DQI:     {p['dqi']}")
        print(f"    Chem:    {p['chem']}")
        print(f"=======================================================")
        
        # Check source presence
        if not p["invsqrt"].exists() or not p["dqi"].exists() or not p["chem"].exists():
            print(f"[-] Skipping Slot {slot}: one or more components missing on disk.")
            continue
            
        package_submission(zip_path, p["invsqrt"], p["dqi"], p["chem"])
        
        digest = sha256_of_file(zip_path)
        manifest[f"slot_{slot}"] = {
            "name": p["name"],
            "description": p["desc"],
            "sha256": digest,
            "size_bytes": zip_path.stat().st_size,
            "invsqrt_source": str(p["invsqrt"].relative_to(ROOT)).replace('\\', '/'),
            "invsqrt_sha256": sha256_of_file(p["invsqrt"]),
            "dqi_source": str(p["dqi"].relative_to(ROOT)).replace('\\', '/'),
            "dqi_sha256": sha256_of_file(p["dqi"]),
            "chem_source": str(p["chem"].relative_to(ROOT)).replace('\\', '/'),
            "chem_submission_sha256": sha256_of_file(p["chem"] / 'submission.npz')
        }
        print(f"[+] Slot {slot} Packaged: SHA-256 = {digest}")

    manifest_path = SUBMISSIONS_DIR / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"\n=======================================================")
    print(f"[+] ALL AVAILABLE SUBMISSION PACKAGES BUILT AND AUDITED!")
    print(f"    Manifest written to: {manifest_path}")
    print(f"=======================================================")
    return manifest

if __name__ == '__main__':
    build_and_verify_all()
