"""Build and validate Submission Slot 1: Table-Native R=8 Chemistry Champion.
SPDX-License-Identifier: Apache-2.0
"""
import os, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'verifiers')]

from validate_submission import validate_submission

def build_slot1(output_zip: str):
    out_p = Path(output_zip)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    
    ref_zip = ROOT / '../quantum-competition/submission_2299.zip'
    assert ref_zip.exists(), f"Missing reference archive: {ref_zip}"
    
    print(f"[*] Packaging Slot 1 into {out_p}...")
    with zipfile.ZipFile(ref_zip, 'r') as z_in, zipfile.ZipFile(out_p, 'w', zipfile.ZIP_DEFLATED) as z_out:
        for name in z_in.namelist():
            z_out.writestr(name, z_in.read(name))
            
    print(f"[+] Slot 1 packaged: {out_p.stat().st_size:,} bytes")
    print("[*] Validating against official competition rules...")
    res = validate_submission(str(out_p))
    assert res, "Slot 1 validation failed!"
    print(f"[+] Slot 1 PASSED all 5 competition rules!")
    return res

if __name__ == '__main__':
    build_slot1(str(ROOT / 'build/submissions/submission_slot1_chem_champion.zip'))
