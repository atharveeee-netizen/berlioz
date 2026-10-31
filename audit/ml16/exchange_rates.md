# CANONICAL EXCHANGE RATES & COST SENSITIVITIES
## Verified on 31 October 2026 via `tools/score_calc.py`

### 1. Composite Score Elasticity
The competition composite score is:
$$S = (R_{\text{inv}} \cdot R_{\text{dqi}} \cdot R_{\text{chem}})^{1/3}$$
Therefore, the marginal score sensitivity with respect to any single component ratio $R_i$ is strictly symmetric:
$$\frac{\partial \ln S}{\partial \ln R_i} = \frac{1}{3}$$
- **+1.0% improvement on ANY single ratio** yields **+0.3322% on the composite score** (approx **+0.0770 score points** at $S = 23.18$).
- Improvements across benchmarks compound multiplicatively:
  $$P = S^3 = R_{\text{inv}} \cdot R_{\text{dqi}} \cdot R_{\text{chem}}$$

---

### 2. DQI Resource Exchange Rates
$$C_{\text{DQI}} = R(\epsilon^+) \times Q^2 \times T_{\text{mean}}$$
- At $Q = 889$ and $T_{\text{mean}} = 427{,}471.2$:
  - **1 Qubit Sensitivity:** $\frac{\partial C}{\partial Q} = 2 R Q T \implies \frac{\Delta C}{C} \approx \frac{2}{Q} = \frac{2}{889} \approx 0.225\%$.
  - 1 Qubit is equivalent to $\approx \mathbf{962 \text{ Toffolis}}$.
  - **1% Cost Reduction** requires saving $\approx \mathbf{4{,}275 \text{ Toffolis}}$ or $\approx \mathbf{4.44 \text{ Qubits}}$.
- **Break-Even Toffoli Allowance for Qubit Reduction ($\Delta T_{\text{max}}$):**
  $$\Delta T_{\text{max}} = T_{\text{old}} \cdot \left[ \left(\frac{Q_{\text{old}}}{Q_{\text{new}}}\right)^2 - 1 \right]$$
  - $Q \to 880$: Break-even $\Delta T_{\text{max}} = \mathbf{+8{,}788 \text{ Toffolis}}$
  - $Q \to 860$: Break-even $\Delta T_{\text{max}} = \mathbf{+29{,}316 \text{ Toffolis}}$
  - $Q \to 840$: Break-even $\Delta T_{\text{max}} = \mathbf{+51{,}326 \text{ Toffolis}}$
  - $Q \to 740$: Break-even $\Delta T_{\text{max}} = \mathbf{+189{,}475 \text{ Toffolis}}$ (Falsified: $Q \ge 840$ is physical floor)

---

### 3. DQI Failure Price (Clopper-Pearson at $N = 102{,}400, \delta = 2^{-128}$)
Cost increase versus $k=0$ errors:
- $k = 1$: $+0.46\%$ cost increase
- $k = 2$: $+0.85\%$ cost increase
- $k = 5$: $+1.82\%$ cost increase
- $k = 10$: $+3.17\%$ cost increase
- $k = 20$: $+5.33\%$ cost increase
- $k = 50$: $+10.25\%$ cost increase
- $k = 100$: $+16.60\%$ cost increase
- $k = 200$: $+26.80\%$ cost increase

---

### 4. Invsqrt Resource Exchange Rates
$$C_{\text{inv}} = Q \times T_{\text{equiv}}$$
- At $Q = 62, T_{\text{equiv}} = 1{,}622.7$:
  - **1 Qubit Sensitivity:** $\Delta C / C \approx 1/62 = \mathbf{1.61\%}$ ($\approx \mathbf{26.17 \text{ Toffoli-equivalents}}$).
  - 1% Cost Reduction $\approx \mathbf{16.23 \text{ Toffoli-equivalents}}$ or $\approx \mathbf{0.62 \text{ Qubits}}$.
  - Each rotation synthesized to $\epsilon \approx 5.21 \times 10^{-13}$ requires $3 \lceil \log_2(1/\epsilon) \rceil = 3 \times 41 = 123$ single-qubit gates $\approx 10.25$ Toffoli-equivalents.

---

### 5. Chemistry Resource Exchange Rates
$$C_{\text{chem}} = \lambda_{\text{eff}} \times Q_{\text{total}} \times T_{\text{total}}$$
- At $Q = 430, T = 16{,}266, \lambda = 48.2992$:
  - **1 Qubit Sensitivity:** $\approx \mathbf{37.8 \text{ Toffolis}}$ ($\approx \mathbf{0.23\%}$ cost).
  - **1% Cost Reduction:** $\approx \mathbf{162.7 \text{ Toffolis}}$ or $\approx \mathbf{4.3 \text{ Qubits}}$ or $\approx \mathbf{0.483 \text{ in } \lambda_{\text{eff}}}$.
