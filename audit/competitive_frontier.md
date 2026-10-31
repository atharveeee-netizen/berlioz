# COMPETITIVE FRONTIER & MATHEMATICAL LEADERBOARD GAP AUDIT

**Target:** Google Quantum AI — Verifiable Quantum Circuit Compilation  
**Current Graded Baseline:** $23.00043$ (Rank #377, Submission `57812617`)  
**Current Local Verified Composite:** $23.06062$  
**Leaderboard Targets:** Top 10 ($S \ge 25.00$), Rank #1 ($S \ge 26.80$)  

---

## 1. MATHEMATICAL PRODUCT SENSITIVITY

Because the competition score is a 3-way geometric mean:
$$S = (R_{\text{inv}} R_{\text{DQI}} R_{\text{chem}})^{1/3} \iff P = S^3 = R_{\text{inv}} R_{\text{DQI}} R_{\text{chem}}$$
Small score increments require large compounding multiplicative product gains:
- **Baseline Product ($S = 23.0606$):** $P = 12{,}263.26$
- **Top 10 Product ($S = 25.0000$):** $P = 15{,}625.00$ ($\times 1.2741$, or $+27.4\%$)
- **Rank #1 Product ($S = 26.8000$):** $P = 19{,}248.83$ ($\times 1.5696$, or $+57.0\%$)

---

## 2. SINGLE-BENCHMARK VS MULTI-BENCHMARK CO-DESIGN

If optimization is restricted to a single benchmark while keeping the other two fixed:
- **DQI-Only to Top 10:** $R_{\text{DQI}}$ must increase from $59.84\times$ to **$76.24\times$** (requires a **$-21.5\%$** drop in DQI cost, reducing dynamic Toffolis from 433k to 340k at $Q=889$).
- **Invsqrt-Only to Top 10:** $R_{\text{inv}}$ must increase from $20.64\times$ to **$26.30\times$** (requires cost to drop to 78,960).
- **Chemistry-Only to Top 10:** $R_{\text{chem}}$ must increase from $9.93\times$ to **$12.65\times$** (requires cost to drop to $2.65 \times 10^8$).

### The Multi-Benchmark Advantage:
Rather than demanding an unrealistic $-21.5\%$ drop from a single benchmark:
- Top 10 can be achieved if **all 3 benchmarks improve by only $+8.41\%$** ($1.0841^3 = 1.2741$).
- Rank #1 can be achieved if **all 3 benchmarks improve by $+16.22\%$** ($1.1622^3 = 1.5696$).

---

## 3. REALISTIC TOP 10 ARCHITECTURAL HYPOTHESES

1. **DQI Lever (The Uncomputation Debt):**
   - $54.3\%$ of DQI Toffolis are spent in uncomputation.
   - If measurement-based uncomputation (HMR) or teleported Pauli frame correction is applied to intermediate syndrome uncomputation, up to $247{,}000$ Toffolis can be removed, boosting $R_{\text{DQI}}$ to $> 100\times$.
2. **Invsqrt Lever (Unified Newton Workspace):**
   - Folding polynomial lookup tables directly into Newton-Raphson multiplier workspace to reclaim 4-6 ancillas ($Q \to 56\text{--}58$).
3. **Chemistry Lever (Symmetric Orbital Grouping):**
   - Grouping symmetry-equivalent orbital rotations to reduce angle circuit count from 16 to 12 without triggering linear QROM expansion.
