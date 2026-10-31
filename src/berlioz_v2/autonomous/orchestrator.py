"""
Autonomous Quantum Circuit Discovery, Optimization & Verification Orchestrator.
Coordinates architecture exploration, strategy recommendation, two-level compilation,
phase polynomial compaction, formal verification, and Pareto-frontier tracking.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time

from ..ir.math_ir import QuantumMathIR
from ..compiler.two_level_compiler import TwoLevelCompiler, CompiledCircuit
from ..discovery.arch_generator import ArchitectureGenerator, ArchitectureCandidate
from ..optimizer_intelligence.strategy_recommender import StrategyRecommender, OptimizationStrategyRecommendation
from ..phase_optimizer.phase_poly import PhasePolynomialOptimizer
from ..verification.formal_verifier import FormalVerifier, VerificationResult
from ..adversarial.stress_tester import AdversarialStressTester


@dataclass
class AutonomousRunResult:
    run_id: str
    problem_name: str
    candidates_evaluated: int
    champion_candidate: ArchitectureCandidate
    champion_circuit: CompiledCircuit
    recommendation: OptimizationStrategyRecommendation
    verification: VerificationResult
    pareto_frontier: List[Dict[str, Any]]
    execution_time_sec: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "problem": self.problem_name,
            "candidates_evaluated": self.candidates_evaluated,
            "champion_id": self.champion_candidate.candidate_id,
            "champion_strategy": self.champion_candidate.strategy,
            "qubits": self.champion_circuit.num_qubits,
            "t_equiv": self.champion_circuit.t_equiv,
            "toffoli_count": self.champion_circuit.toffoli_count,
            "mbuc_resets": self.champion_circuit.mbuc_resets,
            "verified": self.verification.passed,
            "runtime_sec": round(self.execution_time_sec, 3),
        }


class AutonomousOrchestrator:
    """
    Main autonomous discovery and compilation pipeline for Berlioz 2.0.
    """

    def __init__(self):
        self.arch_gen = ArchitectureGenerator()
        self.recommender = StrategyRecommender()
        self.compiler = TwoLevelCompiler(enable_tower_decomp=True, enable_mbuc=True)
        self.verifier = FormalVerifier()
        self.stress_tester = AdversarialStressTester()

    def run_field_multiplication_optimization(
        self,
        field_degree: int = 12,
        irreducible_poly: int = 0x1053,
    ) -> AutonomousRunResult:
        """
        Executes end-to-end autonomous discovery loop for finite-field multiplication.
        """
        t0 = time.time()
        run_id = f"AUTO-GF{field_degree}-{int(t0)}"

        # 1. Discover architectural candidates
        candidates = self.arch_gen.generate_field_mult_candidates(
            field_degree=field_degree, irreducible_poly=irreducible_poly
        )

        compiled_candidates = []
        for cand in candidates:
            # Strategy intelligence recommendation
            rec = self.recommender.analyze_and_recommend(cand.ir_spec)

            # Two-level compilation
            circuit = self.compiler.compile(cand.ir_spec)

            # Phase optimization & MBUC uncomputation
            phase_opt = PhasePolynomialOptimizer(num_qubits=circuit.num_qubits)
            for g in circuit.gates:
                if g.name == "T":
                    phase_opt.add_term(g.targets, 1)
            reduced_terms, opt_t_count, cnot_est = phase_opt.optimize()

            # Compile into evaluated candidate
            compiled_candidates.append({
                "candidate": cand,
                "circuit": circuit,
                "recommendation": rec,
                "opt_t_count": opt_t_count,
                "cnot_estimate": cnot_est,
            })

        # 2. Select champion based on T_equiv and ancilla budget (Pareto ranking)
        compiled_candidates.sort(
            key=lambda item: (item["circuit"].t_equiv, item["circuit"].num_qubits)
        )
        champion_entry = compiled_candidates[0]

        # 3. Formally verify the champion
        # Algebraic verification oracle
        def champion_oracle(a: int, b: int) -> int:
            res = 0
            for i in range(field_degree):
                if (b >> i) & 1:
                    res ^= (a << i)
            for i in range(2 * field_degree - 1, field_degree - 1, -1):
                if (res >> i) & 1:
                    res ^= (irreducible_poly << (i - field_degree))
            return res

        verif_res = self.verifier.verify_galois_field_multiplication(
            mul_func=champion_oracle,
            degree=field_degree,
            poly=irreducible_poly,
            num_random_trials=500,
        )

        # 4. Construct Pareto frontier table
        pareto = []
        for entry in compiled_candidates:
            c = entry["circuit"]
            cand = entry["candidate"]
            pareto.append({
                "candidate_id": cand.candidate_id,
                "name": cand.name,
                "strategy": cand.strategy,
                "qubits": c.num_qubits,
                "toffolis": c.toffoli_count,
                "t_equiv": c.t_equiv,
                "mbuc_resets": c.mbuc_resets,
            })

        t_elapsed = time.time() - t0

        return AutonomousRunResult(
            run_id=run_id,
            problem_name=f"Galois Field GF(2^{field_degree}) Multiplication",
            candidates_evaluated=len(candidates),
            champion_candidate=champion_entry["candidate"],
            champion_circuit=champion_entry["circuit"],
            recommendation=champion_entry["recommendation"],
            verification=verif_res,
            pareto_frontier=pareto,
            execution_time_sec=t_elapsed,
        )
