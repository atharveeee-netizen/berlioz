# Masterloop 32: Beyond-30 Architecture Discovery Blueprint

## 1. Executive Charter & Mathematical Target

The composite competition score is defined as the geometric mean:
$$S = \left(R_{\text{inv}} \cdot R_{\text{dqi}} \cdot R_{\text{chem}}\right)^{1/3}$$

To achieve a verified score **$S \ge 30.00$**, the product of the three benchmark ratios must satisfy:
$$\Pi = R_{\text{inv}} \cdot R_{\text{dqi}} \cdot R_{\text{chem}} \ge 30^3 = \mathbf{27,000}$$

### Current Portfolio State vs. Beyond-30 Target:

| Benchmark | Current Verified (`ML31 Breakthrough`) | Beyond-30 Target | Required Multiplier | Primary Architectural Lever |
| :--- | :---: | :---: | :---: | :--- |
| **Chemistry** | **$10.260\times$** | **$14.000\times$** | $+36.5\%$ | $(R=8, C=34)$ rank compression + Banked QROM ($J=7$) |
| **DQI Decoder** | **$67.020\times$** | **$88.000\times$** | $+31.3\%$ | 852Q Zero-Scratch quotient fold + Mastrovito GF($2^{12}$) scan |
| **Invsqrt** | **$20.654\times$** | **$25.500\times$** | $+23.5\%$ | 59Q Overlapped Horner + WS9 precision margin harvesting |
| **Product $\Pi$** | **$14,201.2$** | **$30,464.0$** | **$+114.5\%$** | **Co-design across all 3 components** |
| **Composite $S$** | **`24.217`** | **`31.23`** | **$+7.01$ pts** | **Shatters the 30.00 competition barrier** |

---

## 2. Research Organization: Two Parallel Tracks with Four Gates

We allocate resources in a deliberate **60 / 40** split:
- **Track A — Architecture Discovery (60%):** Formulating, prototyping, and proving fundamentally new mathematical representations and algorithms.
- **Track B — Existing Architecture Headroom (40%):** Capturing guaranteed incremental gains (e.g. gauge sweeps, Horner coefficient pruning, register overlapping).

### The Four Compulsory Decision Gates:
Every proposed innovation must pass all four gates sequentially before expensive circuit compilation:
```
[Gate 1: Mathematical Feasibility]
   Is the representation provably compliant with the official verifier schema and error bounds?
                 │
                 ▼
[Gate 2: Resource Potential Model]
   Does an analytical cost calculation show at least a +15% improvement in the complete benchmark cost?
                 │
                 ▼
[Gate 3: Prototype Verification]
   Does a reduced-scale numerical prototype (e.g., N=16 orbitals or small shot batch) confirm convergence?
                 │
                 ▼
[Gate 4: Full Circuit Compilation & Verification]
   Official verifier execution, generating signed receipts, exact gate counts, and Kaggle validation.
```

---

## 3. Component Deep Dive: Architectural Search Space

### A. Chemistry ($10.26\times \to 14.00\times$) — Highest Research Leverage
Chemistry has the lowest baseline ratio ($10.26\times$), making it the highest-leverage component in the geometric mean.

1. **The Representation Bottleneck:**
   The official verifier enforces:
   - Factorization: $U \in \mathbb{R}^{R \times B \times N}$ decoded through a tree of $N-1 = 75$ Givens rotations, with $W \in \mathbb{R}^{R \times B \times C}$ and $H_{2, I} \in \mathbb{R}^{R \times C}$.
   - Accuracy: $e_1, e_2 \le 20.00\text{ mHa}$, $E_{\text{gap}} \ge 3.914898\text{ Ha}$, $\Lambda > 49.0$.
   - Cost: $\text{Cost} = \lambda_{\text{eff}}^2 \cdot \overline{T} \cdot Q^2$.
