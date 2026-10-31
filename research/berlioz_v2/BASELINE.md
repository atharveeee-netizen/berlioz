# BERLIOZ 2.0 — REFERENCE BASELINES & AUDIT TRAIL

**Platform:** Berlioz 2.0 Autonomous Quantum Circuit Optimization  
**Host Baseline:** Google Quantum AI Verifiable Quantum Circuit Compilation (Kaggle)  
**Last Synchronized:** 31 October 2026  

---

## 1. OFFICIAL COMPETITION REFERENCE COSTS

The competition evaluates submissions against official Google reference circuits using the geometric mean of ratio improvements:

$$\text{Composite Score} = \left( R_{\text{invsqrt}} \times R_{\text{dqi}} \times R_{\text{chem}} \right)^{1/3}$$

where $R_i = \frac{\text{RefCost}_i}{\text{Cost}_i}$.

| Benchmark | Target Specification | Reference Cost ($\text{RefCost}_i$) | Reference Formulation |
|---|---|---|---|
| **Invsqrt** | 32-bit fixed-point $1/\sqrt{x}$ | **2,076,774.23372** | Analytical floating-point cost model |
| **DQI** | 70-symbol Reed-Solomon syndrome decoder | **24,439,463,583,672.93** | Kickmix shot simulator cost ($T_{\text{mean}} \times R(0)$) |
| **Chemistry** | FeMoco electronic structure state preparation | **3,355,599,588.31554** | $Q=430, T=16,266, \lambda_{\text{ref}}=480.0$ |

---

## 2. HISTORICAL BERLIOZ PROGRESSION

| Milestone / Sub ID | Invsqrt Cost (Ratio) | DQI Cost (Ratio) | Chemistry Cost (Ratio) | Composite Score | Leaderboard / Local Status |
|---|---|---|---|---|---|
| **Google Reference** | 2,076,774 (1.000×) | 24,439,463,583,672 (1.000×) | 3,355,599,588 (1.000×) | **1.00000** | Competition baseline |
| **Submission 57800637** | 100,608 (20.642×) | 412,414,291,100 (59.259×) | 338,000,000 (9.928×) | **22.99562** | Verified Leaderboard |
| **Submission 57811741** | 100,608 (20.642×) | 422,900,000,000 (57.790×) | 338,000,000 (9.928×) | **22.80575** | Regression on DQI salt |
| **Submission 57812617** | 100,608 (20.642×) | 408,396,960,113 (59.842×) | 338,000,000 (9.928×) | **23.00043** | Top Leaderboard (Rank ~377) |
| **Submission 57823923** | 100,608 (20.642×) | 412,414,291,100 (59.259×) | 338,000,000 (9.928×) | **22.99562** | Public check payload |
| **Berlioz 2.0 Champion** | **100,608.68 (20.642×)** | **402,454,582,311.96 (60.726×)** | **337,823,023.22 (9.933×)** | **23.17767** | **New Verified Local SOTA** |

---

## 3. EXTERNAL STATE-OF-THE-ART BASELINES

To evaluate competitive positioning against the global research frontier:

| Work / Group | Benchmark Focus | Best Claimed / Reported Metric | Key Technique | Status in Berlioz |
|---|---|---|---|---|
| **Gidney et al. (Google)** | Invsqrt & Adder | $T_{\text{equiv}} \approx 1,620$ | Carry-lookahead + dirty ancilla borrowing | Integrated (DS-12) |
| **Gluzdov (OpenFermion)** | FeMoco Factorizations | $\lambda \approx 48.3$, $T=16,266$ | 65x60x30 Tensor Factorization | Integrated (DS-09) |
| **Kauers-Moosbauer** | GF(2^k) Multiplication | Tensor rank 42 for $k=12$ | Bilinear algebraic decomposition | Integrated (DS-10) |
| **Anthropic (Gu et al.)** | Modular Inversion | Divsteps reversible uncompute | Dynamic tracking & MBUC | Integrated (DS-18) |
| **yoyobar (Kaggle SOTA)** | DQI & Chemistry | DQI $427.5\text{k}$ Toffolis, Chem $\lambda=48.299$ | One-carry pole history + Voodoo gauge | **Fully Ingested into Champion** |
