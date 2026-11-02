"""Pack Masterloop 32 Candidate Archive and Validate.
SPDX-License-Identifier: Apache-2.0
"""
import shutil
import zipfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
import validate_submission as VS

def pack(chem_dir: Path, dqi_path: Path, inv_path: Path, out_zip: Path):
    stage = ROOT / 'build/ml32_staged'
    shutil.rmtree(stage, ignore_errors=True)
    stage.mkdir(parents=True, exist_ok=True)
    
    # 1. Copy Invsqrt
    shutil.copy2(inv_path, stage / 'invsqrt.kmb')
    print(f'[+] Added invsqrt: {inv_path} ({inv_path.stat().st_size:,} bytes)')
    
    # 2. Copy DQI
    shutil.copy2(dqi_path, stage / 'dqi.kmb')
    print(f'[+] Added dqi: {dqi_path} ({dqi_path.stat().st_size:,} bytes)')
    
    # 3. Copy Chemistry directory
    dest_chem = stage / 'dfthcsos'
    shutil.copytree(chem_dir, dest_chem)
    print(f'[+] Added dfthcsos from {chem_dir} ({len(list(dest_chem.glob("*")))} files)')
    
    # 4. Pack into zip
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(stage.rglob('*')):
            if p.is_file():
                arcname = p.relative_to(stage).as_posix()
                z.write(p, arcname=arcname)
    print(f'[+] Successfully packed {out_zip} ({out_zip.stat().st_size:,} bytes)')
    shutil.copy2(out_zip, ROOT / 'build/submission.zip')
    print(f'[+] Staged {ROOT / "build/submission.zip"} for Kaggle submission')
    
    # 5. Validate with official security and structural checker
    print('[*] Running validate_submission...')
    is_valid = VS.validate_submission(str(out_zip), verbose=True)
    if is_valid:
        print('[PASS] ARCHIVE VALIDATION PASSED!')
    else:
        print('[FAIL] ARCHIVE VALIDATION FAILED!')
        sys.exit(1)

if __name__ == '__main__':
    chem = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build/chem_r8_test/dfthcsos'
    dqi = ROOT / 'build/ml30_apex_optimum/dqi.kmb'
    inv = ROOT / 'build/ml30_apex_optimum/invsqrt.kmb'
    out = ROOT / 'build/portfolios/submission_ml32.zip'
    pack(chem, dqi, inv, out)
