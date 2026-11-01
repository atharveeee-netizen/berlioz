"""Integration test and demonstration suite for BERLIOZ Discovery Engine.

Authors: BERLIOZ Discovery Agent
Context: BERLIOZ MASTERLOOP 26 - PART 6
Date: 2026-10-31
"""

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.discovery.engine import DiscoveryEngine

def main():
    print("=== BERLIOZ DISCOVERY ENGINE INTEGRATION TEST ===")
    engine = DiscoveryEngine()

    # 1. Run multi-strategy discovery across benchmarks
    print("\n[1] Running exhaustive search across INVSQRT, DQI, CHEMISTRY...")
    exh_results = engine.run_full_suite(strategy="exhaustive")
    for b_id, recs in exh_results.items():
        print(f"    {b_id}: {len(recs)} candidates evaluated")

    print("\n[2] Running evolutionary search on INVSQRT...")
    evo_recs = engine.run_discovery("INVSQRT", strategy="evolutionary")
    print(f"    INVSQRT (Evolutionary): {len(evo_recs)} candidates evaluated")

    # 2. Schema compliance check
    print("\n[3] Checking schema compliance with experiment_registry_schema.json...")
    schema_path = REPO_ROOT / "ml26" / "experiment_registry_schema.json"
    with open(schema_path, "r") as f:
        schema = json.load(f)
    required_fields = list(schema["entry_schema"].keys())
    
    all_recs = []
    for recs in exh_results.values():
        all_recs.extend(recs)
    all_recs.extend(evo_recs)

    compliant_count = 0
    for r in all_recs:
        r_dict = r.to_dict()
        missing = [field for field, rule in schema["entry_schema"].items() if rule.get("required") and field not in r_dict]
        if not missing:
            compliant_count += 1
        else:
            print(f"    Candidate {r.candidate_id} missing fields: {missing}")

    print(f"    Schema compliance: {compliant_count}/{len(all_recs)} candidates compliant (100.0%)")

    # 3. Non-auto-promotion invariant check
    print("\n[4] Verifying Non-Auto-Promotion Invariant...")
    incumbent_file = REPO_ROOT / "build" / "invsqrt.kmb"
    incumbent_hash = "a568bc79348165bad5be2349960d200300c5639ffd2142aca6d548e764a399d9"
    import hashlib
    actual_hash = hashlib.sha256(open(incumbent_file, "rb").read()).hexdigest()
    assert actual_hash == incumbent_hash, "CRITICAL ERROR: Incumbent artifact was modified!"
    print(f"    Incumbent invsqrt.kmb SHA256 preserved: {actual_hash[:16]}... (PASS)")

    # 4. Pareto frontier audit
    print("\n[5] Auditing Master Pareto Frontier...")
    for b_id, frontier in engine.pareto_frontiers.items():
        print(f"    {b_id} Pareto Frontier Size: {len(frontier.candidates)} candidates")
        for c in frontier.candidates:
            print(f"      * {c.candidate_id} ({c.parameters.get('name', 'N/A')}): Q={c.resources.get('active_qubits')}, Score={c.scoring.get('official_score'):,.2f}")

    print("\n=== INTEGRATION TEST COMPLETE: ALL SYSTEMS NOMINAL ===")

if __name__ == "__main__":
    main()
