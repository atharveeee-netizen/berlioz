# TURINGIRL QUANTUM: COMPREHENSIVE ARCHITECTURAL HANDOVER
**Google Quantum AI — Verifiable Quantum Circuit Compilation (Kaggle)**  
**Grand Objective**: **Targeting Score 50.0** (Improvement Product $= 50^3 = \mathbf{125{,}000}$)  
**Active Team**: `TuringIRL(akshit)`  
**Current Live Verified Score**: `22.99562` (Submission ID: `57800637`, Graded on 2026-10-30)  
**Historical Baseline**: `21.87976` (Oct 27)

---

## 1. Executive Summary & Problem Scope

This repository houses the complete **TuringIRL Quantum** compilation pipeline, mathematical formulations, scraped competitor intelligence, and verification harnesses for Google Quantum AI's competition on verifiable fault-tolerant quantum circuit synthesis.

Our mission transcends incremental leaderboard ranking: **our North Star is capturing a composite Geometric Mean Score of 50.0**.

### The Score 50 Mathematics
$$\text{Score} = \left(\text{Ratio}_{\text{invsqrt}} \times \text{Ratio}_{\text{dqi}} \times \text{Ratio}_{\text{dfthcsos}}\right)^{1/3} = \mathbf{50.0}$$
$$\implies \text{Product} = \text{Ratio}_{\text{invsqrt}} \times \text{Ratio}_{\text{dqi}} \times \text{Ratio}_{\text{dfthcsos}} = 50^3 = \mathbf{125{,}000}$$

* **Target Invsqrt Ratio**: **$25.0\times$** (56-Qubit NR Seed Table)
* **Target DQI Ratio**: **$200.0\times$** (42-Product Karatsuba Bilinear Multiplier + Global Wire Compaction $Q \to 520$)
* **Target Chemistry Ratio**: **$25.0\times$** ($R=7$ Factorization $\lambda_{\text{eff}} \le 42$ + 8-Address ANF QROM)

$$\text{Projected GM} = (25.0 \times 200.0 \times 25.0)^{1/3} = (125{,}000)^{1/3} = \mathbf{50.0}$$

---

## 2. Competition Metrics & Cost Formulations

The competition grades compiled circuits across three benchmarks evaluated by the official C++ simulator `kickmix`. The overall score is the geometric mean of three improvement ratios relative to Google's baseline references:

$$\text{Ratio}_i = \frac{\text{RefCost}_i}{\text{SubmittedCost}_i}$$

### Fixed Baseline Reference Costs
* $\text{Ref}_{\text{invsqrt}} = \mathbf{2{,}076{,}774.2337}$
* $\text{Ref}_{\text{dqi}} = \mathbf{24{,}439{,}463{,}583{,}672.93}$
* $\text{Ref}_{\text{dfthcsos}} = \mathbf{3{,}355{,}599{,}588.3155}$

---

### Task Specifications

#### 1. `invsqrt` (Fixed-Point Inverse Square Root)
* **Goal**: Reversible calculation of $1/\sqrt{x}$ using Newton-Raphson iterations over 22-bit fixed-point arithmetic across $x \in [1, 3{,}133{,}452]$.
* **Cost Function**: $\text{Cost} = Q \times C = Q \times (\text{Toffolis} + T / 4)$, where Toffolis is mean CCX/CCZ per shot, $T$ is rotation synthesis cost ($0.56 \log_2(1/\epsilon) + 5.3$ T-gates per Z_POW rotation), and $Q$ is active qubits.
* **Current State**: 62-Qubit implementation ($1{,}332.48$ mean Toffolis + $41$ rotations synthesizing to $1{,}186.36$ T-gates $\implies 1{,}629.07$ Toffoli-equivalents). Cost: $62 \times 1{,}629.07 = 101{,}002.48 \implies \mathbf{20.561\times}$ improvement. Verified across 200,540,928 shots with worst-case relative error $0.99932 \times \text{tol}$.

#### 2. `dqi` (Decoded Quantum Interferometry RS Decoder)
* **Goal**: Syndrome decoding of an $\text{RS}(4095, 4025)$ code in $\text{GF}(2^{12})$ across **102,400 verification shots**.
* **Cost Function**: $\text{Cost} = R(\epsilon^+) \times Q^2 \times T_{\text{mean}}$.
  * $R(\epsilon^+)$: Clopper-Pearson confidence penalty on error rate $\epsilon^+$ at $\delta = 2^{-128}$ across 102,400 shots. Zero errors yields $R \approx 1.191$.
  * $Q$: Peak active qubits.
  * $T_{\text{mean}}$: Mean Toffoli count per syndrome measurement shot.
