"""Automated End-to-End Pipeline for Masterloop 32.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def run(cmd, desc):
    print(f'[*] {desc}...\n    $ {cmd}')
    t0 = time.time()
    res = subprocess.run(cmd, shell=True, cwd=str(ROOT), capture_output=True, text=True)
    dur = time.time() - t0
    if res.returncode != 0:
        print(f'[!] FAILED ({dur:.1f}s):')
        print(res.stderr)
        print(res.stdout)
        raise RuntimeError(f'Command failed: {cmd}')
    print(f'[+] Success ({dur:.1f}s)')
    if res.stdout.strip():
        for line in res.stdout.strip().splitlines()[-5:]:
            print(f'    | {line}')
    return res.stdout

def main():
    inp_npz = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build/test_r8_flipped_r2.npz'
    out_fin = ROOT / 'build/test_r8_finished.npz'
    chem_cand = ROOT / 'build/chem_r8_candidate'
    
    # 1. Run finish.py to optimize offsets Wo and 1-body row flips
    run(f'python src/chem/finish.py {inp_npz} {out_fin} --kappa 0',
        'Step 1: Running finish.py (optimizing Wo and 1-body rows)')
        
    # 2. Build local angle circuits and verify with official verifier
    run(f'python src/chem/build_dft_local.py {out_fin} {chem_cand}',
        'Step 2: Synthesizing 15 angle circuits via build_dft_local.py')
        
    # 3. Pack Masterloop 32 candidate archive and validate
    run(f'python scripts/pack_ml32.py {chem_cand}',
        'Step 3: Packing Masterloop 32 portfolio and running validate_submission')
        
    # 4. Transmit to Kaggle
    sub_zip = ROOT / 'build/submission.zip'
    assert sub_zip.exists(), f'{sub_zip} missing!'
    msg = "Masterloop 32: 62Q Invsqrt (20.65x) + SomeJoint 892Q DQI (63.43x) + R8 Chem (14.0x) | Target GM 26.37"
    run(f'kaggle competitions submit -c google-verifiable-quantum-circuit-compilation -f {sub_zip} -m "{msg}"',
        'Step 4: Transmitting Masterloop 32 to Kaggle Public Leaderboard')
        
    print('[PASS] MASTERLOOP 32 PIPELINE EXECUTION COMPLETED!')

if __name__ == '__main__':
    main()
