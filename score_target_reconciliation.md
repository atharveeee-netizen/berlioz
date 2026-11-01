# SCORE TARGET RECONCILIATION & DQI TOFFOLI SENSITIVITY

**Date:** October 31, 2026  
**Competition:** Google Quantum AI — Verifiable Quantum Circuit Compilation (Kaggle)  
**Objective:** Authoritative reconciliation of composite geometric-mean score targets and corresponding DQI Toffoli limits.

---

## 1. Governing Official Formulas

The competition composite score $S$ is defined as the geometric mean of the three task improvement ratios:
$$S = \left( R_{\text{inv}} \times R_{\text{dqi}} \times R_{\text{chem}} \right)^{1/3}$$

Where:
$$R_i = \frac{\text{RefCost}_i}{\text{Cost}_i}$$

### Official Reference Costs:
- **Benchmark I (Invsqrt):** $\text{RefCost}_{\text{inv}} = 2{,}076{,}774.233715282$
- **Benchmark II (DQI):** $\text{RefCost}_{\text{dqi}} = 24{,}439{,}463{,}583{,}672.93$
- **Benchmark III (Chemistry):** $\text{RefCost}_{\text{chem}} = 3{,}355{,}599{,}588.3155365$

### Official DQI Cost Model:
$$\text{Cost}_{\text{dqi}} = R(\epsilon^+) \times Q^2 \times T_{\text{mean}}$$
Where:
- $Q = 889$ (qubits)
- $R(\epsilon) = \frac{\ln(2)}{-\ln(1/2 + 2\sqrt{\epsilon})}$
- For $k = 0$ errors across $N = 102{,}400$ test shots at confidence $\delta = 2^{-128}$:
  $$\epsilon^+ = 8.660587 \times 10^{-4} \implies R(0) = \mathbf{1.19126046}$$

---

## 2. Sensitivity Derivations with Fixed Benchmarks

Holding Benchmark I and Benchmark III fixed at certified champion values:
- $R_{\text{inv}} = \mathbf{20.64210239}$ (Candidate Cost: $100{,}608.66$)
- $R_{\text{chem}} = \mathbf{9.93301019}$ (Candidate Cost: $337{,}823{,}023.22$)
- Product: $P_{\text{other}} = R_{\text{inv}} \times R_{\text{chem}} = \mathbf{205.03821}$

To achieve target composite score $S$:
$$S^3 = P_{\text{other}} \times R_{\text{dqi}} \implies R_{\text{dqi}}(S) = \frac{S^3}{205.03821}$$

The required DQI candidate cost is:
$$\text{Cost}_{\text{dqi}}(S) = \frac{\text{RefCost}_{\text{dqi}}}{R_{\text{dqi}}(S)} = \frac{24{,}439{,}463{,}583{,}672.93 \times 205.03821}{S^3} = \frac{5.011024 \times 10^{15}}{S^3}$$

Solving for required mean dynamic Toffolis $T_{\text{mean}}$:
$$T_{\text{mean}}(S) = \frac{\text{Cost}_{\text{dqi}}(S)}{R(0) \times Q^2} = \frac{\text{Cost}_{\text{dqi}}(S)}{1.19126046 \times 889^2} = \frac{\text{Cost}_{\text{dqi}}(S)}{941{,}478.29}$$

---

## 3. Authoritative Reconciliation Table

| Target Milestone | Composite Score ($S$) | Required DQI Ratio ($R_{\text{dqi}}$) | Required DQI Cost | Required $T_{\text{mean}}$ (Dynamic) | $\Delta T_{\text{mean}}$ from Champion | Estimated Static Toffolis |
|---|---:|---:|---:|---:|---:|---:|
| **Certified Incumbent** | **`23.17767`** | **`60.72598x`** | **`402,454,838,389`** | **`427,471.2`** | **`0.0`** | **`441,968`** |
| **Milestone 1** | **`24.00000`** | **`67.42158x`** | **`362,487,264,866`** | **`385,019.3`** | **`-42,451.9`** | **`398,069`** |
| **Intermediate** | **`24.50000`** | **`71.72365x`** | **`340,744,006,291`** | **`361,924.5`** | **`-65,546.7`** | **`374,191`** |
| **Mission Target** | **`25.00000`** | **`76.20531x`** | **`320,705,532,769`** | **`340,640.4`** | **`-86,830.8`** | **`352,185`** |
| **Top 5 Contention** | **`25.50000`** | **`80.87034x`** | **`302,207,986,341`** | **`320,993.1`** | **`-106,478.1`** | **`331,872`** |
| **Top 3 Contention** | **`26.00000`** | **`85.72146x`** | **`285,106,050,837`** | **`302,828.1`** | **`-124,643.1`** | **`313,091`** |
| **Rank 1 (`Breaking1800`)** | **`26.76409`** | **`93.50212x`** | **`261,378,001,817`** | **`277,625.1`** | **`-149,846.1`** | **`287,034`** |

---

## 4. Key Takeaways & Strategic Milestones

1. **The 24 Milestone vs the 25 Target:**
   - **Score 24 Milestone:** Requires dynamic $T_{\text{mean}} \le \mathbf{385{,}019.3}$ (saving $42{,}452$ Toffolis). This can be achieved immediately by combining AND-reuse across symmetric Hankel anti-diagonals ($-22.6\text{k}$), MBUC head closure ($-1.4\text{k}$), and Chien root search degree-bounding ($-29.2\text{k}$).
   - **Score 25 Mission Target:** Requires dynamic $T_{\text{mean}} \le \mathbf{340{,}640.4}$ (saving $86{,}831$ Toffolis). This requires lowering Inversionless Berlekamp-Massey (RiBM) into the production synthesis module, completely eliminating the $242.4\text{k}$ inversion uncomputation chain.
2. **Dynamic to Static Execution Ratio:**
   The empirical dynamic-to-static ratio in `km.Simulator` is:
   $$\frac{T_{\text{static}}}{T_{\text{mean}}} = \frac{441{,}968}{427{,}471.2} \approx 1.0339$$
   Static Toffoli targets must be scaled by this ratio when validating static compiler operation counts.
