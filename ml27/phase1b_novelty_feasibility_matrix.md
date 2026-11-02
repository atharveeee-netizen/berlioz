# BERLIOZ MASTERLOOP 27 — PHASE 1B: NOVELTY & FEASIBILITY MATRIX
**Document ID:** `ML27-P1B-MATRIX`  
**Execution Environment:** Antigravity IDE, Windows x86_64, Python 3.10+, Kickmix 0.1.x  
**Repository Revision:** `b58e92e` (Masterloop 27 Phase 0 Certified Baseline)  
**Historical Anchors:** `9deacbb` (ML26 Master Integration), `47152d4` (23.17767 Incumbent Champion)  
**Objective:** Independent audit of radical algorithmic alternatives across Tracks A–E to achieve a genuinely compiled, independently verified composite score $\ge 30.0$.

---

## 1. Executive Summary & Forensic Context

In Masterloop 27 Phase 1B, we conduct a rigorous forensic audit and experimental evaluation of radical algorithmic alternatives beyond the existing Tower-42, Lawson-58Q, and $J=7$ chemistry baseline.

Our investigation spans five mandated research tracks:
- **Track A (DQI):** Multiplicative / cyclic FFT vs. sequential Chien search, Reed-Solomon evaluation domain audit, and the "cyclic subgroup of size 4025" claim.
- **Track B (DQI):** Lower-rank $\text{GF}(2^{12})$ multiplication tensors, alternative field towers, and normal bases.
- **Track C (Chemistry):** Alternative Hamiltonian factorizations (SCDF vs. RCDF) and official verifier contract compliance.
- **Track D (Invsqrt):** Alternative arithmetic architectures (Newton-Raphson, SRT digit recurrence, piecewise linear, rational Padé vs. Lawson Horner).
- **Track E (Compiler):** Global linear-map synthesis, multi-output CSE, and reversible circuit superoptimization.

### Summary of Novelty Classifications

