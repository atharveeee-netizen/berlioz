# MASTERLOOP 28 — PHASE 2: INVSQRT MARGIN LADDER & WS9 AUDIT REPORT

**Document ID:** `ML28-P2-INVSQRT-LADDER`  
**Execution Environment:** Antigravity IDE, Windows 11 x86_64, Python 3.10+, Kickmix 0.1.x  
**Evaluated Artifact:** `invsqrt.kmb` (SHA-256: `a568bc79348165bad5be2349960d200300c5639ffd2142aca6d548e764a399d9`)  
**Domain Scope:** Exhaustive evaluation of all $3,133,452$ required inputs ($x = 1, \dots, 3,133,452$)  
**Throughput:** $129,460\text{ inputs/sec}$ (Total duration: $24.20\text{ seconds}$)

---

## 1. Executive Summary & Stopping Decision

Under Masterloop 17 Workstream 9 (ML17 WS9), we evaluated whether seed-table entries, rounding constants, and final truncation could be adjusted to yield two or more margin doublings ($\min_x (\text{tol}(x) - |\text{error}(x)|)$), which would lower the fallback rotation synthesis cost.

### Key Empirical Findings:
1. **Full Domain Precision Verified:** All $3,133,452$ required benchmark inputs pass the verifier's strict tolerance bound ($|\text{error}(x)| \le \text{tol}(x)$). Zero violations observed.
2. **Global Minimum Margin:**
   $$\min_{x \in [1, 3133452]} \text{margin}(x) = \mathbf{58,597,850\text{ units of } 2^{-64}\text{ turns}} \approx 3.1765 \times 10^{-12}\text{ turns}.$$
   The minimum margin represents only **$1.2180\%$ of the allowed tolerance** at the worst-margin input.
3. **Worst Error Ratio:**
   $$\max_{x \in [1, 3133452]} \frac{|\text{error}(x)|}{\text{tol}(x)} = \mathbf{0.99932377} \quad (\text{at } x = 161).$$
   At $x=161$, the circuit's phase error reaches **$99.9324\%$ of the maximum allowed limit**, leaving a fractional margin of only $0.0676\%$.
4. **Quantization Barrier to Margin Doubling:**
   - Shifting any seed-table entry, polynomial coefficient, or rounding constant by $\pm 1$ quantum bit shifts the output phase by $\ge 2^{-32}$ turns ($\approx 4.295 \times 10^9$ units of $2^{-64}$).
   - This discrete step is **$73.3\times$ larger than the entire remaining margin ($58.598 \times 10^6$ units)**.
   - Any manual or heuristic perturbation to widen the margin on the worst inputs instantly causes severe tolerance violations ($|\text{error}| > \text{tol}$) on adjacent cliff-edge inputs ($x=161, 52229, 12673$).
5. **Mandated Stopping Decision:**
   Fewer than two useful margin doublings are achievable within the current circuit architecture. Per protocol instructions (*"If fewer than two useful margin doublings are achievable, document the result and stop this experiment"*), **Phase 2 is formally stopped**, and the champion circuit `invsqrt.kmb` is preserved unchanged.

---

## 2. Exhaustive Margin Ladder Analysis

### Top 10 Worst-Margin Inputs across $3,133,452$ Inputs

| Rank | Input ($x$) | Remaining Margin ($2^{-64}$ turns) | Error Ratio ($|\text{err}|/\text{tol}$) | Allowed Tolerance ($2^{-64}$ turns) | Used Error ($2^{-64}$ turns) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **$52,229$** | **$58,597,850$** | $0.98782027$ | $4,811,095,427$ | $4,752,497,577$ |
| **2** | **$851,985$** | **$58,597,850$** | $0.95080762$ | $1,191,197,716$ | $1,132,599,866$ |
| **3** | **$2,157,629$** | **$58,597,850$** | $0.92171650$ | $748,533,844$ | $689,935,994$ |
| **4** | **$869,138$** | **$58,597,851$** | $0.95031489$ | $1,179,384,612$ | $1,120,786,761$ |
| **5** | **$2,474,113$** | **$58,597,851$** | $0.91617151$ | $699,020,739$ | $640,422,888$ |
| **6** | **$835,671$** | **$58,597,851$** | $0.95128087$ | $1,202,768,819$ | $1,144,170,968$ |
| **7** | **$983,396$** | **$58,597,851$** | $0.94714987$ | $1,108,755,042$ | $1,050,157,191$ |
| **8** | **$3,046,270$** | **$58,597,851$** | $0.90698220$ | $629,963,851$ | $571,366,000$ |
| **9** | **$3,001,932$** | **$58,597,851$** | $0.90766161$ | $634,599,026$ | $576,001,175$ |
| **10** | **$12,673$** | **$58,597,851$** | $0.99400041$ | $9,766,975,743$ | $9,708,377,892$ |

### Margin Ladder Distribution:
- **Rank 1:** $x = 52,229 \implies \text{Margin} = 58,597,850$
- **Rank 10:** $x = 12,673 \implies \text{Margin} = 58,597,851$
- **Rank 100:** $x = 2,156,029 \implies \text{Margin} = 74,864,970$
- **Worst Ratio:** $x = 161 \implies \text{Ratio} = 0.99932377$, $\text{Margin} = 58,597,850$

---

## 3. Margin Doubling Sensitivity & Theoretical Bounds

In the official verifier (`verify_submission_invsqrt.py:316-322`), the cost of synthesizing $n_{\text{rot}} = 41$ non-Clifford rotations is governed by:

$$\text{eps} = \frac{\pi \cdot \text{min\_margin}}{2^{64} \cdot n_{\text{rot}}}, \quad t_{\text{rot}} = 0.56 \log_2(1/\text{eps}) + 5.3\text{ T gates}.$$

| Evaluation State | Margin ($\times 10^6$ units) | Synthesis $\epsilon$ | T-gates / rot | Total Rotation T | Net Toffoli Savings | Official Score | Net Ratio Impact |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Current Baseline** | **$58.598$** | **$2.434 \times 10^{-13}$** | **$28.765$** | **$1,179.36$** | Baseline ($0.0$) | **$100,517.58$** | **`20.66080x`** |
| **1 Margin Doubling ($2\times$)** | $117.196$ | $4.868 \times 10^{-13}$ | $28.205$ | $1,156.40$ | $+5.74\text{ Toff}$ | $100,161.70$ | $+0.35\%$ ($20.73\times$) |
| **2 Margin Doublings ($4\times$)** | $234.391$ | $9.736 \times 10^{-13}$ | $27.645$ | $1,133.44$ | $+11.48\text{ Toff}$ | $99,805.82$ | $+0.71\%$ ($20.81\times$) |
| **Zero Synthesis Fallback (Hypothetical)** | N/A | $\infty$ | $0.000$ | $0.00$ | $+294.84\text{ Toff}$ | $93,325.50$ | $+7.71\%$ ($22.25\times$) |

### Conclusion:
Even if two margin doublings were theoretically possible, the net gain would be only $+11.48$ Toffoli-equivalents ($+0.71\%$ score improvement). Because discrete coefficient shifting causes immediate cliff-edge failure, the 62Q Lawson Horner implementation in `portfolio_ml27_repaired.zip` is locked as the optimal champion.
