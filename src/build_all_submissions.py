#!/usr/bin/env python3
"""Master Autonomous Synthesis, Packaging, and Verification Loop for All 4 Submissions.
Builds, validates against all 5 Kaggle rules, and certifies:
- Slot 1: Syzygy Apex Chem Champion (62Q Invsqrt + 889Q DQI + R=8 B143 C60 Chem)
- Slot 2: Syzygy Peak-Ratio Apex (63Q Invsqrt + 889Q DQI + R=8 B143 C60 Chem)
- Slot 3: Syzygy Low-Qubit Explorer (62Q Invsqrt + 877Q DQI + R=8 B143 C60 Chem)
- Slot 4: Syzygy Robustness Ensemble (63Q Invsqrt + 889Q DQI + v44 Chem)

SPDX-License-Identifier: Apache-2.0
"""
import os, sys, shutil, zipfile, hashlib, json, time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / 'verifiers'), str(ROOT / 'src')]
from validate_submission import validate_submission

SUBMISSIONS_DIR = ROOT / 'build/submissions'
SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)

# Proven, verified component sources
INVSQRT_62Q = ROOT / 'build/invsqrt.kmb'
INVSQRT_63Q = ROOT.parent / 'quantum-competition/current_best/invsqrt.kmb'

DQI_889Q = ROOT / 'build/dqi.kmb'
DQI_877Q = ROOT.parent / 'quantum-competition/current_best/dqi.kmb'

CHEM_R8_CHAMPION = ROOT / 'fact/r8_champion'
CHEM_V44 = ROOT.parent / 'quantum-competition/latest_assets/yoyobar_v44'

def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

def package_submission(output_zip: Path, invsqrt_path: Path, dqi_path: Path, chem_dir: Path):
    """Packs exactly {invsqrt.kmb, dqi.kmb, dfthcsos/submission.npz, dfthcsos/angle_k_*.kmb}."""
    assert invsqrt_path.exists(), f"Missing {invsqrt_path}"
    assert dqi_path.exists(), f"Missing {dqi_path}"
    assert (chem_dir / 'submission.npz').exists(), f"Missing {chem_dir}/submission.npz"
    
    angles = sorted(chem_dir.glob('angle_k_*.kmb'), key=lambda p: int(p.stem.split('_')[-1]))
    assert len(angles) > 0, f"No angle circuits in {chem_dir}"
    
    tmp_zip = output_zip.with_suffix('.tmp.zip')
    with zipfile.ZipFile(tmp_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=1) as z:
        z.write(invsqrt_path, 'invsqrt.kmb')
        z.write(dqi_path, 'dqi.kmb')
        z.write(chem_dir / 'submission.npz', 'dfthcsos/submission.npz')
        for a in angles:
            z.write(a, f'dfthcsos/{a.name}')
            
    if output_zip.exists():
        output_zip.unlink()
    tmp_zip.rename(output_zip)
    print(f"[+] Packaged {output_zip.name} ({output_zip.stat().st_size:,} bytes)")

def build_and_verify_all():
    portfolios = [
        {
            "slot": 1,
            "name": "submission_slot1_chem_champion.zip",
            "desc": "Syzygy Apex Chem Champion (62Q Invsqrt + 889Q DQI + R=8 Chem)",
            "invsqrt": INVSQRT_62Q,
            "dqi": DQI_889Q,
            "chem": CHEM_R8_CHAMPION,
            "expected_gm": 25.05
        },
        {
            "slot": 2,
            "name": "submission_slot2_peak_ratio.zip",
            "desc": "Syzygy Peak-Ratio Apex (63Q Invsqrt + 889Q DQI + R=8 Chem)",
            "invsqrt": INVSQRT_63Q,
            "dqi": DQI_889Q,
            "chem": CHEM_R8_CHAMPION,
            "expected_gm": 25.43
        },
        {
            "slot": 3,
            "name": "submission_slot3_lowqubit_877.zip",
            "desc": "Syzygy Low-Qubit Explorer (62Q Invsqrt + 877Q DQI + R=8 Chem)",
            "invsqrt": INVSQRT_62Q,
            "dqi": DQI_877Q,
            "chem": CHEM_R8_CHAMPION,
            "expected_gm": 22.97
        },
        {
            "slot": 4,
            "name": "submission_slot4_v44_ensemble.zip",
            "desc": "Syzygy Robustness Ensemble (63Q Invsqrt + 889Q DQI + v44 Chem)",
            "invsqrt": INVSQRT_63Q,
            "dqi": DQI_889Q,
            "chem": CHEM_V44,
            "expected_gm": 25.42
        }
    ]

    manifest = {}

    for p in portfolios:
        slot = p["slot"]
        zip_path = SUBMISSIONS_DIR / p["name"]
        print(f"\n=======================================================")
        print(f"[*] Processing Slot {slot}: {p['desc']}")
        print(f"    Invsqrt: {p['invsqrt'].name}")
        print(f"    DQI:     {p['dqi'].name}")
        print(f"    Chem:    {p['chem'].name}")
        print(f"=======================================================")
        
        # Iterative build & verification loop
        attempt = 0
        max_attempts = 3
        passed = False
        while attempt < max_attempts and not passed:
            attempt += 1
            print(f"[*] Build attempt {attempt} for Slot {slot}...")
            package_submission(zip_path, p["invsqrt"], p["dqi"], p["chem"])
            
            print(f"[*] Verifying submission constraints against all 5 rules...")
            is_valid = validate_submission(zip_path)
            if is_valid:
                passed = True
                print(f"[+] Slot {slot} PASSED all 5 submission constraints!")
            else:
                print(f"[-] Slot {slot} FAILED verification! Retrying...")
                time.sleep(1)
                
        assert passed, f"Slot {slot} failed validation after {max_attempts} attempts!"
        
        digest = sha256_of_file(zip_path)
        manifest[f"slot_{slot}"] = {
            "name": p["name"],
            "description": p["desc"],
            "sha256": digest,
            "size_bytes": zip_path.stat().st_size,
            "invsqrt": p["invsqrt"].name,
            "dqi": p["dqi"].name,
            "chem": p["chem"].name,
            "projected_gm": p["expected_gm"]
        }
        print(f"[+] Slot {slot} Certified: SHA-256 = {digest}")

    manifest_path = SUBMISSIONS_DIR / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"\n=======================================================")
    print(f"[+] ALL 4 SUBMISSION PACKAGES BUILT AND CERTIFIED!")
    print(f"    Manifest written to: {manifest_path}")
    print(f"=======================================================")
    return manifest

if __name__ == '__main__':
    build_and_verify_all()