* **Baseline**: 889-qubit decoder using standard 63-AND polynomial multiplication. Cost: $4.1026 \times 10^{11} \implies \mathbf{59.57\times}$ improvement.
* **Verified Arithmetic Lever**: The 42-Product Bilinear Tensor (`src/dqi/tower42.py`) drops Toffolis by **21.18%**, boosting the ratio to **$75.57\times$**. Combining this with prospective wire compaction ($Q \to 520$) forms our long-term research horizon towards **$200.0\times$**.

#### 3. `dfthcsos` (Double-Factorized THC Chemistry Simulation)
* **Goal**: Low-energy simulation of FeMoCo active nitrogenase catalytic site (76 orbitals, 113 electrons) from a 128 MB FCIDUMP.
* **Cost Function**: $\text{Cost} = \lambda_{\text{eff}} \times Q_{\text{total}} \times T_{\text{chem}}$.
  * Constraints: $e_1 \le 20.0\text{ mHa}$, $e_2 \le 20.0\text{ mHa}$, $E_{\text{gap}} \in [3.8, 4.0]\text{ Ha}$, $Q_{\text{angle}} \le 126$.
* **Live Champion**: The live submission (`submission_2299.zip`) uses an $R=8, B=143, C=60$ factor matrix with 15 angle circuits generated via 4-address pebble QROM, totaling only 4,168 1-pass Toffolis (8,336 2-pass), $\lambda_{\text{eff}} = 48.32$, achieving **$9.928\times$** improvement (Score: 337.99M).
* **Masterloop 11 Finding**: The $R=10, B=129, C=60$ factor matrix with $J=7$ achieves **$5.993\times$** (Score: 559.89M, saving 5,764 Toffolis over $J=5$). Although $R=10$ has a slightly lower continuous $\lambda_{\text{eff}} = 48.03$, its expanded address table forces 2-address mode, proving that continuous and discrete optimization must be co-designed. Table-native basis permutation and sign gauge optimization delivers a 12.11% reduction in QROM Hamming distance with zero chemical drift.

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

## 4. Repository Structure & Scraped Top Solutions

* `top_solutions/`: Contains 22 scraped solution notebooks from all top competitors (`avazaku`, `michaelrustad`, `somejoint`, `yoyobar`, `ahmedberatozer`, `busyaprime`, `dmitriyab`, `sigmaborov`). See `top_solutions/README.md`.
* `RESEARCH_VAULT_AND_LITERATURE.md`: Exhaustive academic documentation covering all cited papers (arXiv:2610.23832, arXiv:2510.10967, PRX Quantum 2, 030305, etc.).
* `src/chem/`: Complete DF-THC chemistry optimization suite (L-BFGS, progressive quantization, Givens gauge, banked QROM).
* `src/dqi/tower42.py`: The exact 42-product bilinear tensor discovering module and Kickmix builder adapter.
* `src/build_portfolio.py`: Master synthesis and packaging script.
* `fact/dfthc_r10_b129_c60_brot8.npz`: Verified $R=10$ factorization matrix ($\lambda_{\text{eff}} = 48.0311$).
* `verifiers/`: Official Google verification suites.
* `HANDOVER.md`: This comprehensive AI-readable guide.
* `README.md`: High-level presentation and quickstart guide.

---

## 5. Guidance for Incoming AI Collaborators

1. **DQI Compaction to $Q \le 520$**:
   Because DQI cost scales quadratically ($Q^2$), reducing peak live qubits from 889 to 520 yields a **$2.92\times$ cost reduction** independently of gate count. Formulate a global linear-scan interval coloring pass over temporary ancilla allocations.
2. **Recompilation with `TowerBuilder`**:
   Wrap the syndrome evaluation and Berlekamp-Massey control loop in `TowerBuilder` (`src/dqi/tower42.py`) to emit the 42-product `dqi.kmb`.
3. **Chemistry $R=7$ Compression**:
   Run `src/chem/cont_lbfgs.py` and `src/chem/pq.py` on the $(13, 129, 60)$ merged group matrix to prune from 10 down to 7 groups while remaining strictly within the 20 mHa error cap.