2. **Architectural Opportunities:**
   - **Rank-8 / Compressed Basis $(R=8, B=143, C=34)$:**
     The outer and inner state-preparation Toffolis scale directly with $RC$:
     $$RC = 9 \times 40 = 360 \longrightarrow RC = 8 \times 34 = 272 \quad (-24.4\% \text{ reduction})$$
     This cuts inner state-preparation Toffolis from $4,171 \to 3,150$.
   - **Banked QROM Scheduling ($J=7$ with 8-bit Word Packing):**
     Angle circuits currently consume 9,496 Toffolis ($58.5\%$ of total chemistry Toffolis!).
     By banking addresses into 7-bit blocks and interleaving control words, angle circuit Toffolis drop to $\approx 6,600$.
   - **Combined Impact:** Total Toffolis fall from $16,237 \to 11,400$ with $Q=418$ and $\lambda_{\text{eff}} = 47.0$, raising the ratio from $10.26\times \to \mathbf{14.15\times}$!

---

### B. Invsqrt ($20.65\times \to 25.50\times$) — Precision vs Reversibility
1. **The Reversibility Trap of Non-Polynomial Algorithms:**
   - Multi-stage methods (Newton-Raphson $y_{k+1} = \frac{1}{2}y_k(3 - xy_k^2)$, Goldschmidt, Padé rational) require holding multiple intermediate product registers live simultaneously ($y_k, y_k^2, xy_k^2$) to preserve reversibility until Bennett uncomputation.
   - This blows up active width $Q$ from $62 \to 72\text{--}128$ qubits, which completely negates their Toffoli efficiency under the $Q \cdot T$ metric.
2. **The Winning Mathematical Architecture:**
   - **In-Place Horner Accumulation:** Horner form evaluates $P(x) = c_0 + x(c_1 + x(\dots))$ using a single in-place accumulator, using dirty mantissa bits as temporary scratch that are automatically uncomputed by downstream stages.
   - **WS9 Precision Margin Harvesting:**
     Our 62Q Horner core has a worst-case error ratio of $\max_x |e(x)| / \text{tol}(x) = 0.8677$ across all 3,133,452 integers. There is **13.23% unused tolerance slack**.
     Trimming the highest-order Remez multiplier from 16 to 12 bits saves $\approx 210$ Toffolis.
   - **Scratch Overlapping ($62Q \to 59Q$):**
     Overlapping the low-order Remez uncomputation scratch reclaims 3 qubits, bringing $Q \to 59$.
   - **Combined Impact:** $Q=59$, $T_{\text{equiv}} = 1,320 \implies \text{Cost} = 77,880 \implies \mathbf{R_{\text{inv}} = 25.6\times}$!

---

### C. DQI ($67.02\times \to 88.00\times$) — Zero-Scratch Confluent Decoder
1. **The Natural Floor:**
   The 70 syndrome ports occupy $70 \times 12 = 840$ qubits. The retimed decoder sits at $Q = 889$ (49 scratch qubits).
2. **Architectural Opportunities:**
   - **Quotient Borrowing to Reach 852Q:**
     The 24-qubit `spare` allocation in `even_fold.py` can be completely eliminated by streaming `full_product` into the measured `head` register and borrowing scalar inverse outputs.
     This reduces peak width from $889 \to 852$ qubits ($Q^2$ cost reduction of $-8.1\%$).
   - **Mastrovito / Montgomery GF($2^{12}$) Scan:**
     In the 4,095-point syndrome scan, replacing the standard Karatsuba multiplication with a structured polynomial basis reduces dynamic Toffolis by $12\%$.
   - **Combined Impact:** $Q = 852$, $T_{\text{mean}} \approx 395,000 \implies \mathbf{R_{\text{dqi}} = 88.2\times}$!

---

## 4. Work Packages & Immediate Milestones

| Milestone | Deliverable | Owner | Verification Gate |
| :--- | :--- | :--- | :--- |
| **M32.1** | Authoritative Score & Metric Unification (`src/score_master.py`) | Infrastructure | Gate 1 & 2 |
| **M32.2** | Chemistry $(R=8, C=34)$ Factorization & J=7 Banked QROM Prototype | Chemistry Track | Gate 1, 2, 3 |
| **M32.3** | Invsqrt 59Q WS9 Pruned Remez Core with Exact 3.13M Integer Verification | Invsqrt Track | Gate 1, 2, 3, 4 |
| **M32.4** | DQI 852Q Quotient Borrowing Circuit Synthesis & Shot Verifier Run | DQI Track | Gate 1, 2, 3, 4 |
| **M32.5** | Portfolio Assembly & Submission targeting **`GM >= 30.0`** | System Lead | Official Kaggle |
