"""Central Reusable Quantum Circuit Discovery Engine.

Authors: BERLIOZ Discovery Agent
Context: BERLIOZ MASTERLOOP 26 - PART 6
Date: 2026-10-31
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from src.discovery.interfaces import BenchmarkPlugin
from src.discovery.plugins.chemistry import ChemistryPlugin
from src.discovery.plugins.dqi import DQIPlugin
from src.discovery.plugins.invsqrt import InvsqrtPlugin
from src.discovery.types import (
    CandidateArtifact,
    CandidateRecord,
    CandidateSpec,
    CheckResult,
    ParetoFrontier,
    PhaseResult,
    ResourceMetrics,
    ScoreResult,
    SemanticResult,
)

# SYZYGY Client integration
SYZYGY_PATH = Path("C:/Users/noobg/.gemini/antigravity-ide/scratch/syzygy")
if str(SYZYGY_PATH) not in sys.path:
    sys.path.insert(0, str(SYZYGY_PATH))

try:
    from core.memory import OpenVikingClient
    HAS_SYZYGY = True
except ImportError:
    HAS_SYZYGY = False

logger = logging.getLogger("BERLIOZ.DiscoveryEngine")


class DiscoveryEngine:
    """Autonomous algorithm-to-circuit discovery engine for multi-benchmark quantum compilation."""

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path("ml26")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Register benchmark plugins
        self.plugins: Dict[str, BenchmarkPlugin] = {
            "INVSQRT": InvsqrtPlugin(),
            "DQI": DQIPlugin(),
            "CHEMISTRY": ChemistryPlugin(),
        }

        # Initialize Pareto frontiers
        self.pareto_frontiers: Dict[str, ParetoFrontier] = {
            b_id: ParetoFrontier(b_id) for b_id in self.plugins
        }

        # Connect to SYZYGY memory
        self.viking_client = OpenVikingClient() if HAS_SYZYGY else None

    def register_plugin(self, plugin: BenchmarkPlugin) -> None:
        """Registers a custom benchmark plugin."""
        self.plugins[plugin.benchmark_id] = plugin
        if plugin.benchmark_id not in self.pareto_frontiers:
            self.pareto_frontiers[plugin.benchmark_id] = ParetoFrontier(plugin.benchmark_id)

    def evaluate_candidate(self, plugin: BenchmarkPlugin, spec: CandidateSpec) -> CandidateRecord:
        """Executes the full 6-stage candidate verification and resource extraction pipeline."""
        start_time = time.time()
        research_id = f"RES-{spec.benchmark_id}"
        exp_id = f"EXP-{spec.candidate_id}"

        # Stage 1: Static Checks
        check = plugin.static_checks(spec)
        if not check.passed:
            duration = time.time() - start_time
            return CandidateRecord(
                experiment_id=exp_id,
                research_id=research_id,
                candidate_id=spec.candidate_id,
                algorithm_id=spec.strategy,
                benchmark_id=spec.benchmark_id,
                parameters=spec.parameters,
                source_revision=spec.source_revision,
                build_config={"status": "STATIC_CHECK_FAILED", "reason": check.rejection_reason},
                verification={"overall_status": "REJECTED_STATIC_CHECK", "rejection_reason": check.rejection_reason},
                resources={},
                scoring={},
                artifact_hash=None,
                evidence_files=[],
                duration_seconds=duration
            )

        # Stage 2: Compilation
        try:
            artifact = plugin.compile(spec)
        except Exception as e:
            duration = time.time() - start_time
            return CandidateRecord(
                experiment_id=exp_id,
                research_id=research_id,
                candidate_id=spec.candidate_id,
                algorithm_id=spec.strategy,
                benchmark_id=spec.benchmark_id,
                parameters=spec.parameters,
                source_revision=spec.source_revision,
                build_config={"status": "COMPILATION_ERROR", "error": str(e)},
                verification={"overall_status": "REJECTED_COMPILATION_FAILED", "error": str(e)},
                resources={},
                scoring={},
                artifact_hash=None,
                evidence_files=[],
                duration_seconds=duration
            )

        # Stage 3: Semantic Verification
        semantic = plugin.semantic_verification(artifact)
        if not semantic.passed:
            duration = time.time() - start_time
            return CandidateRecord(
                experiment_id=exp_id,
                research_id=research_id,
                candidate_id=spec.candidate_id,
                algorithm_id=spec.strategy,
                benchmark_id=spec.benchmark_id,
                parameters=spec.parameters,
                source_revision=spec.source_revision,
                build_config=artifact.compilation_metadata,
                verification={
                    "overall_status": "REJECTED_SEMANTIC_FAILED",
                    "input_restored": semantic.input_restored_exact,
                    "ancilla_clean": semantic.ancilla_clean_to_zero,
                    "reason": semantic.rejection_reason
                },
                resources={},
                scoring={},
                artifact_hash=artifact.artifact_sha256,
                evidence_files=[],
                duration_seconds=duration
            )

        # Stage 4: Phase Verification
        phase = plugin.phase_verification(artifact)
        if not phase.passed:
            duration = time.time() - start_time
            return CandidateRecord(
                experiment_id=exp_id,
                research_id=research_id,
                candidate_id=spec.candidate_id,
                algorithm_id=spec.strategy,
                benchmark_id=spec.benchmark_id,
                parameters=spec.parameters,
                source_revision=spec.source_revision,
                build_config=artifact.compilation_metadata,
                verification={
                    "overall_status": "REJECTED_PHASE_FAILED",
                    "max_relative_error": phase.max_relative_error,
                    "worst_ratio": phase.worst_error_ratio,
                    "reason": phase.rejection_reason
                },
                resources={},
                scoring={},
                artifact_hash=artifact.artifact_sha256,
                evidence_files=[],
                duration_seconds=duration
            )

        # Stage 5: Resource Measurement
        resources = plugin.measure_resources(artifact)

        # Stage 6: Official Scoring
        # Retrieve explicit parameters for chemistry if present
        if spec.benchmark_id == "CHEMISTRY":
            p = spec.parameters
            score = p.get("lambda_eff", 48.323649) * resources.mean_dynamic_toffolis * resources.active_qubits
            ratio = plugin.baseline_score / score
            is_sup = score < plugin.incumbent_score
            scoring = ScoreResult(
                benchmark_id="CHEMISTRY",
                official_score=score,
                baseline_score=plugin.baseline_score,
                benchmark_ratio=ratio,
                composite_contribution=ratio,
                is_superior_to_incumbent=is_sup,
                details={"score": score, "lambda_eff": p.get("lambda_eff", 48.323649)}
            )
        else:
            scoring = plugin.official_scoring(resources, phase)

        duration = time.time() - start_time

        # Build candidate record conforming to experiment_registry_schema.json
        rec = CandidateRecord(
            experiment_id=exp_id,
            research_id=research_id,
            candidate_id=spec.candidate_id,
            algorithm_id=spec.strategy,
            benchmark_id=spec.benchmark_id,
            parameters=spec.parameters,
            source_revision=spec.source_revision,
            build_config=artifact.compilation_metadata,
            verification={
                "overall_status": "PASS",
                "semantic_passed": semantic.passed,
                "input_restored": semantic.input_restored_exact,
                "ancilla_clean": semantic.ancilla_clean_to_zero,
                "phase_passed": phase.passed,
                "max_relative_error": phase.max_relative_error,
                "worst_ratio_over_tolerance": phase.worst_error_ratio,
                "min_margin_slack": phase.min_margin_slack
            },
            resources={
                "active_qubits": resources.active_qubits,
                "static_toffolis": resources.static_toffolis,
                "dynamic_mean_toffolis": resources.mean_dynamic_toffolis,
                "t_equivalent_cost": resources.t_equivalent_cost,
                "t_gates": resources.t_gates,
                "cnot_gates": resources.cnot_gates,
                "rotations": resources.rotations,
                "circuit_depth": resources.circuit_depth
            },
            scoring={
                "official_score": scoring.official_score,
                "benchmark_ratio": scoring.benchmark_ratio,
                "baseline_score": scoring.baseline_score,
                "is_superior_to_incumbent": scoring.is_superior_to_incumbent,
                "status": "CANDIDATE_SUPERIOR" if scoring.is_superior_to_incumbent else "VERIFIED_SUBOPTIMAL"
            },
            artifact_hash=artifact.artifact_sha256,
            evidence_files=[],
            duration_seconds=duration
        )

        # Update Pareto frontier
        frontier = self.pareto_frontiers[spec.benchmark_id]
        is_pareto, status_msg = frontier.update(rec)
        rec.scoring["pareto_status"] = status_msg

        # Store in SYZYGY memory
        if self.viking_client:
            uri = f"viking://berlioz/experiments/{spec.candidate_id}"
            try:
                self.viking_client.put(uri, rec.to_dict())
            except Exception as e:
                logger.warning(f"Could not store {uri} in SYZYGY: {e}")

        return rec

    def run_discovery(self, benchmark_id: str, strategy: str = "exhaustive", **kwargs) -> List[CandidateRecord]:
        """Runs candidate discovery for a given benchmark and search strategy."""
        plugin = self.plugins.get(benchmark_id)
        if not plugin:
            raise ValueError(f"Unknown benchmark family: {benchmark_id}")

        candidates = plugin.generate_candidates(strategy, **kwargs)
        records = []
        for spec in candidates:
            rec = self.evaluate_candidate(plugin, spec)
            records.append(rec)

        return records

    def run_full_suite(self, strategy: str = "exhaustive") -> Dict[str, List[CandidateRecord]]:
        """Runs candidate discovery across all three registered benchmark families."""
        results = {}
        for b_id in ["INVSQRT", "DQI", "CHEMISTRY"]:
            results[b_id] = self.run_discovery(b_id, strategy=strategy)

        # Update master Pareto frontier in SYZYGY
        if self.viking_client:
            pareto_data = {
                b_id: self.pareto_frontiers[b_id].to_list()
                for b_id in self.pareto_frontiers
            }
            try:
                self.viking_client.put("viking://berlioz/discovery/pareto", pareto_data)
            except Exception as e:
                logger.warning(f"Could not update viking://berlioz/discovery/pareto: {e}")

        return results
