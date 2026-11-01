"""Common data structures for the Reusable Quantum Circuit Discovery Engine.

Authors: BERLIOZ Discovery Agent
Context: BERLIOZ MASTERLOOP 26 - PART 6
Date: 2026-10-31
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class CandidateSpec:
    """Specification defining an algorithmic candidate before compilation."""
    candidate_id: str
    benchmark_id: str  # 'INVSQRT', 'DQI', 'CHEMISTRY'
    name: str
    strategy: str  # 'exhaustive', 'parameter_sweep', 'evolutionary', 'bayesian', 'graph', 'constraint'
    parameters: Dict[str, Any]
    source_revision: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    random_seed: int = 42

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def generate_id(cls, benchmark_id: str, strategy: str, params: Dict[str, Any]) -> str:
        param_str = json.dumps(params, sort_keys=True)
        h = hashlib.sha256(param_str.encode("utf-8")).hexdigest()[:8].upper()
        return f"CAND-{benchmark_id}-{strategy[:3].upper()}-{h}"


@dataclass
class CandidateArtifact:
    """Compiled circuit representation or simulation model."""
    spec: CandidateSpec
    artifact_path: Optional[Path]
    circuit_repr: Any
    artifact_sha256: str
    compilation_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CheckResult:
    """Result of static pre-compilation checks."""
    passed: bool
    rejection_reason: Optional[str] = None
    estimated_qubits: Optional[int] = None
    estimated_toffoli: Optional[int] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SemanticResult:
    """Result of reversible semantic verification."""
    passed: bool
    input_restored_exact: bool
    ancilla_clean_to_zero: bool
    mismatch_count: int = 0
    dirty_qubits: List[int] = field(default_factory=list)
    rejection_reason: Optional[str] = None


@dataclass
class PhaseResult:
    """Result of continuous / numerical phase verification."""
    passed: bool
    max_relative_error: float
    worst_error_ratio: float
    min_margin_slack: float
    worst_case_input: Any
    rejection_reason: Optional[str] = None
    tolerance_floor: float = 0.0


@dataclass
class ResourceMetrics:
    """Physical compiled circuit resource metrics."""
    active_qubits: int
    static_toffolis: int
    mean_dynamic_toffolis: float
    t_gates: float
    cnot_gates: int
    rotations: int
    circuit_depth: int
    t_equivalent_cost: float


@dataclass
class ScoreResult:
    """Official benchmark scoring evaluation."""
    benchmark_id: str
    official_score: float
    baseline_score: float
    benchmark_ratio: float
    composite_contribution: float
    is_superior_to_incumbent: bool
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CandidateRecord:
    """Comprehensive candidate record adhering to experiment_registry_schema.json."""
    experiment_id: str
    research_id: str
    candidate_id: str
    algorithm_id: str
    benchmark_id: str
    parameters: Dict[str, Any]
    source_revision: str
    build_config: Dict[str, Any]
    verification: Dict[str, Any]
    resources: Dict[str, Any]
    scoring: Dict[str, Any]
    results: Dict[str, Any] = field(default_factory=dict)
    artifact_hash: Optional[str] = None
    evidence_files: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if not d.get("results"):
            d["results"] = {
                "status": self.verification.get("overall_status", "PASS"),
                "logical_qubits": self.resources.get("active_qubits", 0),
                "peak_workspace": self.resources.get("active_qubits", 0),
                "static_toffolis": self.resources.get("static_toffolis", 0),
                "dynamic_mean_toffolis": self.resources.get("dynamic_mean_toffolis", 0.0),
                "t_equivalent_cost": self.resources.get("t_equivalent_cost", 0.0),
                "cnot_count": self.resources.get("cnot_gates", 0),
                "measurements": 0,
                "rotations": self.resources.get("rotations", 0),
                "circuit_depth": self.resources.get("circuit_depth", 0),
                "official_score": self.scoring.get("official_score", 0.0),
                "benchmark_ratio": self.scoring.get("benchmark_ratio", 0.0),
                "composite_contribution": self.scoring.get("benchmark_ratio", 0.0),
                "error_rate": self.verification.get("max_relative_error", 0.0),
                "runtime_seconds": self.duration_seconds
            }
        return d


class ParetoFrontier:
    """Maintains a persistent multi-objective Pareto frontier."""

    def __init__(self, benchmark_id: str):
        self.benchmark_id = benchmark_id
        self.candidates: List[CandidateRecord] = []

    def is_dominated(self, new_rec: CandidateRecord, existing: CandidateRecord) -> bool:
        """Returns True if existing dominates new_rec (lower qubits & lower Toffoli/score)."""
        q_new = new_rec.resources.get("active_qubits", float("inf"))
        c_new = new_rec.scoring.get("official_score", float("inf"))
        
        q_ex = existing.resources.get("active_qubits", float("inf"))
        c_ex = existing.scoring.get("official_score", float("inf"))
        
        return (q_ex <= q_new and c_ex <= c_new) and (q_ex < q_new or c_ex < c_new)

    def update(self, candidate: CandidateRecord) -> Tuple[bool, str]:
        """Attempts to insert candidate into Pareto frontier.
        
        Returns (is_pareto_optimal, status_message).
        """
        if candidate.verification.get("overall_status") != "PASS":
            return False, "REJECTED_VERIFICATION_FAILED"

        # Check if dominated by any existing point
        for ex in self.candidates:
            if self.is_dominated(candidate, ex):
                return False, f"DOMINATED_BY_{ex.candidate_id}"

        # Remove points dominated by the new candidate
        self.candidates = [ex for ex in self.candidates if not self.is_dominated(ex, candidate)]
        self.candidates.append(candidate)
        return True, "PARETO_OPTIMAL_INSERTED"

    def to_list(self) -> List[Dict[str, Any]]:
        return [c.to_dict() for c in self.candidates]