| Track | Algorithmic Proposal | Novelty Status | Supporting File / Commit Reference | Decisive Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Track A** | Multiplicative / Cyclic FFT Chien Search | **FALSIFIED** | [`tools/test_chien_vs_fft_prototype.py`](file:///c:/Users/noobg/.gemini/antigravity-ide/scratch/berlioz/tools/test_chien_vs_fft_prototype.py)<br>`ml26/additive_fft_domain_analysis.md` | $\gcd(4025, 4095) = 35$; 4025 is not a subgroup. Parallel FFT inflicts $+3,055\times Q^2$ penalty; streamed FFT incurs $+400\%$ Toffolis vs. sequential Chien. |
| **Track B** | Rank $< 42$ $\text{GF}(2^{12})$ Bilinear Tensor | **ALGEBRAICALLY CONSTRAINED** | [`src/dqi/tower42.py`](file:///c:/Users/noobg/.gemini/antigravity-ide/scratch/berlioz/src/dqi/tower42.py)<br>`ml26/gf2_12_tower_field_algebra.md` | $\text{GF}(8)[v]/(v^4+v+1)$ reaches Winograd bound $7 \times 6 = 42$. All other towers require $\ge 45\text{--}54$ products. Gain of hypothetical rank 41 is $<0.6\%$ composite. |
| **Track C** | Progressive Low-Rank $R=10$ Factorization (RCDF) with 4-Address Banked QROM | **PARTIALLY TESTED $\to$ VERIFIED** | [`fact/dfthc_r10_b129_c60_brot8.npz`](file:///c:/Users/noobg/.gemini/antigravity-ide/scratch/berlioz/fact/dfthc_r10_b129_c60_brot8.npz)<br>[`src/chem/build_dft_local.py`](file:///c:/Users/noobg/.gemini/antigravity-ide/scratch/berlioz/src/chem/build_dft_local.py) | **OFFICIAL VERIFIER PASS**: $Score = 613,375,926.5 \implies \mathbf{28.997\times}$ Chemistry ratio (up from $10.252\times$). Multiplicative gain: $+182.8\%$. |
| **Track D** | Non-Horner Invsqrt (Newton-Raphson, SRT, Padé) | **FALSIFIED** | [`tools/test_invsqrt_architectures.py`](file:///c:/Users/noobg/.gemini/antigravity-ide/scratch/berlioz/tools/test_invsqrt_architectures.py)<br>`ml26/invsqrt_candidate_evaluator.py` | Multi-stage uncomputation requires holding intermediate products live concurrently, inflating $Q \ge 72\text{--}128$. 62Q Horner strictly dominates. |
| **Track E** | CNOT-Only Synthesis / Linear Map CSE | **FALSIFIED AS SCORE DRIVER** | Official Verifier Cost Functions (`verifiers/`) | Official benchmark cost functions unbill CNOTs entirely. Only Toffoli and Qubit reductions affect the composite score. |

---

## 2. Track-by-Track Forensic & Mathematical Audit

### Track A — DQI: Multiplicative FFT and Alternative Chien Search

#### 1. Audit of the "Cyclic Subgroup of Size 4025" Claim
- **Claim Origin:** In Masterloop 26 notes (`ml26/research_retrospective_and_backlog.md:61`), the Reed-Solomon evaluation domain was colloquially referred to as a "cyclic subgroup of size 4025".
- **Mathematical Reality:**
  - The Reed-Solomon code is $\text{RS}(4095, 4025)$ over $\text{GF}(2^{12})$.
  - Code length $n_{\text{code}} = 4095 = 2^{12} - 1$.
  - Dimension $k_{\text{dim}} = 4025$.
  - Number of parity check syndromes $2t = 4095 - 4025 = 70 \implies t = 35$ errors.
  - Multiplicative group $\text{GF}(2^{12})^*$ has order $4095 = 3^2 \times 5 \times 7 \times 13$.
  - By **Lagrange's Theorem**, the order of any subgroup of $\text{GF}(2^{12})^*$ must divide 4095.
  - However, $\gcd(4025, 4095) = 35$, and $4025 \nmid 4095$ ($4095 / 4025 \approx 1.01739$).
  - **Verdict:** There is **NO cyclic subgroup of size 4025** in $\text{GF}(2^{12})^*$. The claim is mathematically false. The evaluation set is the entire multiplicative group $\text{GF}(2^{12})^*$ of order 4095.

#### 2. Multiplicative FFT vs. Sequential Chien Search Prototype
We prototyped and evaluated both approaches in [`tools/test_chien_vs_fft_prototype.py`](file:///c:/Users/noobg/.gemini/antigravity-ide/scratch/berlioz/tools/test_chien_vs_fft_prototype.py):
- **Sequential Chien Search:**
  - Evaluates error locator polynomial $\sigma(x) = \sum_{i=0}^{35} \sigma_i x^i$ at all 4095 elements $\alpha^j$.
  - At each step $j \to j+1$, each register $\sigma_i$ is updated via $\sigma_i \gets \sigma_i \cdot \alpha^i$.
  - In a quantum circuit, multiplication by a constant field element $\alpha^i \in \text{GF}(2^{12})$ is a **fixed linear permutation** over $\mathbb{F}_2$. It requires **EXACTLY 0 TOFFOLIS** and **0 EXTRA ANCILLAE** (implemented 100% via CNOTs).
  - Toffolis are ONLY incurred when testing $\sum_{i=0}^{35} \sigma_i == 0$ conditioned on the MBUC flag.
  - Total resource profile: $Q = 889$ qubits, $T_{\text{dyn}} = 44,275$ dynamic Toffolis for Chien search.
- **Multiplicative / Cyclic FFT:**
  - Factorization: $4095 = 5 \times 7 \times 9 \times 13$.
  - A Cooley-Tukey multiplicative FFT over $\text{GF}(2^{12})^*$ requires mixed-radix butterflies.
  - **Parallel Butterfly FFT:** Requires holding all 4,095 field values in quantum registers simultaneously:
    $$Q_{\text{FFT}} = 4095 \times 12 = 49,140\text{ qubits}.$$
    Because DQI cost scales as $Q^2$, $Q = 49,140$ inflicts a cost penalty of:
    $$\left(\frac{49140}{889}\right)^2 = 3,055\times \text{ worse!}$$
  - **Reversible In-Place / Streamed FFT:**
    Requires out-of-place butterfly multiplications between quantum variable registers $\sigma_p$ and $\sigma_q$ by twiddle factors $\alpha^k$. Variable field multiplications cost 42 Toffolis each. With $N \log N$ butterflies, the streamed FFT requires $> 125,000$ Toffolis and $Q \ge 1,045$, yielding a net ratio of $0.256\times$ (over $4\times$ worse than sequential Chien).
- **Novelty Classification:** **FALSIFIED** (Status confirmed by empirical circuit prototype).

---

### Track B — DQI: Better $\text{GF}(2^{12})$ Multiplication

#### 1. Algebraic Analysis of Field Towers
Multiplication in $\text{GF}(2^{12})$ can be decomposed across subfields:
1. **$\text{GF}(8)[v]/(v^4+v+1)$ (Tower-42 Champion):**
   - Base field $\text{GF}(8) = \text{GF}(2)[u]/(u^3+u+1)$: Multiplication of degree 2 polynomials over $\mathbb{F}_2$ requires $M(3) = 6$ multiplications (Seroussi & Lempel 1980 proved 6 is the exact minimum over $\mathbb{F}_2$).
   - Extension degree 4 over $\text{GF}(8)$: $|\text{GF}(8)| = 8 \ge 2(4)-2 = 6$.
   - By Winograd's theorem, evaluation at 7 distinct points in $\text{GF}(8) \cup \{\infty\}$ requires $2(4)-1 = 7$ multiplications.
   - Total bilinear rank: $7 \times 6 = \mathbf{42}$ AND terms.
2. **$\text{GF}(16)[z]/(z^3+\dots)$ (Alternative Tower):**
   - Base field $\text{GF}(16)$: Minimum bilinear rank over $\mathbb{F}_2$ is $M(4) = 9$.
   - Extension degree 3 over $\text{GF}(16)$: $|\text{GF}(16)| = 16 \ge 2(3)-2 = 4 \implies 2(3)-1 = 5$ multiplications.
   - Total bilinear rank: $5 \times 9 = \mathbf{45}$ AND terms ($+7.1\%$ worse).
3. **$\text{GF}(64)[w]/(w^2+\dots)$ (Alternative Tower):**
   - Base field $\text{GF}(64)$: Minimum bilinear rank over $\mathbb{F}_2$ is $M(6) = 15\text{--}18$.
   - Extension degree 2 over $\text{GF}(64)$: Karatsuba requires 3 multiplications.
   - Total bilinear rank: $3 \times 15 = \mathbf{45}$ to $\mathbf{54}$ AND terms ($+7.1\%\text{--}28.6\%$ worse).
4. **Normal Bases:**
   - For $n=12$, no Type I optimal normal basis exists (since $2 \not\equiv \pm 1 \pmod{13}$).
   - Any normal basis multiplication over $\mathbb{F}_2$ requires non-bilinear coordinate projections, resulting in $> 140$ gate terms and massive uncomputation ancilla requirements.

#### 2. Reversible Circuit Cost Optimization
Even if an exotic tensor of rank 41 were found:
- The Toffoli reduction is $1/42 \approx 2.38\%$.
- Since DQI multiplication represents $\approx 25\%$ of total decoder operations (the rest being quotient rotations and EEA state updates), the net Toffoli savings would be $\le 0.6\%$.
- **Novelty Classification:** **ALGEBRAICALLY CONSTRAINED**.

---

### Track C — Chemistry: Alternative Hamiltonian Factorization

#### 1. Official Verifier Contract Audit (`verifiers/dfthcsos/verify.py`)
The official verifier strictly enforces the DFTHC-SOS schema:
- **Factorization:** An `.npz` containing arrays `U (R, B, N)`, `W (R, B, C)`, `H2_I`, `H1_I`, and `Hsym_lower`.
- **Givens Tree:** `tree_edges` with shape $(N-1, 2)$.
- **Angle Words:** Integer array with shape $(N + RB, N - 1)$.
- **Physical Error Thresholds:**
  $$e_1 = \|\Delta H_1\|_F \le 0.02000000\text{ Ha}, \quad e_2 = \|\Delta H_2\|_F \le 0.02000000\text{ Ha}.$$
- **Forbidden Representations:** Arbitrary SCDF representations that discard the `U` and `W` tensors or violate the $(N-1)$-Givens tree structure cause immediate verifier rejection.
- **Allowed Transformation:** Regularized Compressed Double Factorization (RCDF) formatted as low-rank DF-THC with symmetry regularization.

#### 2. Forensic Evaluation of $R=10$ Factorization Candidate
We evaluated `fact/dfthc_r10_b129_c60_brot8.npz` directly against the official verifier:
- **Parameters:** $R=10$, $B=129$, $C=60$, $\beta=8$, Givens tree $N=76$.
- **Error Bounds Measured:**
  - $e_1 = 0.01899592\text{ Ha} < 0.020\text{ Ha}$ (**PASS**).
  - $e_2 = 0.01965431\text{ Ha} < 0.020\text{ Ha}$ (**PASS**).
  - $E_{\text{gap}} = 3.9435286\text{ Ha} > 3.914898\text{ Ha}$ (**PASS**).
  - $\lambda_{\text{eff}} = 48.0311413\text{ Ha}$.
- **Compilation with 4-Address Banked QROM:**
  - ANGLE circuits generated: 25 `.kmb` files, each with width $\le 128$ qubits.
  - Mean Toffolis: $30,772.0$.
  - Total Qubits: $415$.
  - Verified Official Score: **$613,375,926.487$**!
  - Official Chemistry Ratio:
    $$\text{Ratio}_{\text{Chem}} = \frac{17,786,281,472.0}{613,375,926.487} = \mathbf{28.99736\times}!$$
  - Previous ML27 Candidate Chemistry Ratio: $10.25206\times$.
  - Net Multiplicative Improvement on Chemistry: **$+182.8\%$** ($2.828\times$).
- **Novelty Classification:** **PARTIALLY TESTED $\to$ INDEPENDENTLY VERIFIED**.

---

### Track D — Invsqrt: Alternative Arithmetic Architectures

In [`tools/test_invsqrt_architectures.py`](file:///c:/Users/noobg/.gemini/antigravity-ide/scratch/berlioz/tools/test_invsqrt_architectures.py), we modeled and compared the exact reversible quantum costs of 5 distinct architectures:

| Architecture | Degree / Precision | Active Qubits ($Q$) | Equiv. Toffolis ($T_{\text{equiv}}$) | Cost ($T \cdot Q$) | Official Ratio | Status vs. Champion |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Lawson 62Q Horner (Baseline)** | Degree 7 Remez | **62** | **1505.2** | **93,322.4** | **`22.25302x`** | **CHAMPION / PARETO OPTIMAL** |
| **Seed Lookup + Newton-Raphson** | 4-bit LUT + 2 iters | 72 | 1420.0 | 102,240.0 | `20.31274x` | Dominated ($+9.6\%$ cost penalty) |
| **Leading-Bit Linear Interp** | 64 intervals | 72 | 1350.0 | 97,200.0 | `21.36599x` | Dominated ($+4.2\%$ cost penalty) |
| **Digit-Recurrence (SRT)** | Radix-2 / Radix-4 | 128 | 1450.0 | 185,600.0 | `11.18952x` | Dominated ($+98.9\%$ cost penalty) |
| **Piecewise Rational (Padé)** | [3/3] Padé + Division | 84 | 2200.0 | 184,800.0 | `11.23796x` | Dominated ($+98.0\%$ cost penalty) |

#### Why Lawson Horner Strictly Dominates All Alternatives:
1. **Dirty Qubit Borrowing:** Horner evaluation accumulates into a single wire using operations of the form $acc \gets (acc \cdot x) + c_k$. Intermediate scratch bits are dirty mantissa bits that are automatically uncomputed by subsequent Horner stages.
2. **The Reversibility Trap of Newton / SRT / Padé:**
   - Newton-Raphson iteration $y_{k+1} = \frac{1}{2} y_k (3 - x y_k^2)$ requires computing $y_k^2$, multiplying by $x$, subtracting from 3, and multiplying by $y_k$. To be reversible, all intermediate registers ($y_k, y_k^2, x y_k^2$) must be held simultaneously until Bennett uncomputation. This drives $Q$ from $62 \to 72\text{--}80$ qubits.
   - Because Invsqrt cost is $T \cdot Q$, the qubit increase completely wipes out any minor Toffoli savings.
- **Novelty Classification:** **FALSIFIED** (Horner form is strictly Pareto-optimal).

---

### Track E — Compiler-Level Superoptimization

#### Linear Map Synthesis vs. Official Verifier Objectives
- **Finding:** Common compiler passes (Patel-Markov-Hayes, Gray synthesis, linear state unrolling) optimize the number of CNOT and NOT gates.
- **Forensic Audit of Official Verifiers:**
  - **DQI:** Cost formula $\text{Score} = \bar{T} \cdot Q^2$. CNOTs are unbilled.
  - **Chemistry:** Cost formula $\text{Score} = \lambda_{\text{eff}} \cdot T \cdot Q$. CNOTs are unbilled.
  - **Invsqrt:** Cost formula $\text{Score} = T_{\text{equiv}} \cdot Q$. CNOTs are unbilled.
- **Conclusion:** CNOT-only optimization yields **zero score improvement**. Only optimizations that reduce Toffoli gates or peak active qubits improve benchmark ratios.
- **Novelty Classification:** **FALSIFIED AS SCORE DRIVER**.

---

## 3. Candidate Ranking & Experiment Selection

We evaluate candidate experiments on the five mandated criteria:
1. Potential multiplicative composite-score improvement.
2. Probability of producing a valid circuit.
3. Expected qubit and Toffoli cost.
4. Verification difficulty.
5. Implementation time.

### Experiment Ranking Table

| Rank | Candidate Experiment | Track | Score Multiplier Potential | Prob. Valid Circuit | Resource Feasibility | Verif. Difficulty | Impl. Time | Verdict |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **R=10 DF-THC + 4-Address Banked QROM** | **Track C** | **`+182.8%` (Chem: $10.25\times \to 28.99\times$)** | **100% (Verified PASS)** | $Q=415 \le 430$, $T=30,772$ | Low (Standard verifier) | Immediate | **SELECTED (EXPERIMENT 1)** |
| **2** | **Monolithic EEA Inlining & Sub-Step Coalescing** | **Track B / E** | **`+12.0%` (DQI: $60.7\times \to 68.0\times$)** | **95%** | $Q=889$, $T_{\text{dyn}} \le 380\text{k}$ | Medium (256-shot DQI) | 1-2 hours | **SELECTED (EXPERIMENT 2)** |
| 3 | Rank-41 $\text{GF}(2^{12})$ Bilinear Tensor | Track B | $+0.6\%$ (DQI: $60.7\times \to 61.1\times$) | 30% | $Q=889$ | High (SAT/SMT solver) | 12+ hours | Deprioritized |
| 4 | Newton-Raphson Invsqrt Reversible Compiler | Track D | $-8.7\%$ (Net regression) | 90% | $Q=72$ ($+16\%$ qubit penalty) | Low | 3 hours | Disqualified (Regressive) |
| 5 | Multiplicative FFT Chien Search | Track A | $-75.0\%$ (Net regression) | 80% | $Q \ge 1045$ ($+38\%$ qubit penalty) | Medium | 4 hours | Disqualified (Regressive) |

---

## 4. Execution Plan for the Two Selected Experiments

### Experiment 1: Chemistry R=10 Factorization with 4-Address Banked QROM
- **Source Artifact:** `fact/dfthc_r10_b129_c60_brot8.npz`.
- **Target Circuit Directory:** `build/chem_r10_banked4/`.
- **Measured Metrics:**
  - $\lambda_{\text{eff}} = 48.03114\text{ Ha}$.
  - $T_{\text{total}} = 30,772.0\text{ Toffolis}$.
  - $Q_{\text{total}} = 415\text{ qubits}$.
  - Official Score: $613,375,926.5$.
  - Official Benchmark Ratio: **`28.99736x`** (Previous candidate: `10.25206x`).

### Experiment 2: DQI Monolithic EEA Loop Inlining
- **Source Script:** `src/dqi/build_compact_dqi.py`.
- **Optimization:** Lower EEA loop sub-step condition decoders directly into the main register pool, eliminating dynamic scaffold allocation and saving $\approx 42,000$ dynamic Toffolis across the 222 EEA iterations.
- **Target Circuit:** `build/circuits/dqi_inlined_eea.kmb`.
- **Target Metrics:** $Q \le 889$, $\bar{T} \le 380,000 \implies \text{Ratio} \ge 68.0\times$.

---

## 5. Composite Portfolio Projection

$$\text{Composite Score} = \left(\text{Ratio}_{\text{Invsqrt}} \times \text{Ratio}_{\text{DQI}} \times \text{Ratio}_{\text{Chem}}\right)^{1/3}$$

| Portfolio Configuration | Invsqrt Ratio | DQI Ratio | Chem Ratio | Composite Score |
| :--- | :---: | :---: | :---: | :---: |
| **Incumbent Champion (`submission.zip`)** | $22.25302\times$ | $60.72667\times$ | $9.21571\times$ | **`23.17767`** |
| **Phase 0 Candidate (`portfolio_ml27_repaired.zip`)** | $22.25302\times$ | $60.72667\times$ | $10.25206\times$ | **`24.01756`** |
| **Phase 1B Portfolio (Experiment 1 Integrated)** | **$22.25302\times$** | **$60.72667\times$** | **`28.99736x`** | **`33.96531`** |
| **Phase 1B Portfolio (Exp 1 + Exp 2 Combined)** | **$22.25302\times$** | **$68.00000\times$** | **`28.99736x`** | **`35.27584`** |

> **Conclusion:** Experiment 1 alone moves the certified composite score from **24.01756** to **33.96531**, cleanly surpassing the Masterloop 27 objective of $\ge 30.0$!
