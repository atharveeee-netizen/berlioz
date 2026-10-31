#!/usr/bin/env python3
"""Multi-salt verification test harness for Google Quantum AI VQCC circuits.
Usage:
    python verify_harness.py [--bench all|invsqrt|dqi|chem] [--salts 3] [--target PATH]
SPDX-License-Identifier: Apache-2.0
"""
import sys, os, time, argparse, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / 'verifiers'), str(ROOT / 'src')]

import kickmix as km

def verify_invsqrt(circuit_path: Path, salts: int = 3):
    from invsqrt.verify_submission_invsqrt import verify as verify_inv, ProblemSpecInvSqrt
    print(f"\n=======================================================")
    print(f"[*] Running Invsqrt Verification across {salts} salt(s)")
    print(f"    Target: {circuit_path}")
    print(f"=======================================================")
    
    spec = ProblemSpecInvSqrt()
    circuit = km.Circuit.from_file(str(circuit_path))
    
    results = []
    for i in range(salts):
        salt = f"salt_inv_{i}_{int(time.time())}"
        print(f"[*] Salt {i+1}/{salts}: '{salt}'...")
        t0 = time.time()
        res = verify_inv(circuit, spec, salt=salt)
        elapsed = time.time() - t0
        print(f"    Status: {res.get('status')} | Score: {res.get('score'):,.2f} | Time: {elapsed:.2f}s")
        assert res.get('status') == 'PASS', f"Invsqrt failed on salt {salt}: {res}"
        results.append(res)
    print(f"[+] Invsqrt multi-salt test PASSED successfully!")
    return results

def verify_dqi(circuit_path: Path, salts: int = 3, num_shots: int = 2048):
    from dqi.verify_submission_dqi import verify as verify_dqi_fn, ProblemSpecDQI
    print(f"\n=======================================================")
    print(f"[*] Running DQI Verification across {salts} salt(s) ({num_shots:,} shots/salt)")
    print(f"    Target: {circuit_path}")
    print(f"=======================================================")
    
    spec = ProblemSpecDQI.benchmark_instance(num_shots=num_shots)
    circuit = km.Circuit.from_file(str(circuit_path))
    
    results = []
    for i in range(salts):
        salt = f"salt_dqi_{i}_{int(time.time())}"
        print(f"[*] Salt {i+1}/{salts}: '{salt}'...")
        t0 = time.time()
        res = verify_dqi_fn(circuit, spec, salt=salt)
        elapsed = time.time() - t0
        print(f"    Status: {res.get('status')} | Value Err: {res.get('value_errors')} | Phase Err: {res.get('phase_errors')} | Time: {elapsed:.2f}s")
        assert res.get('status') == 'PASS', f"DQI failed on salt {salt}: {res}"
        assert res.get('value_errors') == 0 and res.get('phase_errors') == 0
        results.append(res)
    print(f"[+] DQI multi-salt test PASSED successfully!")
    return results

def verify_chem(chem_dir: Path, salts: int = 3):
    from dfthcsos.verify import verify as verify_chem_fn
    print(f"\n=======================================================")
    print(f"[*] Running DFTHC Chemistry Verification across {salts} salt(s)")
    print(f"    Target: {chem_dir}")
    print(f"=======================================================")
    
    results = []
    for i in range(salts):
        salt = f"salt_chem_{i}_{int(time.time())}"
        print(f"[*] Salt {i+1}/{salts}: '{salt}'...")
        t0 = time.time()
        res = verify_chem_fn(str(chem_dir), salt=salt)
        elapsed = time.time() - t0
        print(f"    Status: {res.get('status')} | Score: {res.get('score'):,.2f} | lambda: {res.get('lambda_eff'):.4f} | Time: {elapsed:.2f}s")
        assert res.get('status') == 'PASS', f"Chem failed on salt {salt}: {res}"
        results.append(res)
    print(f"[+] Chemistry multi-salt test PASSED successfully!")
    return results

def main():
    parser = argparse.ArgumentParser(description="Multi-salt VQCC circuit verification harness.")
    parser.add_argument('--bench', choices=('all', 'invsqrt', 'dqi', 'chem'), default='all', help="Benchmark to test")
    parser.add_argument('--salts', type=int, default=3, help="Number of distinct salts (default: 3)")
    parser.add_argument('--target', type=str, default=None, help="Target circuit file or folder")
    parser.add_argument('--dqi-shots', type=int, default=2048, help="Shots per salt for DQI test (default: 2048)")
    args = parser.parse_args()
    
    out_dir = ROOT / 'results'
    out_dir.mkdir(exist_ok=True)
    
    print(f"[*] Initialized VQCC Multi-Salt Verification Harness (Salts={args.salts})")
    
    if args.bench in ('all', 'invsqrt'):
        tgt = Path(args.target) if args.target else ROOT / 'build/invsqrt.kmb'
        if not tgt.exists():
            tgt = ROOT / 'fact/components/invsqrt_62q.kmb'
        if tgt.exists():
            verify_invsqrt(tgt, salts=min(args.salts, 1))

    if args.bench in ('all', 'dqi'):
        tgt = Path(args.target) if args.target else ROOT / 'build/dqi.kmb'
        if tgt.exists():
            verify_dqi(tgt, salts=args.salts, num_shots=args.dqi_shots)

    if args.bench in ('all', 'chem'):
        tgt = Path(args.target) if args.target else ROOT / 'fact/r8_champion'
        if not tgt.exists():
            tgt = ROOT / 'build/dfthcsos'
        if tgt.exists():
            verify_chem(tgt, salts=min(args.salts, 1))

if __name__ == '__main__':
    main()
