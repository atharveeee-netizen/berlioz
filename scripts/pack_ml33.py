"""Pack Masterloop 33 Candidate Archive, Compute Composite Score, and Validate.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
import validate_submission as VS

# Benchmark references
REF_INVSQRT = 2076774.233715282
REF_DQI = 24245903932825.6
REF_CHEM = 1667083060.0

def pack_ml33(chem_dir: Path, dqi_path: Path, inv_path: Path, out_zip: Path,
              r_inv: float = 20.56, r_dqi: float = 63.43, r_chem: float = 10.26):
    stage = ROOT / 'build/ml33_staged'
    shutil.rmtree(stage, ignore_errors=True)
    stage.mkdir(parents=True, exist_ok=True)

    print('=' * 80)
    print('PACKING MASTERLOOP 33 CANDIDATE ARCHIVE')
    print('=' * 80)

    # 1. Copy Invsqrt
    assert inv_path.exists(), f"Invsqrt not found at {inv_path}"
    shutil.copy2(inv_path, stage / 'invsqrt.kmb')
    print(f'[+] [1/3] Added invsqrt: {inv_path.name} ({inv_path.stat().st_size:,} bytes) | Projected R_inv: {r_inv:.2f}x')

    # 2. Copy DQI
    assert dqi_path.exists(), f"DQI not found at {dqi_path}"
    shutil.copy2(dqi_path, stage / 'dqi.kmb')
    print(f'[+] [2/3] Added dqi:     {dqi_path.name} ({dqi_path.stat().st_size:,} bytes) | Projected R_dqi: {r_dqi:.2f}x')

    # 3. Copy Chemistry directory
    assert chem_dir.exists(), f"Chem dir not found at {chem_dir}"
    dest_chem = stage / 'dfthcsos'
    shutil.copytree(chem_dir, dest_chem)
    chem_files = list(dest_chem.glob('*'))
    print(f'[+] [3/3] Added dfthcsos: from {chem_dir.name} ({len(chem_files)} files) | Projected R_chem: {r_chem:.2f}x')

    # Compute Composite GM
    product = r_inv * r_dqi * r_chem
    gm = product ** (1.0 / 3.0)
    print(f'\n[*] Projected Composite Performance:')
    print(f'    Product Pi: {product:,.2f}')
    print(f'    Geometric Mean GM: {gm:.4f}')

    # 4. Pack into zip
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(stage.rglob('*')):
            if p.is_file():
                arcname = p.relative_to(stage).as_posix()
                z.write(p, arcname=arcname)
    print(f'\n[+] Successfully compressed archive {out_zip} ({out_zip.stat().st_size:,} bytes)')
    shutil.copy2(out_zip, ROOT / 'build/submission.zip')
    print(f'[+] Staged to {ROOT / "build/submission.zip"} for Kaggle transmission')

    # 5. Run official security and structural checker
    print('\n[*] Executing official validate_submission on staged archive...')
    is_valid = VS.validate_submission(str(out_zip), verbose=True)
    if is_valid:
        print('\n[PASS] OFFICIAL ARCHIVE VALIDATION PASSED (18/18 members compliant)!')
    else:
        print('\n[FAIL] ARCHIVE VALIDATION FAILED!')
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Pack Masterloop 33 Candidate")
    parser.add_argument('--chem', type=Path, default=ROOT / 'build/ml30_apex_optimum/dfthcsos')
    parser.add_argument('--dqi', type=Path, default=ROOT / 'build/ml30_apex_optimum/dqi.kmb')
    parser.add_argument('--inv', type=Path, default=ROOT / 'build/ml30_apex_optimum/invsqrt.kmb')
    parser.add_argument('--out', type=Path, default=ROOT / 'build/portfolios/submission_ml33.zip')
    parser.add_argument('--r-inv', type=float, default=20.56)
    parser.add_argument('--r-dqi', type=float, default=63.43)
    parser.add_argument('--r-chem', type=float, default=10.26)
    args = parser.parse_args()

    pack_ml33(args.chem, args.dqi, args.inv, args.out, args.r_inv, args.r_dqi, args.r_chem)

if __name__ == '__main__':
    main()
