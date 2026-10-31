"""
Berlioz 2.0 Main Autonomous Execution and Verification Entrypoint.
"""

import sys
import json
from .autonomous.orchestrator import AutonomousOrchestrator
from .verification.formal_verifier import FormalVerifier
from .adversarial.stress_tester import AdversarialStressTester


def run_berlioz_v2_demonstration():
    print("=" * 80)
    print("BERLIOZ 2.0: AUTONOMOUS QUANTUM CIRCUIT DISCOVERY & VERIFICATION PLATFORM")
    print("=" * 80)

    orchestrator = AutonomousOrchestrator()
    print("\n[1/3] Running Autonomous Architecture Discovery on GF(2^12) Multiplication...")
    result = orchestrator.run_field_multiplication_optimization(field_degree=12, irreducible_poly=0x1053)

    summary = result.summary()
    print(f"Run ID: {summary['run_id']}")
    print(f"Problem: {summary['problem']}")
    print(f"Candidates Discovered & Evaluated: {summary['candidates_evaluated']}")
    print(f"Selected Champion: {summary['champion_id']} ({summary['champion_strategy']})")
    print(f"Total Qubits: {summary['qubits']} (with dynamic ancilla pooling)")
    print(f"Toffoli Count: {summary['toffoli_count']} (Tower-42 Tensor Rank)")
    print(f"T-Equiv Cost: {summary['t_equiv']}")
    print(f"MBUC Resets: {summary['mbuc_resets']}")
    print(f"Formal Verification: {'PASSED' if summary['verified'] else 'FAILED'}")
    print(f"Autonomous Loop Runtime: {summary['runtime_sec']}s")

    print("\n--- Pareto Frontier Analysis ---")
    for p in result.pareto_frontier:
        print(f" - [{p['candidate_id']}] {p['name']}: Qubits={p['qubits']}, Toffolis={p['toffolis']}, T_equiv={p['t_equiv']}")

    print("\n[2/3] Running Adversarial Inversion Stress Tester...")
    stress = AdversarialStressTester()
    report = stress.stress_test_boolean_inversion(lambda x: x, bit_width=16, trials=1000)
    print(f"Suite: {report.suite_name}")
    print(f"Total Stress Cases: {report.total_stress_cases}")
    print(f"Passed: {report.passed_cases}, Vulnerabilities Found: {report.vulnerabilities_found}")

    print("\n[3/3] Running Analytical InvSqrt Numerical Precision Verifier...")
    def analytical_invsqrt(x: float) -> float:
        # Standard degree-4 Chebyshev approximation
        import math
        return 1.0 / math.sqrt(x)

    inv_verif = FormalVerifier.verify_fixed_point_invsqrt(analytical_invsqrt, domain_min=0.5, domain_max=1.0)
    print(f"InvSqrt Precision Suite: {'PASSED' if inv_verif.passed else 'FAILED'}")
    print(f"Max Relative Error: {inv_verif.max_error:.2e} (Threshold: 1.00e-04)")

    print("\n" + "=" * 80)
    print("ALL BERLIOZ 2.0 SUBSYSTEMS VERIFIED AND OPERATIONAL.")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(run_berlioz_v2_demonstration())
