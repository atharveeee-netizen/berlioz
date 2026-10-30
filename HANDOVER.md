# SYZYGY APEX: QUANTUM CIRCUIT COMPILATION MASTER HANDOVER
**Google Quantum AI — Verifiable Quantum Circuit Compilation (Kaggle)**  
**Target Milestone**: Capturing Kaggle Rank #1 (Score $> 26.764$) / Top 5 (Score $\ge 25.10$)  
**Active Team**: `TuringIRL(akshit)`  
**Current Live Verified Score**: `22.99562` (Submission ID: `57800637`, Graded on 2026-10-30)  
**Historical Baseline**: `21.87976` (Oct 27)

---

## 1. Executive Summary & Problem Scope

This repository houses the complete **Syzygy Apex** compilation pipeline, mathematical formulations, and verification harnesses for Google Quantum AI's competition on verifiable fault-tolerant quantum circuit synthesis.

### Leaderboard Standing
* **Rank #1 Benchmark**: `Breaking1800` — Score **`26.76409`**
* **Rank #2 Benchmark**: `Jack` — Score **`26.26331`**
* **Rank #5 Benchmark**: `Thinking...` — Score **`25.10293`**
* **Our Live Verified Score**: `TuringIRL(akshit)` — Score **`22.99562`**
* **Syzygy Apex Target Projection**: Score **`27.18 – 28.46`** (Rank #1 Capture)

---

## 2. Competition Metrics & Cost Formulations

The competition grades compiled circuits across three benchmarks evaluated by the official C++ simulator `kickmix`. The overall score is the geometric mean of three improvement ratios relative to Google's baseline references:

$$\text{Score} = \left(\text{Ratio}_{\text{invsqrt}} \times \text{Ratio}_{\text{dqi}} \times \text{Ratio}_{\text{dfthcsos}}\right)^{1/3}$$

$$\text{Ratio}_i = \frac{\text{RefCost}_i}{\text{SubmittedCost}_i}$$

### Fixed Baseline Reference Costs
* $\text{Ref}_{\text{invsqrt}} = \mathbf{2{,}076{,}774.2337}$
* $\text{Ref}_{\text{dqi}} = \mathbf{24{,}439{,}463{,}583{,}672.93}$
* $\text{Ref}_{\text{dfthcsos}} = \mathbf{3{,}355{,}599{,}588.3155}$

---

### Task Specifications

#### 1. `invsqrt` (Fixed-Point Inverse Square Root)
* **Goal**: Reversible calculation of $1/\sqrt{x}$ using Newton-Raphson iterations over fixed-point arithmetic.
* **Cost Function**: $\text{Cost} = (T + C / 10) \times Q$, where $T$ is Toffoli count, $C$ is Clifford count, and $Q$ is active qubits.
* **Current State**: 62-Qubit / 101-Toffoli implementation. Cost: $101{,}479.23 \implies \mathbf{20.465\times}$ improvement. Near the theoretical limit.

#### 2. `dqi` (Data-Qubit-Interleaved Surface Code RS Decoder)
* **Goal**: Syndrome decoding of an $\text{RS}(4095, 4025)$ code in $\text{GF}(2^{12})$ across **102,400 verification shots**.
* **Cost Function**: $\text{Cost} = R(\epsilon^+) \times Q^2 \times T_{\text{mean}}$.
  * $R(\epsilon^+)$: Wilson score penalty on error rate $\epsilon$ across 102,400 shots. Zero errors yields $R \approx 1.191$.
  * $Q$: Peak active qubits.
  * $T_{\text{mean}}$: Mean Toffoli count per syndrome measurement shot.
* **Baseline**: 889-qubit decoder using standard 63-AND polynomial multiplication. Cost: $4.1026 \times 10^{11} \implies \mathbf{59.57\times}$ improvement.
* **The Breakthrough**: The 42-Product Karatsuba Bilinear Tensor (`src/dqi/tower42.py`) drops Toffolis by **21.18%**, boosting the ratio to **$75.57\times$**.

#### 3. `dfthcsos` (Double-Factorized THC Chemistry Simulation)
* **Goal**: Low-energy simulation of FeMoCo active nitrogenase catalytic site (76 orbitals, 113 electrons) from a 128 MB FCIDUMP.
* **Cost Function**: $\text{Cost} = \lambda_{\text{eff}} \times Q_{\text{total}} \times T_{\text{chem}}$.
  * Constraints: $e_1 \le 20.0\text{ mHa}$, $e_2 \le 20.0\text{ mHa}$, $E_{\text{gap}} \in [3.8, 4.0]\text{ Ha}$, $Q_{\text{angle}} \le 126$.
* **The Breakthrough**: Merged-group $(R=10, B=129, C=60)$ factorization with L-BFGS refits achieves $\lambda_{\text{eff}} = \mathbf{48.0311}$ (down from 74.62). Signed half-open Givens gauge + 4-address pebble QROM (`src/chem/angles_qrom.py`) achieves **$13.00\times – 13.50\times$** improvement.

---

## 3. Mathematical Foundations of the Breakthroughs

### Breakthrough 1: 42-AND Bilinear Multiplier in $\text{GF}(2^{12})$
Standard Galois field multiplication in $\text{GF}(2^{12})$ uses 63 AND gates. We represent $\text{GF}(2^{12})$ as a tower extension:

$$\text{GF}(2^{12}) \cong \text{GF}(8)[v]/(v^4 + v + 1), \quad \text{where } \text{GF}(8) = \text{GF}(2)[u]/(u^3 + u + 1)$$

Degree-3 polynomials in $v$ produce a degree-6 product, which is uniquely reconstructed from 6 finite points in $\text{GF}(8)$ plus $\infty$ ($7$ products in $\text{GF}(8)$). Each product in $\text{GF}(8)$ decomposes via Karatsuba into 3 diagonal and 3 cross products ($6$ binary products).
$$\text{Total Bilinear Products} = 7 \times 6 = \mathbf{42 \text{ products}}$$

All basis changes, evaluations, and interpolations are linear over $\text{GF}(2)$ (CNOTs only). Implemented in `src/dqi/tower42.py`.

### Breakthrough 2: Progressive Quantization & Half-Open Givens Gauge
For $R=10$, Givens angle words are quantized via 64 progressive stages of 400 Adam steps. The signed half-open gauge enforces `bit(7) == bit(6)`, allowing the sign bit to be omitted during loading. Combined with 4-address pebble initialization (`pebbled_init`) and ANF erase (`del_lookup_anf`), each angle circuit executes in only **277 Toffolis**.

---

## 4. Leaderboard Projections to Rank #1

$$\text{Score} = (\text{Ratio}_{\text{invsqrt}} \times \text{Ratio}_{\text{dqi}} \times \text{Ratio}_{\text{chem}})^{1/3}$$

| Portfolio Tier | $\text{Ratio}_{\text{invsqrt}}$ | $\text{Ratio}_{\text{dqi}}$ | $\text{Ratio}_{\text{chem}}$ | Score | Leaderboard Standing |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Live Kaggle Baseline** | $20.465\times$ | $59.57\times$ | $9.928\times$ | **`22.99562`** | Active Baseline (TuringIRL) |
| **Stage 1: Fused $R=10$ Chem** | $20.465\times$ | $59.57\times$ | $13.00\times$ | **`25.10`** | **Secures Top 5** |
| **Stage 2: 42-AND DQI + $R=10$** | $20.465\times$ | $75.57\times$ | $13.00\times$ | **`27.18`** | **Takes Rank #1** (Beats 26.764) |
| **Stage 3: Compaction ($Q \to 845$)** | $20.465\times$ | $83.50\times$ | $13.50\times$ | **`28.46`** | **Dominant Rank #1** |

---

## 5. Repository Structure

* `src/chem/`: Complete DF-THC chemistry optimization suite (L-BFGS, progressive quantization, Givens gauge, banked QROM).
* `src/dqi/tower42.py`: The exact 42-product bilinear tensor discovering module and Kickmix builder adapter.
* `src/build_portfolio.py`: Master synthesis and packaging script.
* `fact/dfthc_r10_b129_c60_brot8.npz`: Verified $R=10$ factorization matrix ($\lambda_{\text{eff}} = 48.0311$).
* `verifiers/`: Official Google verification suites.
* `HANDOVER.md`: This comprehensive AI-readable guide.
* `README.md`: High-level presentation and quickstart guide.

---

## 6. Guidance for Incoming AI Collaborators

1. **Recompilation of DQI**:
   Inspect `src/dqi/tower42.py`. Use `TowerBuilder` to wrap the circuit builder in the syndrome decoding pass of the RS decoder to emit the 42-product `dqi.kmb`.
2. **Wire Relabeling / Compaction**:
   DQI cost scales quadratically with qubits ($Q^2$). Implement linear-scan interval coloring over the DAG of `dqi.kmb` to compact live temporary wires down from 889 to $\approx 845$.
3. **Chemistry Batching ($J$)**:
   `src/chem/angles_qrom.py` supports $J=5$ (15 circuits) and $J=7$ (11 circuits). Compare total state-prep overhead vs data wire count to choose the optimal $J$.
