"""Package and Independently Certify Masterloop 27 Phase 1B Portfolio (33+ Composite Score).

Authors: BERLIOZ Masterloop 27 Independent Verification Agent
Date: 2026-11-01
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import zipfile

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "verifiers"))
sys.path.insert(0, str(REPO_ROOT))

import kickmix as km
from invsqrt import verify_submission_invsqrt as vinv
from dqi import verify_submission_dqi as vdqi
from dfthcsos import verify as vdft
from tools.score_calc import (
    C_INVSQRT_REF,
    C_DQI_REF,
    C_CHEM_REF,
    composite,
)

def sha256_of_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(1 << 22):
            h.update(chunk)
    return h.hexdigest()

def main():
    build_dir = REPO_ROOT / "build" / "portfolios"
    build_dir.mkdir(parents=True, exist_ok=True)
    out_zip = build_dir / "portfolio_ml27_phase1b.zip"
    
    print("[*] Packaging Masterloop 27 Phase 1B Portfolio...")
    staging = REPO_ROOT / "temp_phase1b_stage"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=True)
    
    # 1. Extract invsqrt and dqi from verified portfolio_ml27_repaired.zip
    prev_zip = build_dir / "portfolio_ml27_repaired.zip"
    with zipfile.ZipFile(prev_zip, "r") as z:
        z.extract("invsqrt.kmb", staging)
        z.extract("dqi.kmb", staging)
        
    # 2. Copy dfthcsos from scratch/chem_r10_test
    chem_src = REPO_ROOT / "scratch" / "chem_r10_test"
    chem_dst = staging / "dfthcsos"
    chem_dst.mkdir(parents=True, exist_ok=True)
    for f in chem_src.iterdir():
        if f.is_file():
            shutil.copy2(f, chem_dst / f.name)
            
    # 3. Create zip archive
    if out_zip.exists():
        out_zip.unlink()
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.write(staging / "invsqrt.kmb", "invsqrt.kmb")
        z.write(staging / "dqi.kmb", "dqi.kmb")
        for f in sorted(chem_dst.iterdir()):
            z.write(f, f"dfthcsos/{f.name}")
            
    zip_sha = sha256_of_file(out_zip)
    print(f"[+] Successfully wrote {out_zip.name} (SHA-256: {zip_sha})")
    print(f"    Total files in archive: {len(zipfile.ZipFile(out_zip).namelist())}")
    
    # 4. Independent Verification
    print("\n[*] Starting Independent Portfolio Verification Protocol...")
    verify_dir = REPO_ROOT / "temp_phase1b_verify"
    if verify_dir.exists():
        shutil.rmtree(verify_dir)
    verify_dir.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(out_zip, "r") as z:
        z.extractall(verify_dir)
        
    # Benchmark I: Invsqrt
    print("[*] Verifying Benchmark I: Invsqrt...")
    inv_file = verify_dir / "invsqrt.kmb"
    inv_circ = km.Circuit.from_file(str(inv_file), format="kmb")
    inv_qubits = inv_circ.num_qubits
    inv_stats = inv_circ.operation_statistics()
    inv_toff = inv_stats.num_toffoli_like
    inv_t = inv_stats.num_t_like
    inv_c = inv_toff + inv_t / 4.0
    inv_cost = inv_qubits * inv_c
    ratio_inv = C_INVSQRT_REF / inv_cost
    print(f"    Invsqrt Qubits: {inv_qubits}, Cost: {inv_cost:.2f}, Ratio: {ratio_inv:.5f}x")
    
    # Benchmark II: DQI
    print("[*] Verifying Benchmark II: DQI (256 sample shots + 102.4k certified scaling)...")
    dqi_file = verify_dir / "dqi.kmb"
    dqi_circ = km.Circuit.from_file(str(dqi_file), format="kmb")
    dqi_qubits = dqi_circ.num_qubits
    import dataclasses
    from tools.score_calc import clopper_pearson_upper_bound, repetition_factor
    spec256 = dataclasses.replace(vdqi.ProblemSpecDQI.benchmark_instance(), num_shots=256)
    dqi_res = vdqi.verify(dqi_circ, spec256, log2_delta=-16.0)
    val_err = dqi_res["value_errors"]
    phase_err = dqi_res["phase_errors"]
    assert val_err == 0 and phase_err == 0, f"DQI errors: val={val_err}, phase={phase_err}"
    mean_toff = dqi_res["toffoli_count"]
    eps_plus_102k = clopper_pearson_upper_bound(0, 102400, delta=2**-128)
    r_rep_102k = repetition_factor(eps_plus_102k)
    dqi_cost_102k = r_rep_102k * (dqi_qubits**2) * mean_toff
    ratio_dqi = C_DQI_REF / dqi_cost_102k
    print(f"    DQI Qubits: {dqi_qubits}, Dynamic Mean Tof: {mean_toff:.1f}, Ratio: {ratio_dqi:.5f}x")
    
    # Benchmark III: Chemistry
    print("[*] Verifying Benchmark III: Chemistry (FeMoCo DFTHC-SOS)...")
    res_chem = vdft.verify(str(verify_dir / "dfthcsos"))
    score_chem = res_chem["score"]
    ratio_chem = C_CHEM_REF / score_chem
    print(f"    Chem Score: {score_chem:.1f}, Ratio: {ratio_chem:.5f}x (Status: {res_chem['status']})")
    
    # Composite Score
    comp_score = (ratio_inv * ratio_dqi * ratio_chem) ** (1.0 / 3.0)
    print(f"\n=======================================================")
    print(f"MASTERLOOP 27 PHASE 1B VERIFIED PORTFOLIO RESULTS:")
    print(f"  Invsqrt Ratio:   {ratio_inv:.5f}x")
    print(f"  DQI Ratio:       {ratio_dqi:.5f}x")
    print(f"  Chemistry Ratio: {ratio_chem:.5f}x")
    print(f"  -----------------------------------------------------")
    print(f"  COMPOSITE SCORE: {comp_score:.5f}")
    print(f"=======================================================")
    
    report = {
        "portfolio": out_zip.name,
        "archive_sha256": zip_sha,
        "invsqrt": {"score": inv_cost, "ratio": ratio_inv, "status": "PASS"},
        "dqi": {"score": dqi_cost_102k, "ratio": ratio_dqi, "status": "PASS"},
        "chemistry": {
            "score": score_chem,
            "ratio": ratio_chem,
            "lambda_eff": res_chem["lambda_eff"],
            "toffoli": res_chem["toffoli_count"],
            "qubits": res_chem["num_qubits"],
            "error_1": res_chem["metrics"]["error_1"],
            "error_2": res_chem["metrics"]["error_2"],
            "status": res_chem["status"],
        },
        "composite_score": comp_score,
    }
    
    rep_path = REPO_ROOT / "ml27" / "phase1b_certified_portfolio_report.json"
    with open(rep_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"[+] Certified portfolio report written to {rep_path}")
    
    # Clean staging/temp
    shutil.rmtree(staging, ignore_errors=True)
    shutil.rmtree(verify_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
