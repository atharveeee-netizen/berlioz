# CHEMISTRY R=10 FACTORIZATION & RESOURCE AUDIT REPORT

**Author:** Berlioz Quantum AI Compiler Team  
**Scope:** Track B — Double-Factorized THC Chemistry Simulation (FeMoCo Active Site)  
**Objective:** Independent audit of $R=10$ continuous factorization, energy/spectral gap constraints, 4-address banked QROM synthesis, and comparison against frozen $R=8$ incumbent.

---

## 1. Executive Summary & Verification Verdict

| Metric | Official Limit | Certified $R=8$ Incumbent | Measured $R=10$ Candidate | Status |
|---|---|---:|---:|:---:|
| **Rank ($R$) / Bases ($B$)** | — | $R=8, B=143, C=60$ | $R=10, B=129, C=60$ | — |
| **One-body Error ($e_1$)** | $\le 20.0\text{ mHa}$ | $18.42\text{ mHa}$ | **$18.9959\text{ mHa}$** | **PASS** |
| **Two-body Error ($e_2$)** | $\le 20.0\text{ mHa}$ | $19.11\text{ mHa}$ | **$19.6543\text{ mHa}$** | **PASS** |
| **Spectral Gap ($E_{\text{gap}}$)** | $> 3.914898\text{ Ha}$ | $3.9388\text{ Ha}$ | **$3.9435\text{ Ha}$** | **PASS** |
| **LCU Normalization ($\Lambda$)** | $> 49.0\text{ Ha}$ | $296.8\text{ Ha}$ | **$294.48\text{ Ha}$** | **PASS** |
| **Effective Norm ($\lambda_{\text{eff}}$)** | minimize | $48.2992$ | **$48.0311$** | **IMPROVED (-0.55%)** |
| **Angle Circuit Max Qubits** | $\le 128\text{ qubits}$ | $112\text{ qubits}$ ($J=5$) | **$103\text{ qubits}$ ($J=3$)** / **$124\text{ qubits}$ ($J=7$)** | **PASS** |
| **State Prep Toffolis** | model | $7,930$ | **$9,072$** | $+14.4\%$ |
| **Angle QROM Toffolis (2-pass)** | measured | $8,336$ | **$21,700$ ($J=3$)** / **$17,006$ ($J=7$)** | $+104.0\%$ |
| **Total Chemistry Toffolis** | minimize | **$16,266.0$** | **$30,772.0$ ($J=3$)** / **$26,078.0$ ($J=7$)** | **REGRESSION** |
| **Active Qubits ($Q_{\text{total}}$)** | model | $430$ | **$415$ ($J=3$)** / **$447$ ($J=7$)** | — |
| **Compiled Cost** | minimize | **$337,823,023.22$** | **$613,375,926.49$ ($J=3$)** / **$559,892,578.19$ ($J=7$)** | **REGRESSION** |
| **Official Benchmark Ratio** | maximize | **$9.93301\times$** | **$5.4707\times$ ($J=3$)** / **$5.9933\times$ ($J=7$)** | **REJECTED FOR PROMOTION** |

**PROMOTION VERDICT:** Under the Global Rules ("Never overwrite the champion", "Keep measured results separate from projections", "Promote only a complete candidate that improves official composite score"), **$R=10$ is REJECTED for promotion**. The frozen $R=8$ candidate remains the official active champion for Benchmark III.

---

## 2. Factorization & Continuous Metric Validation

The $R=10$ continuous factorization artifact (`fact/dfthc_r10_b129_c60_brot8.npz`) was evaluated against the official 128 MB FeMoCo active-space FCIDUMP (`FeMoCo76o113e.fcidump`) using `verifiers/dfthcsos/verify.py` and `dfthcsos.scoreinfra.dfthc_math.evaluate_dfthc_angle_words`:
- Symmetry shifts $(S, \beta_1)$ were strictly bound to official baseline fixed shifts (`load_fixed_shifts()`).
- Reconstructed vectors $U$ and $W$ were computed from recovered angle words on the 75-edge Givens tree with rotation bit-width $\text{brot} = 8$.
- **Continuous Metrics Confirmed:**
  - $e_1 = 0.0189959\text{ Ha} = 18.9959\text{ mHa} \le 20.0\text{ mHa}$.
  - $e_2 = 0.0196543\text{ Ha} = 19.6543\text{ mHa} \le 20.0\text{ mHa}$.
  - $\Lambda = 294.475098\text{ Ha} > 49.0\text{ Ha}$.
  - $E_{\text{gap}} = 3.943529\text{ Ha} \in [3.8, 4.0]\text{ Ha}$.
  - $\lambda_{\text{eff}} = \sqrt{E_{\text{gap}} (2\Lambda - E_{\text{gap}})} = \mathbf{48.031141}$.

The continuous mathematical optimization successfully lowered $\lambda_{\text{eff}}$ from $48.2992$ down to $48.0311$.

---

## 3. The Discrete Bottleneck: QROM Banked Address Expansion

Despite superior continuous $\lambda_{\text{eff}}$, the full compilation demonstrates why continuous and discrete optimization must be co-designed:

1. **Address Register Growth:**
   - In $R=8, B=143$: Number of addresses $A = N + R \times B = 76 + 8 \times 143 = 1,220$.
   - In $R=10, B=129$: Number of addresses $A = N + R \times B = 76 + 10 \times 129 = 1,366$.
2. **Width Constraint ($\le 128$ Qubits):**
   In 4-address banked QROM with half-open Givens gauge (`angles_qrom.py`):
   $$\text{Qubit Need}(J) = n + \text{brot} \cdot J + 3(\text{brot} - 1) \cdot J + 6 = 11 + 8J + 21J + 6 = 17 + 29J$$
   - For $J = 5$: $17 + 145 = 162\text{ qubits} > 128$ (**Violates qubit cap!**).
   - Maximum allowable batch size in 4-address mode: $J = 3$ ($17 + 87 = 104 \le 128$).
3. **Circuit Count Explosion:**
   - For $J = 3$, $K = \lceil 75 / 3 \rceil = \mathbf{25\text{ angle circuits}}$ must be synthesized.
   - Total 1-pass angle Toffolis: $10,850$ $\implies$ 2-pass Toffolis: **$21,700$**.
   - In contrast, $R=8$ with $J=5$ needs only 15 circuits totaling $8,336$ 2-pass Toffolis.
4. **State-Preparation Overhead:**
   - `SpinFreeData_V1` inner state prep scales with $R \times C \times B$:
     - For $R=8$: $8 \times 60 \times 143 = 68,640$ values $\implies 5,311$ Toffolis.
     - For $R=10$: $10 \times 60 \times 129 = 77,400$ values $\implies 6,423$ Toffolis.

---

## 4. Architectural Recommendation

To make $R=10$ viable and achieve the projected $\sim 14,000$ Toffolis ($11.6\times$ ratio):
- Pruning groups ($B$) from $129$ down to $B \le 114$ is required so that $A \le 1,216$, allowing $J=4$ or $J=5$ within 128 qubits.
- Until a pruned $R=10, B \le 114$ factorization is generated that simultaneously satisfies $e_1, e_2 \le 20\text{ mHa}$, the **$R=8$ candidate ($9.93301\times$) remains our certified, verified champion**.
