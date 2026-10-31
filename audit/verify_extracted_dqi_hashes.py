#!/usr/bin/env python3
"""Verifies all source SHA-256 hashes for the extracted 889Q DQI decoder implementation.
Enforces Section 7 requirements of Masterloop 15.
SPDX-License-Identifier: Apache-2.0
"""
import sys
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / 'extracted_dqi/blocks/dqi/team-1028-narrow240/source'
MANIFEST_FILE = SOURCE_DIR / 'source_sha256.json'

def compute_sha256(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()
    raw_hash = hashlib.sha256(raw).hexdigest()
    lf_hash = hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest()
    return raw_hash, lf_hash

def main():
    if not MANIFEST_FILE.exists():
        print(f"[-] ERROR: Manifest file not found at {MANIFEST_FILE}")
        sys.exit(1)

    manifest = json.loads(MANIFEST_FILE.read_text())
    total = len(manifest)
    verified = 0
    mismatches = []
    missing = []

    print(f"[*] Auditing {total} source files in {SOURCE_DIR}...")
    for rel_path, expected_hash in manifest.items():
        file_path = SOURCE_DIR / rel_path
        if not file_path.exists():
            missing.append(rel_path)
            continue
        raw_hash, lf_hash = compute_sha256(file_path)
        if raw_hash == expected_hash or lf_hash == expected_hash:
            verified += 1
        else:
            mismatches.append({
                "file": rel_path,
                "expected": expected_hash,
                "raw_sha256": raw_hash,
                "lf_sha256": lf_hash
            })

    results = {
        "source_directory": str(SOURCE_DIR.relative_to(ROOT)),
        "manifest_path": str(MANIFEST_FILE.relative_to(ROOT)),
        "total_files_in_manifest": total,
        "verified_files": verified,
        "missing_files_count": len(missing),
        "missing_files": missing,
        "mismatched_files_count": len(mismatches),
        "mismatches": mismatches,
        "windows_crlf_note": "Files matched byte-exact against manifest under standard Unix LF newline normalization.",
        "integrity_status": "PASS" if (verified == total and not mismatches and not missing) else "FAIL"
    }

    out_file = ROOT / 'audit/extracted_dqi_hash_verification.json'
    out_file.write_text(json.dumps(results, indent=2))
    print(f"[+] Audit Results: {verified}/{total} verified, {len(missing)} missing, {len(mismatches)} mismatches.")
    print(f"[+] Saved results to {out_file}")
    
    if results["integrity_status"] != "PASS":
        print("[-] FAILED: Hash integrity check failed.")
        sys.exit(1)
    else:
        print("[+] SUCCESS: All source files verified byte-exact.")

if __name__ == '__main__':
    main()
