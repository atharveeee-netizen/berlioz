# 00_LANDSCAPE: QUANTUM CIRCUIT COMPILATION COMPETITION LANDSCAPE
**Google Quantum AI — Verifiable Quantum Circuit Compilation (Kaggle)**  
**Benchmark Closing Date**: January 20, 2027  
**Official Verifier Framework**: `kickmix` (inside `github.com/quantumlib/Qualtran`)  
**Date**: October 30, 2026  

---

## 1. Ground Truth Primary Literature

### 1.1 The Organizing Paper
* **Citation**: H. Khattar, N. C. Rubin, C. Gidney, M. Broughton, G. H. Low, R. Babbush, *"Leveraging Verifiable Structure in Quantum Circuit Compilation"*, arXiv:2610.23832 (Google Quantum AI, Oct 2026).
* **Core Contribution**:
  * Formulates three verifiable compilation benchmarks where fast classical verification is guaranteed despite exponential Hilbert space size.
  * Introduces the `kickmix` C++ Pauli frame and Clifford+Toffoli simulator supporting measurement-based uncomputation (`HMR` and `R`), classical condition blocks (`if b`), and automated phase tracking.
  * Defines the official geometric mean competition scoring metric:
    $$\text{Score} = \left(\frac{\text{Ref}_{\text{invsqrt}}}{\text{Cost}_{\text{invsqrt}}} \times \frac{\text{Ref}_{\text{dqi}}}{\text{Cost}_{\text{dqi}}} \times \frac{\text{Ref}_{\text{dfthcsos}}}{\text{Cost}_{\text{dfthcsos}}}\right)^{1/3}$$
  * Fixes the baseline reference costs:
    * $\text{Ref}_{\text{invsqrt}} = 2{,}076{,}774.2337$
    * $\text{Ref}_{\text{dqi}} = 24{,}439{,}463{,}583{,}672.93$
    * $\text{Ref}_{\text{dfthcsos}} = 3{,}355{,}599{,}588.3155$

### 1.2 Benchmark II: Decoded Quantum Interferometry (DQI)
* **Citation**: D. Maslov, S. P. Jordan et al., *"Verifiable Quantum Advantage via Optimized DQI Circuits"*, arXiv:2510.10967 (Oct 2025); and arXiv:2408.08292.
* **Core Definition**:
  * **DQI stands for Decoded Quantum Interferometry**, NOT Data-Qubit-Interleaved Surface Codes.
  * Implements an $\text{RS}(4095, 4025)$ Reed-Solomon syndrome decoder over the finite field $\text{GF}(2^{12})$ correcting up to $l = 35$ errors from $n = 70$ syndromes.
  * Given quantum syndrome registers $S_0, \dots, S_{n-1}$ and classical measurement registers $E_0, \dots, E_{m-1}$, applies the kickback phase:
    $$(-1)^{\sum_j \text{popcount}(e_j \ \& \ E_j)}$$
    where $e = \text{decode}(S)$, and restores all syndrome and scratch qubits cleanly to $|0\rangle$.
  * Evaluation uses 102,400 shots drawn from the DQI error-weight distribution. Cost is penalized by the Clopper-Pearson failure-rate upper bound:
    $$\text{Cost}_{\text{dqi}} = R(\epsilon^+) \times Q^2 \times T_{\text{mean}}$$
    where $R(\epsilon) = \ln(2) / -\ln(1/2 + 2\sqrt{\epsilon})$, $Q$ is peak qubits, and $T_{\text{mean}}$ is mean Toffolis per shot.

### 1.3 LLM Evolutionary Optimization & Kickmix Arena
* **Citation**: Y. Gu, A. Kemeny, S. F. Yelin, M. D. Lukin, *"Automated Circuit Optimization with Large Language Models"*, arXiv:2610.22367 (Harvard, Anthropic, QuEra, Oct 2026).
* **Core Takeaways**:
  * Evaluator: `tatra-labs/kickmix-arena`.
  * Demonstrates that generic LLM trial-and-error loops against a verifier converge on public heuristics (e.g. standard Karatsuba decompositions and Peephole optimizations).
  * Consequence: Merely running an "agent loop against the verifier" is NOT a novel research contribution. Novelty requires domain-specific algebraic breakthroughs, exact synthesis, or architectural co-design.

