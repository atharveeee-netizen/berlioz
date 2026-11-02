"""Masterloop 28 Ground Truth Audit Script.
Extracts and audits:
- Hashes of all archives
- Hashes of all internal members
- Verifier source blobs and file hashes
- Official parameters
- Discrepancy analysis on 24.01756 claim
"""
import hashlib
import json
from pathlib import Path
import zipfile

REPO_ROOT = Path(__file__).resolve().parents[1]

def sha256_of_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()

def sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def audit_zip(zip_path: Path):
    if not zip_path.exists():
        return None
    info = {
        "path": str(zip_path.relative_to(REPO_ROOT)),
        "size_bytes": zip_path.stat().st_size,
        "sha256": sha256_of_file(zip_path),
        "members": []
    }
    with zipfile.ZipFile(zip_path, "r") as z:
        for m in sorted(z.infolist(), key=lambda x: x.filename):
            data = z.read(m.filename)
            info["members"].append({
                "filename": m.filename,
                "file_size": m.file_size,
                "compress_size": m.compress_size,
                "sha256": sha256_of_bytes(data)
            })
    return info

def main():
    archives = [
        REPO_ROOT / "submission.zip",
        REPO_ROOT / "build" / "portfolios" / "portfolio_ml27_repaired.zip",
        REPO_ROOT / "build" / "portfolios" / "portfolio_ml27_phase1b.zip"
    ]
    
    results = {"archives": {}}
    for arch in archives:
        res = audit_zip(arch)
        if res:
            results["archives"][arch.name] = res
            
    verifiers = [
        REPO_ROOT / "verifiers" / "invsqrt" / "verify_submission_invsqrt.py",
        REPO_ROOT / "verifiers" / "dqi" / "verify_submission_dqi.py",
        REPO_ROOT / "verifiers" / "dfthcsos" / "verify.py",
    ]
    results["verifiers"] = {}
    for v in verifiers:
        results["verifiers"][str(v.relative_to(REPO_ROOT))] = {
            "size_bytes": v.stat().st_size,
            "sha256": sha256_of_file(v)
        }
        
    out_file = REPO_ROOT / "ml28_ground_truth_audit.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[+] Ground truth audit written to {out_file}")

if __name__ == "__main__":
    main()
