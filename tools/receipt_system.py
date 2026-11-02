"""Masterloop 28 Canonical Receipt System (Adaptation of ML17 WS1).

Authors: BERLIOZ Verification & Integrity Agent
Date: 2026-11-01
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Any, Dict, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]

# Canonical Official Reference Costs (Verified from official_eval/evaluator.py)
C_INVSQRT_REF = 2076774.233715282
C_DQI_REF = 24439463583672.93
C_CHEM_REF = 3355599588.3155365

def sha256_of_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()

def get_git_blob_hash(rel_path: str) -> Optional[str]:
    try:
        res = subprocess.run(
            ["git", "ls-tree", "HEAD", rel_path],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=True
        )
        parts = res.stdout.strip().split()
        if len(parts) >= 3 and parts[1] == "blob":
            return parts[2]
    except Exception:
        pass
    return None

def estimate_full_run(benchmark: str, pilot_shots: int, pilot_duration_sec: float) -> Dict[str, Any]:
    """Projects total execution time based on pilot scaling."""
    sec_per_shot = pilot_duration_sec / max(1, pilot_shots)
    if benchmark == "INVSQRT":
        official_shots = 3133452 * 64  # 200,540,928 shots
        est_sec = sec_per_shot * official_shots
        # In batch mode (batch=256, multi-threaded), throughput is ~50,000 shots/sec
        return {
            "official_shots": official_shots,
            "pilot_shots": pilot_shots,
            "sec_per_shot": sec_per_shot,
            "projected_full_duration_sec": est_sec,
            "projected_full_duration_hours": est_sec / 3600.0,
            "recommendation": "Full 200M shot run requires dedicated cluster; use Bit-Exact Classical Twin for exhaustive domain check."
        }
    elif benchmark == "DQI":
        official_shots = 102400
        est_sec = sec_per_shot * official_shots
        return {
            "official_shots": official_shots,
            "pilot_shots": pilot_shots,
            "sec_per_shot": sec_per_shot,
            "projected_full_duration_sec": est_sec,
            "projected_full_duration_hours": est_sec / 3600.0,
            "recommendation": "Full 102,400 run takes ~2.5h on 4 cores. 256-shot empirical pilot + Clopper-Pearson scaling is recommended during development."
        }
    elif benchmark == "CHEMISTRY":
        return {
            "official_shots": 87424,
            "projected_full_duration_sec": pilot_duration_sec,
            "projected_full_duration_hours": pilot_duration_sec / 3600.0,
            "recommendation": "Full verification takes ~30-45s locally; official execution is safe for every run."
        }
    return {}

def create_receipt(
    benchmark: str,
    target_path: Path,
    verifier_path: Path,
    classification: str,  # "OFFICIAL", "PILOT", "ESTIMATE", "UNKNOWN"
    execution_args: Dict[str, Any],
    verifier_output: Dict[str, Any],
    duration_sec: float,
    notes: str = ""
) -> Dict[str, Any]:
    """Constructs a strict, reproducible verification receipt."""
    assert classification in ("OFFICIAL", "PILOT", "ESTIMATE", "UNKNOWN"), f"Invalid classification {classification}"
    
    target_rel = str(target_path.relative_to(REPO_ROOT)) if target_path.is_relative_to(REPO_ROOT) else str(target_path)
    verifier_rel = str(verifier_path.relative_to(REPO_ROOT)) if verifier_path.is_relative_to(REPO_ROOT) else str(verifier_path)
    
    target_sha = sha256_of_file(target_path) if target_path.is_file() else "DIRECTORY"
    verifier_sha = sha256_of_file(verifier_path)
    verifier_blob = get_git_blob_hash(verifier_rel)
    
    # Calculate score & ratio
    score = verifier_output.get("score")
    ratio = None
    if score and score > 0:
        if benchmark == "INVSQRT":
            ratio = C_INVSQRT_REF / score
        elif benchmark == "DQI":
            ratio = C_DQI_REF / score
        elif benchmark == "CHEMISTRY":
            ratio = C_CHEM_REF / score

    receipt = {
        "receipt_version": "ML28-WS1-V1",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "classification": classification,
        "benchmark": benchmark,
        "notes": notes,
        "environment": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count(),
        },
        "verifier": {
            "path": verifier_rel,
            "sha256": verifier_sha,
            "git_blob": verifier_blob,
            "arguments": execution_args,
        },
        "target": {
            "path": target_rel,
            "sha256": target_sha,
            "size_bytes": target_path.stat().st_size if target_path.is_file() else None,
        },
        "results": {
            "status": verifier_output.get("status", "UNKNOWN"),
            "score": score,
            "ratio": ratio,
            "qubits": verifier_output.get("num_qubits"),
            "toffoli_count": verifier_output.get("toffoli_count"),
            "verified_shots": verifier_output.get("verified_shots"),
            "benchmark_specific": {k: v for k, v in verifier_output.items() if k not in ("status", "score", "num_qubits", "toffoli_count", "verified_shots")}
        },
        "execution": {
            "duration_seconds": duration_sec,
        }
    }
    
    receipt_dir = REPO_ROOT / "audit" / "receipts" / benchmark.lower()
    receipt_dir.mkdir(parents=True, exist_ok=True)
    out_name = f"receipt_{target_path.stem}_{int(time.time())}.json"
    receipt_file = receipt_dir / out_name
    with open(receipt_file, "w") as f:
        json.dump(receipt, f, indent=2)
    print(f"[+] Receipt generated: {receipt_file.relative_to(REPO_ROOT)} [{classification}]")
    return receipt

if __name__ == "__main__":
    print("[*] Receipt system loaded successfully.")