### 1.4 Benchmark III: Electronic Structure Simulation (DF-THC)
* **Citation**: J. Lee, D. W. Berry, C. Gidney, W. J. Huggins, J. R. McClean, N. Wiebe, R. Babbush, *"Even More Efficient Quantum Computation of Chemistry Through Tensor Hypercontraction"*, PRX Quantum 2, 030305 (2021).
* **Core Takeaways**:
  * Simulates active FeMoCo cofactor ($76$ orbitals, $113$ electrons) from `FeMoCo76o113e.fcidump`.
  * Double factorizes the two-electron Coulomb integral:
    $$V_{pqrs} \approx \sum_{t=1}^M \zeta_{pq}^t \zeta_{rs}^t, \quad \zeta_{pq}^t = \sum_{\mu=1}^N \sum_{\nu=1}^N \chi_\mu(p) \chi_\nu(q) W_{\mu\nu}^t$$
  * Cost: $\lambda_{\text{eff}} \times T_{\text{total}} \times Q_{\text{total}}$, subject to chemical accuracy bounds $e_1 \le 20\text{ mHa}$, $e_2 \le 20\text{ mHa}$, and gap condition $E_{\text{gap}} \in [3.8, 4.0]\text{ Ha}$.
  * Angle circuits are restricted to $Q_{\text{angle}} \le 128$ qubits with zero T-gates.

---

## 2. Competitive Landscape & Public Solutions

The competition has seen rapid convergence across several public notebooks:

| Competitor / Team | Public Artifacts | Core Techniques Used | Impact on Benchmarks | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Yoyobar** | `yoyobar_lb-22-99-invsqrt-101-62-qubits.ipynb` | 62-qubit, 101-Toffoli Newton-Raphson polynomial seed table with zero phase drift. Cost: 101,002. | Invsqrt Ratio: **$20.56\times$** | **SATURATED**: Near theoretical limit. |
| **SomeJoint / Agniv Banerjee** | `somejoint_quantum-circuits-22-77-local-gm-889-qubit-dqi.ipynb` | 889-qubit streamed RS decoder with paired extraction chains and Bézout-Hankel solvers. | DQI Ratio: **$59.57\times$** | **BASELINE**: 63-AND multiplier in place. |
| **Avazaku (Sargis Khachatryan)** | `avazaku_dqi-exact-42-and-arithmetic-full-verification.ipynb` | Bilinear rank-42 multiplication in $\text{GF}(2^{12})$ via $\text{GF}(8)$ tower. 21.18% Toffoli drop. | DQI Ratio: **$75.57\times$** (isolated) | **ADAPTED**: Standard tower construction. |
| **Michael Rustad** | `michaelrustad_vqcc-r10-merged-group-chemistry-12-87-lb.ipynb` | $R=10, B=129, C=60$ factor matrix with $\lambda_{\text{eff}} = 48.0311$; half-open Givens gauge `bit(7)==bit(6)`. | Chem Ratio: **$5.09\times$ - $9.93\times$** | **ACTIVE**: Uncoupled swap risk if manual. |
| **Atakan Aldemir & Dmitriy Abulkhanov** | `atakanaldemir_qcc-888q-repair-and-native-chemistry-co-design.ipynb` | Co-design of native chemistry rotation circuits with 888Q/889Q DQI repairs. | Composite Score: **$22.995$** | **ACTIVE**: Basis for live score 22.99. |

---

## 3. What is Saturated vs. Where the Frontier Lies

### Saturated Dimensions
1. **Invsqrt standard polynomial tuning**: The 62-qubit NR design is operating with worst-case relative error $0.9993 \times \text{tol}$. Incremental polynomial tweaking yields $< 0.5\%$ improvement.
2. **Standard 42-AND multiplier integration**: Evaluating 42 products via $\text{GF}(8)$ tower is well-understood and public. Re-implementing 42 products without higher-order algorithmic restructuring (e.g., quadratic-phase erasure or register compaction) does not bridge the gap to Score 50.
3. **Naive factor matrix swapping**: Attempting to interchange uncoupled `submission.npz` files with independent angle circuits triggers catastrophic chemical accuracy violations ($e_1 > 60{,}000\text{ mHa}$).

### The Open High-Value Levers
1. **DQI Quadratic-Phase Erasure**: Because $\text{GF}(2^{12})$ products are bilinear in their inputs, intermediate product registers can be erased via CNOT basis changes and CZ networks for ZERO Toffolis instead of running inverse multipliers.
2. **DQI Promise-Specialized Speculative Decoder**: RS decoder iteration bounds are set to 222 worst-case iterations. Exploiting typical error mass ($k \ll 35$) while bounding Clopper-Pearson $\epsilon^+$ offers massive Toffoli reductions.
3. **Chemistry Table-Content Co-Design & QROM Angle Batching**: Givens angle rounding is a logic-synthesis don't-care within the 20 mHa tolerance window. Choosing entries that optimize ANF degree and unary iteration trees while maximally batching ($J=7$) cuts angle Toffolis significantly.
4. **Scorer Price-Book Exploitation**: Profiling the exact cost models across executed conditional blocks, dirty ancilla reuse, and Z_POW rotation precision.
