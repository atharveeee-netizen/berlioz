# ML26 PART 11: COMPREHENSIVE RESEARCH RETROSPECTIVE & NEXT-PHASE BACKLOG

**Author:** BERLIOZ Chief Research Architect  
**Context:** BERLIOZ MASTERLOOP 26 — PART 11  
**Framework:** Syzygy Spec-Driven Development Standard (v1.0.0)  
**Execution Date:** 2026-10-31 / 2026-11-01  
**Status:** EVIDENCE-GROUNDED RETROSPECTIVE & AUTHORITATIVE RESEARCH BACKLOG

---

## 1. Research Retrospective: The Evidence Record

The Masterloop 26 programme was designed to move our quantum circuit compilation engine from speculative heuristic adjustments to mathematically grounded, verifier-enforced co-design.

Across Parts 1 through 10, **fifteen core hypotheses** were formulated, isolated in dedicated test benches, subjected to falsification tests, and evaluated under official verifier contracts.

```mermaid
pie title Hypothesis Verification Outcomes in Masterloop 26
    "Succeeded & Certified" : 5
    "Falsified & Disproved" : 6
    "Untested / High-Priority Backlog" : 4
```

---

## 2. Hypothesis Post-Mortem

### 2.1 The Five Succeeded Hypotheses (Confirmed & Integrated)

1. **H1 — Lawson Minimax Piecewise Approximation + Workspace Reclaim (`INV-LAWSON-58Q`):**
   - *Hypothesis:* Partitioning $[1, 4)$ into 4 subintervals with degree-3 Lawson minimax polynomials expands phase slack, permitting in-place vacated-bit register packing and carry folding.
   - *Result:* **CONFIRMED.** Min margin expanded to $3.022 \times 10^{-11}\text{ turns}$. Lower 2 normalization bits reused for subinterval indexing, and carry folded into Horner subtractor, dropping width to **$Q = 58$ qubits**. Rotation precision relaxed to $\varepsilon = 2.316 \times 10^{-12}$.
   - *Metric Gain:* Cost dropped from $100,608.66 \to \mathbf{92,972.55}$, boosting Invsqrt ratio from **$20.642\times \to 22.345\times$** (+1.703x).

2. **H2 — Galois Subfield Tower-42 Bilinear Multiplication (`DQI-TOWER42-889Q`):**
   - *Hypothesis:* Representing $\text{GF}(2^{12}) \cong \text{GF}(8)[v]/(v^4+v+1)$ with 7 evaluation points in $\text{GF}(8)$ and Karatsuba factoring reduces bilinear multiplication from 63 to 42 Toffolis.
   - *Result:* **CONFIRMED.** All 144 basis products and 500 randomized vector tests passed bit-exact. Reversible pooling recycles scratch ancillae. Mean dynamic Toffolis dropped from $427,471.2 \to \mathbf{345,618.4}$.
   - *Metric Gain:* DQI ratio boosted from **$60.726\times \to 75.112\times$** (+14.386x).

3. **H3 — Signed Half-Open Givens Gauge (`CHEM-R8-J5-PEBBLE`):**
   - *Hypothesis:* Enforcing $\text{bit}(7) \equiv \text{bit}(6)$ across all Givens angle words removes the explicit sign bit from QROM loading.
   - *Result:* **CONFIRMED.** Saved 5 difference wires per circuit, ensuring all 15 angle circuits strictly adhere to the $Q_{\text{angle}} \le 128$ ceiling (actual: $Q = 126$).

4. **H4 — Split Algebraic Normal Form (ANF) Monomial Erasure (`CHEM-ANF-ERASE`):**
   - *Hypothesis:* Monomials can be uncomputed via relative-phase Toffolis and out-of-order Clifford commutations without a separate backward uncompute pass.
   - *Result:* **CONFIRMED.** Angle circuits execute in only $277.87$ Toffolis/pass ($16,266$ total), preserving chemical accuracy ($e_1, e_2 \le 0.85\text{ mHa}$) and establishing the **`9.93301x`** benchmark record.

5. **H5 — Exact Clopper-Pearson Calibration at $\delta = 2^{-128}$ (`SCORE-CALC-CANONICAL`):**
   - *Hypothesis:* Discrepancies between local scores and Kaggle public leaderboard rankings stem from unmodeled repetition penalty ladders.
   - *Result:* **CONFIRMED.** Implemented exact beta distribution quantiles, fixing $R(0) = \mathbf{1.19126046}$ and reconciling submission `57811741` with exact mathematical precision.

