"""Abstract benchmark plugin interface for quantum circuit candidate discovery.

Authors: BERLIOZ Discovery Agent
Context: BERLIOZ MASTERLOOP 26 - PART 6
Date: 2026-10-31
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Optional

from src.discovery.types import (
    CandidateArtifact,
    CandidateSpec,
    CheckResult,
    PhaseResult,
    ResourceMetrics,
    ScoreResult,
    SemanticResult,
)


class BenchmarkPlugin(ABC):
    """Abstract interface defining a self-contained quantum benchmark family."""

    @property
    @abstractmethod
    def benchmark_id(self) -> str:
        """Returns benchmark identifier: 'INVSQRT', 'DQI', or 'CHEMISTRY'."""
        pass

    @property
    @abstractmethod
    def hard_qubit_ceiling(self) -> Optional[int]:
        """Returns hard physical qubit cap if one exists (e.g., 128 for Chemistry, 64 for Invsqrt)."""
        pass

    @property
    @abstractmethod
    def baseline_score(self) -> float:
        """Returns the reference competition baseline score."""
        pass

    @property
    @abstractmethod
    def incumbent_score(self) -> float:
        """Returns the current champion score."""
        pass

    @abstractmethod
    def generate_candidates(self, strategy: str, **kwargs) -> Iterable[CandidateSpec]:
        """Generates candidate specifications according to the chosen search strategy."""
        pass

    @abstractmethod
    def static_checks(self, spec: CandidateSpec) -> CheckResult:
        """Fast pre-compilation filtering (qubit estimation, parameter feasibility)."""
        pass

    @abstractmethod
    def compile(self, spec: CandidateSpec) -> CandidateArtifact:
        """Synthesizes or compiles the candidate specification into executable circuit representations."""
        pass

    @abstractmethod
    def semantic_verification(self, artifact: CandidateArtifact) -> SemanticResult:
        """Verifies bit-exact input restoration and 100% clean ancilla return to |0>."""
        pass

    @abstractmethod
    def phase_verification(self, artifact: CandidateArtifact) -> PhaseResult:
        """Verifies numerical accuracy, SOS eigenvalue bounds, and remaining margin slack."""
        pass

    @abstractmethod
    def measure_resources(self, artifact: CandidateArtifact) -> ResourceMetrics:
        """Extracts physical circuit resources (Qubits, Toffolis, T-count, CNOTs, Depth)."""
        pass

    @abstractmethod
    def official_scoring(self, metrics: ResourceMetrics, phase: PhaseResult) -> ScoreResult:
        """Computes official competition metric and ratio against historical baseline."""
        pass
