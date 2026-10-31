"""
Berlioz 2.0: Autonomous Quantum Circuit Discovery, Optimization, Verification & Generalization Platform.
"""

__version__ = "2.0.0"
__author__ = "Berlioz Team (TuringIRL)"

from .ir.math_ir import MathOp, FieldOp, ArithmeticOp, QuantumMathIR
from .compiler.two_level_compiler import TwoLevelCompiler
from .discovery.arch_generator import ArchitectureGenerator
from .optimizer_intelligence.strategy_recommender import StrategyRecommender
from .phase_optimizer.phase_poly import PhasePolynomialOptimizer
from .verification.formal_verifier import FormalVerifier
from .adversarial.stress_tester import AdversarialStressTester
from .autonomous.orchestrator import AutonomousOrchestrator

__all__ = [
    "MathOp",
    "FieldOp",
    "ArithmeticOp",
    "QuantumMathIR",
    "TwoLevelCompiler",
    "ArchitectureGenerator",
    "StrategyRecommender",
    "PhasePolynomialOptimizer",
    "FormalVerifier",
    "AdversarialStressTester",
    "AutonomousOrchestrator",
]
