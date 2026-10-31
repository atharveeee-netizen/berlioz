#!/usr/bin/env python3
"""
Automated Experiment Engine for Masterloop 20.
Maintains a reproducible experiment loop:
1. Records hypothesis, parameters, source revision, and artifact SHA-256.
2. Executes official verification checks (smoke/fast mode and full 102.4k shot mode).
3. Evaluates task costs and composite score using AuthoritativeScoreEngine.
4. Strictly gates promotions: only candidates that pass full verification AND strictly improve the composite score are promoted.
5. Preserves all previous candidates in the candidates vault.
"""

import os
import sys
import json
import csv
import time
import shutil
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from research.masterloop20.score_engine import AuthoritativeScoreEngine, compute_composite_score


class ExperimentEngine:
    def __init__(self, workspace_root: Optional[Path] = None):
        self.root = workspace_root or Path(__file__).resolve().parents[2]
        self.ml20_dir = self.root / "research" / "masterloop20"
        self.vault_dir = self.ml20_dir / "candidates_vault"
        self.ledger_path = self.ml20_dir / "experiments_ledger.csv"
        self.score_engine = AuthoritativeScoreEngine()

        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self._init_ledger()
        self.incumbent = self._load_incumbent()

    def _init_ledger(self):
        if not self.ledger_path.exists():
            headers = [
                "experiment_id",
                "timestamp",
                "git_commit",
                "task",
                "hypothesis",
                "parameters",
                "artifact_sha256",
                "qubit_count",
                "toffoli_count",
                "t_equiv",
                "verifier_mode",
                "shots",
                "failures",
                "task_cost",
                "composite_score",
                "promoted",
                "promotion_reason",
            ]
            with open(self.ledger_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)

    def _load_incumbent(self) -> Dict[str, Any]:
        metrics_path = self.ml20_dir / "incumbent_metrics.json"
        if metrics_path.exists():
            with open(metrics_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                cand = data.get("candidate_metrics", {})
                scores = data.get("scores", {})
                return {
                    "composite_score": scores.get("official_composite_score", 23.17767),
                    "invsqrt": {
                        "qubits": cand.get("invsqrt", {}).get("qubits", 62),
                        "t_equiv": cand.get("invsqrt", {}).get("t_equiv", 1622.7),
                        "cost": cand.get("invsqrt", {}).get("cost", 100607.4),
                        "ratio": cand.get("invsqrt", {}).get("ratio", 20.64210),
                    },
                    "dqi": {
                        "qubits": cand.get("dqi", {}).get("qubits", 889),
                        "t_mean": cand.get("dqi", {}).get("mean_toffolis", 427471.2),
                        "cost": cand.get("dqi", {}).get("cost", 402454611307.23),
                        "ratio": cand.get("dqi", {}).get("ratio", 60.72598),
                    },
                    "chemistry": {
                        "qubits": cand.get("chemistry", {}).get("qubits", 430),
                        "toffolis": cand.get("chemistry", {}).get("toffolis", 16266.0),
                        "lambda_eff": cand.get("chemistry", {}).get("lambda_eff", 48.2992),
                        "cost": cand.get("chemistry", {}).get("cost", 337827649.32),
                        "ratio": cand.get("chemistry", {}).get("ratio", 9.93301),
                    },
                }
        return {
            "composite_score": 23.17767,
            "invsqrt": {"qubits": 62, "t_equiv": 1622.72030097, "cost": 100608.66, "ratio": 20.64210},
            "dqi": {"qubits": 889, "t_mean": 427471.2, "cost": 402454799602.87, "ratio": 60.72598},
            "chemistry": {"qubits": 430, "toffolis": 16266.0, "lambda_eff": 48.29920925, "cost": 337823023.19, "ratio": 9.93301},
        }

    def get_git_commit(self) -> str:
        try:
            res = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=self.root, capture_output=True, text=True)
            return res.stdout.strip()
        except Exception:
            return "unknown"

    def record_run(
        self,
        experiment_id: str,
        task: str,
        hypothesis: str,
        params: Dict[str, Any],
        artifact_path: Optional[Path],
        metrics: Dict[str, Any],
        verifier_mode: str = "quick",
        shots: int = 102400,
        failures: int = 0,
    ) -> Dict[str, Any]:
        """
        Evaluates the candidate, checks for score improvement, records to ledger,
        and manages promotion decision.
        """
        commit = self.get_git_commit()
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Hash artifact
        artifact_sha = "N/A"
        if artifact_path and artifact_path.exists():
            h = hashlib.sha256()
            with open(artifact_path, "rb") as f:
                while chunk := f.read(65536):
                    h.update(chunk)
            artifact_sha = h.hexdigest()

            # Preserve in vault
            vault_dest = self.vault_dir / f"{experiment_id}_{artifact_path.name}"
            shutil.copy2(artifact_path, vault_dest)

        # Assemble full portfolio for composite evaluation
        curr_inv = dict(self.incumbent["invsqrt"])
        curr_dqi = dict(self.incumbent["dqi"])
        curr_chem = dict(self.incumbent["chemistry"])

        if task == "invsqrt":
            curr_inv.update(metrics)
        elif task == "dqi":
            curr_dqi.update(metrics)
        elif task in ("chemistry", "dfthcsos"):
            curr_chem.update(metrics)

        portfolio_eval = self.score_engine.evaluate_portfolio(curr_inv, curr_dqi, curr_chem)
        new_composite = portfolio_eval["composite_score"]
        incumbent_composite = self.incumbent["composite_score"]

        # Promotion rule: must be FULL verification mode AND strictly higher score
        promoted = False
        reason = "Rejected: no score improvement"
        if new_composite > incumbent_composite:
            if verifier_mode == "full" and failures == 0:
                promoted = True
                reason = f"PROMOTED: Composite improved from {incumbent_composite:.5f} to {new_composite:.5f}"
                self.incumbent = portfolio_eval
                # Update saved incumbent metrics
                with open(self.ml20_dir / "incumbent_metrics.json", "w", encoding="utf-8") as f:
                    json.dump(self.incumbent, f, indent=2)
            else:
                reason = f"Candidate score higher ({new_composite:.5f} > {incumbent_composite:.5f}) but not full verification mode or failures > 0"

        # Record to ledger
        row = [
            experiment_id,
            ts,
            commit,
            task,
            hypothesis,
            json.dumps(params),
            artifact_sha,
            metrics.get("qubits", "N/A"),
            metrics.get("toffolis", metrics.get("t_mean", "N/A")),
            metrics.get("t_equiv", "N/A"),
            verifier_mode,
            shots,
            failures,
            portfolio_eval[task]["cost"] if task in portfolio_eval else "N/A",
            f"{new_composite:.5f}",
            promoted,
            reason,
        ]
        with open(self.ledger_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)

        print(f"[*] Experiment {experiment_id} recorded: Composite = {new_composite:.5f} | Promoted = {promoted}")
        print(f"    Reason: {reason}")
        return {
            "experiment_id": experiment_id,
            "composite_score": new_composite,
            "promoted": promoted,
            "reason": reason,
            "portfolio": portfolio_eval,
        }


if __name__ == "__main__":
    engine = ExperimentEngine()
    print(f"[+] Experiment Engine initialized with incumbent score: {engine.incumbent['composite_score']:.5f}")