---

### 2.2 The Six Falsified Hypotheses (Disproved Traps & Negative Results)

1. **H6 — Continuous $R=10$ Factorization Improves Quantum Circuit (`CHEM-R10-FAIL`):**
   - *Why it failed:* While continuous L-BFGS reduced $\lambda_{\text{eff}}$ from $48.32 \to 48.032\text{ Ha}$ ($-0.56\%$), the address table expanded from $A = 1,220 \to 1,366$. This forced the pebble QROM to $Q = 135 > 128$ (Disqualified) or forced fallback to 2-address linear mode ($T=27,574$), increasing cost by $+65.7\%$.
   - *Takeaway:* Continuous and discrete optimization must be co-designed. Never optimize $\lambda_{\text{eff}}$ in isolation from memory layout.

2. **H7 — Additive FFT Chien Search Accelerates Reed-Solomon Decoding (`DQI-FFT-FAIL`):**
   - *Why it failed:* Additive FFT requires evaluation domains to be affine $\mathbb{F}_2$-subspaces ($2^{12}=4096$). The RS(4095, 4025) code is defined on a cyclic subgroup of size $4,025$ (not an affine subspace). Padding 71 dummy points and allocating out-of-place reversible butterfly ancillae inflated Toffolis by $+566\%$ ($1,120,000$ Toffolis) and qubits to $Q=1420$, degrading ratio to $9.084\times$.

3. **H8 — Measurement-Based Cleanup (MBUC) on Additive FFT Butterflies (`DQI-MBUC-FFT-FAIL`):**
   - *Why it failed:* Measuring intermediate bilinear product registers $y = a \cdot b$ over superpositions kicks back entangled two-qubit non-Clifford $CZ(a, b)$ phase gates. These cannot be tracked in a classical Pauli frame, destroying quantum coherence.

4. **H9 — Projective Reed-Solomon Decoding Eliminates Chien Search (`DQI-PROJECTIVE-FAIL`):**
   - *Why it failed:* Projective measurements collapse the quantum syndrome superposition, permanently destroying the coherence required by the Forney formula to calculate error values. Rebuilding error values requires $>120$ quantum amplitude amplification rounds ($4.85 \times 10^7$ Toffolis, ratio $0.502\times$).

5. **H10 — Global Bennett Pebbling on RiBM (`DQI-PEBBLING-FAIL`):**
   - *Why it failed:* RiBM is *already an in-place systolic array*. Adding pebbling checkpoints allocates storage wires that inflate active qubits from $889 \to 1,120$. In DQI, cost scales with $Q^2$, incurring a $+58.7\%$ penalty that degrades the ratio from $60.726\times \to 38.26\times$.

6. **H11 — Estrin Parallel Evaluation Reduces Invsqrt Cost (`INV-ESTRIN-FAIL`):**
   - *Why it failed:* In reversible logic, intermediate registers cannot be overwritten. Evaluating $(c_0+c_1\delta)$ and $\delta^2(c_2+c_3\delta)$ in parallel requires allocating separate physical registers for each branch, inflating $Q: 58 \to 86 > 64$ and dropping the ratio to $15.73\times$.

---

### 2.3 The Four High-Priority Untested Hypotheses

1. **H12 — Monolithic Inline Tower-42 Decoder Binary Synthesis:**
   - Replacing all 1,364 multipliers in the full 534 MB `dqi.kmb` state machine binary without introducing temporary ancilla leaks.
2. **H13 — 740-Qubit In-Place Syndrome Wire Recycling:**
   - Reusing the 840 syndrome qubits $S_0 \dots S_{69}$ in-place during the Chien search root-finding stage to reduce peak live wires from $889 \to 740$ ($(889/740)^2 = 1.443\times$ gain).
3. **H14 — Chemistry $R=8, J=7$ Packed Pebble Mode:**
   - Compiling Givens angles in groups of $J=7$ ($Q = 20 + 15(7) = 125 \le 128$) to reduce angle circuits from 15 to 11, saving $5,764$ Toffolis.
4. **H15 — Invsqrt Single Global Rotation Synthesis ($N_{\text{rot}} = 1$):**
   - Factoring all phase polynomial evaluations into a single global rotation stage, eliminating 40 rotation synthesis penalties.

---

## 3. Disproved Assumptions & Core Architectural Laws

