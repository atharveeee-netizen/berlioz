"""Build and validate Submission Slot 1: Table-Native R=8 Chemistry Champion.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'verifiers')]

from validate_submission import validate_submission

def build_slot1(output_zip: str):
    out_p = Path(output_zip)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    
    ref_zip = ROOT / 'audit/baseline_vault/submission_2299.zip'
    if not ref_zip.exists():
        ref_zip = ROOT / 'submission.zip'
    assert ref_zip.is_file(), f"Missing reference archive: {ref_zip}"
    
    tmp_zip = out_p.with_suffix('.tmp.zip')
    if tmp_zip.exists():
        tmp_zip.unlink()
        
    try:
        print(f"[*] Packaging Slot 1 from {ref_zip.name} into {out_p}...")
        with zipfile.ZipFile(ref_zip, 'r') as z_in, zipfile.ZipFile(tmp_zip, 'w', zipfile.ZIP_DEFLATED) as z_out:
            for name in z_in.namelist():
                z_out.writestr(name, z_in.read(name))
                
        print(f"[+] Slot 1 packaged: {tmp_zip.stat().st_size:,} bytes")
        print("[*] Validating against official competition rules...")
        res = validate_submission(str(tmp_zip))
        assert res, "Slot 1 validation failed!"
        
        if out_p.exists():
            out_p.unlink()
        tmp_zip.rename(out_p)
        print(f"[+] Slot 1 atomically placed and PASSED all 5 competition rules!")
        return res
    finally:
        if tmp_zip.exists():
            tmp_zip.unlink()

if __name__ == '__main__':
    build_slot1(str(ROOT / 'build/submissions/submission_slot1_chem_champion.zip'))
