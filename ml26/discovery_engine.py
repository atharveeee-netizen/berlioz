"""BERLIOZ Reusable Algorithm-to-Circuit Discovery Engine CLI & API.

Authors: BERLIOZ Discovery Agent
Context: BERLIOZ MASTERLOOP 26 - PART 6
Date: 2026-10-31

Entry point for multi-benchmark quantum circuit candidate discovery.
Supports:
- Benchmarks: INVSQRT, DQI, CHEMISTRY
- Strategies: exhaustive, parameter_sweep, evolutionary, bayesian, graph, constraint
- Verification: 6-stage verification pipeline
- Output: Persistent JSON registry, comparative CSV, and SYZYGY memory persistence
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

# Ensure repository root is on path
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.discovery.engine import DiscoveryEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="BERLIOZ Autonomous Quantum Circuit Discovery Engine")
    parser.add_argument("--benchmark", type=str, choices=["INVSQRT", "DQI", "CHEMISTRY", "ALL"], default="ALL",
                        help="Benchmark family to evaluate")
    parser.add_argument("--strategy", type=str, choices=["exhaustive", "parameter_sweep", "evolutionary", "bayesian", "graph", "constraint"],
                        default="exhaustive", help="Search strategy")
    parser.add_argument("--out-dir", type=Path, default=REPO_ROOT / "ml26", help="Output directory for reports")
    args = parser.parse_args()

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    engine = DiscoveryEngine(storage_dir=out_dir)
    print(f"[*] Initialized BERLIOZ Discovery Engine (Benchmark: {args.benchmark}, Strategy: {args.strategy})")

    if args.benchmark == "ALL":
        results = engine.run_full_suite(strategy=args.strategy)
    else:
        results = {args.benchmark: engine.run_discovery(args.benchmark, strategy=args.strategy)}

    # Save discovery results to JSON
    results_file = out_dir / "discovery_run_results.json"
    serializable_results = {
        b_id: [r.to_dict() for r in recs]
        for b_id, recs in results.items()
    }
    with open(results_file, "w") as f:
        json.dump(serializable_results, f, indent=2)
    print(f"[+] Saved discovery run results to {results_file}")

    # Save master Pareto frontier to JSON
    pareto_file = out_dir / "pareto_frontier_master.json"
    pareto_data = {
        b_id: engine.pareto_frontiers[b_id].to_list()
        for b_id in engine.pareto_frontiers
    }
    with open(pareto_file, "w") as f:
        json.dump(pareto_data, f, indent=2)
    print(f"[+] Saved master Pareto frontier to {pareto_file}")

    # Summary table
    print("\n" + "=" * 95)
    print(f"{'Benchmark':<12} | {'Candidate ID':<26} | {'Strategy':<12} | {'Qubits':<8} | {'Toffolis':<10} | {'Score / Ratio':<18} | {'Status'}")
    print("-" * 95)
    for b_id, recs in results.items():
        for r in recs:
            s = r.scoring
            res = r.resources
            v = r.verification
            ratio_str = f"{s.get('benchmark_ratio', 0.0):.4f}x" if s.get('benchmark_ratio') else "N/A"
            toff_str = f"{res.get('dynamic_mean_toffolis', 0):,.0f}" if res.get('dynamic_mean_toffolis') else "N/A"
            q_str = str(res.get('active_qubits', 'N/A'))
            status = v.get("overall_status", "UNKNOWN")
            if status == "PASS":
                status = s.get("status", "PASS")
            print(f"{b_id:<12} | {r.candidate_id:<26} | {r.algorithm_id:<12} | {q_str:<8} | {toff_str:<10} | {ratio_str:<18} | {status}")
    print("=" * 95)


if __name__ == "__main__":
    main()