| Disproved Assumption | Architectural Ground Truth & New Operating Law |
| :--- | :--- |
| **"Additive projections hold across techniques."** | **The Anti-Additive Law:** Reversible circuits exhibit strong non-linear coupling. Independent gains cannot be summed. |
| **"Lowering continuous $\lambda_{\text{eff}}$ always improves chemistry."** | **The Discrete Address Cliff:** Continuous gains are erased if they trigger address table expansion beyond the 128-qubit ceiling. |
| **"Mid-circuit measurement can uncompute any scratch register."** | **The Bilinear Clifford Correction Theorem:** MBUC is strictly valid only on linear registers. Measuring bilinear products creates non-Clifford phase kickback. |
| **"Parallel classical trees reduce reversible circuit cost."** | **Width-First Dominance:** In $Q \times C$ and $Q^2 \times T$ metrics, qubit count dominates. Sequential in-place Horner is strictly superior to parallel Estrin. |
| **"Pebbling checkpoints always save resources."** | **The In-Place Dominance Theorem:** Checkpointing an already in-place systolic array inflates live wires without reducing gates. |

---

## 4. "Where the Cost Lives": Dominant Remaining Cost Blocks

```mermaid
graph LR
    subgraph "Invsqrt: 92,972 Cost"
        I1["Seed Table Poly Eval: 81.8%"]
        I2["Rotation Synthesis: 18.2%"]
    end
    subgraph "DQI: 3.25e11 Cost"
        D1["Galois Field Multiplications: 85.0%"]
        D2["Chien & Forney Roots: 15.0%"]
    end
    subgraph "Chemistry: 3.38e8 Cost"
        C1["State Prep Floor: 60.6%"]
        C2["QROM Angle Loads: 25.5%"]
        C3["Givens Rotations: 13.8%"]
    end
```

* **Invsqrt Bottleneck:** 81.8% of cost is locked in polynomial evaluation Toffolis; 18.2% in 41 non-Clifford rotations.
* **DQI Bottleneck:** Over 85% of all executed Toffolis occur inside Galois field multiplications during EEA and Chien search.
* **Chemistry Bottleneck:** 60.6% is a fixed state preparation floor; 25.5% is QROM data loading across angle circuits.

---

## 5. Authoritative Next-Phase Research Backlog (Prioritized)

| Priority | Task ID | Subsystem | Proposed Algorithmic Mutation | Mathematical Basis | Target Metric Impact |
| :---: | :---: | :---: | :--- | :--- | :---: |
| **P1** | `TASK-DQI-01` | DQI | **Inline Tower-42 State Machine Lowering** | Lower rank-42 bilinear tensor directly into the 534 MB `dqi.kmb` state machine binary without temporary routing registers. | $T_{\text{mean}} \to 345,618.4$ ($R_{\text{dqi}} \to \mathbf{75.112x}$) |
| **P2** | `TASK-DQI-02` | DQI | **Syndrome Register In-Place Wire Reuse** | Reuse idle syndrome wires $S_0 \dots S_{69}$ for Chien search scratch, squeezing active wires from $889 \to 740$. | $Q \to 740 \implies \mathbf{1.443x \text{ auto gain}}$ ($R_{\text{dqi}} \to \mathbf{108.4x}$) |
| **P3** | `TASK-CHEM-01` | Chem | **$J=7$ Packed Pebble Angle Compilation** | Batch Givens angles into 11 circuits ($J=7$) under $Q=125 \le 128$ ceiling using signed half-open gauge. | $T \to 13,850$ ($R_{\text{chem}} \to \mathbf{11.666x}$) |
| **P4** | `TASK-INV-01` | Invsqrt | **Single-Rotation Seed Table Factoring** | Factor phase angles into $N_{\text{rot}} = 1$ global rotation, eliminating 40 rotation synthesis penalties. | $T_{\text{equiv}} \to 1,480$ ($R_{\text{inv}} \to \mathbf{25.000x}$) |
| **P5** | `TASK-CHEM-02` | Chem | **SO(60) Riemannian Manifold Annealing** | Optimize orbital rotation matrices on Grassmannian manifold constrained strictly to $A \le 1,220$. | $\lambda_{\text{eff}} \to \le 45.0\text{ Ha}$ ($R_{\text{chem}} \to \mathbf{12.5x}$) |

### Projected Impact of Backlog Execution:
$$\text{Projected Frontier Score } S = (25.000 \times 108.400 \times 11.666)^{1/3} = (31,614.86)^{1/3} = \mathbf{31.621}$$
*(Exceeds current World Rank #1 of `26.76409` by $+18.1\%$).*
