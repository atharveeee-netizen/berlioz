# Official Competition Scoring Contract & Parameter Reconstruction

**Benchmark Environment:** Google Quantum AI, Verifiable Quantum Circuit Compilation  
**Metric Definition:** Geometric mean of three individual benchmark improvement ratios:

$$\text{Score} = \left( \frac{C_{\text{invsqrt}}^{\text{ref}}}{C_{\text{invsqrt}}} \times \frac{C_{\text{DQI}}^{\text{ref}}}{C_{\text{DQI}}} \times \frac{C_{\text{chem}}^{\text{ref}}}{C_{\text{chem}}} \right)^{1/3}$$

---

## 1. Official Reference Costs ($C^{\text{ref}}$)
Extracted directly from the official benchmark reference verifiers:
- **Benchmark I (`invsqrt`):** $C_{\text{invsqrt}}^{\text{ref}} = 2{,}076{,}774.233715282$
  - Baseline architecture: 260 qubits, $C = 7{,}987.5932$ Toffoli equivalents, 200,540,928 shots.
- **Benchmark II (`DQI`):** $C_{\text{DQI}}^{\text{ref}} = 24{,}439{,}463{,}583{,}672.93$ ($2.443946 \times 10^{13}$)
  - Baseline architecture: 1,893 qubits, $T = 5{,}725{,}108.38$ mean Toffolis, $R = 1.19126046$, 102,400 shots.
- **Benchmark III (`dfthcsos`):** $C_{\text{chem}}^{\text{ref}} = 3{,}355{,}599{,}588.3155365$ ($3.3556 \times 10^9$)
  - Baseline architecture: 730 qubits, $T = 93{,}237.0$ Toffolis, $\lambda_{\text{eff}} = 49.301369$, 254,464 shots.

---

## 2. Benchmark I: `invsqrt` Verification & Cost Model
- **File:** `verifiers/invsqrt/verify_submission_invsqrt.py`
- **Instance:** $n_p = 10$, $w = 22$, $\beta = 1$, $x \in [1, 3{,}133{,}452]$.
- **Contract:**
  1. $x$ register ($22$ qubits) must be restored exactly.
  2. All scratch qubits must return cleanly to $|0\rangle$.
  3. Tracked phase $\theta$ must satisfy $|\theta - \beta/\sqrt{x}| \le \text{tol}(x) = 2^{-24} \beta / \sqrt{x}$.
  4. Non-Clifford $Z_{\text{pow}}$ rotation synthesis cost: $T_{\text{rot}} = 0.56 \log_2(1/\epsilon) + 5.3$ where $\epsilon = \pi \cdot \text{min\_margin} / (2^{64} \cdot N_{\text{rot}})$.
- **Cost Formula:**
  $$\text{Cost}_{\text{invsqrt}} = Q \times \left( T_{\text{mean}} + \frac{T_{\text{count}}}{4} \right)$$
- **Candidate Cost:**
  - 63Q Invsqrt: $Q=63, T=1416, T_{\text{gate}}=1 \implies \text{Cost} = 89{,}223.75 \implies \text{Ratio} = \mathbf{23.27602\times}$.
  - 62Q Invsqrt: $Q=62, T=1502, T_{\text{gate}}=13 \implies \text{Cost} = 93{,}325.50 \implies \text{Ratio} = \mathbf{22.25304\times}$.

---

## 3. Benchmark II: `DQI` Verification & Cost Model
- **File:** `verifiers/dqi/verify_submission_dqi.py`
- **Instance:** $m = 4095, n = 70, b = 12, r = 2016, \delta = 2^{-128}$.
- **Official Evaluation Shots:** $N = 102{,}400$ shots ($400 \times 256$).
- **Cost Formula:**
  $$\text{Cost}_{\text{DQI}} = R(\epsilon^+) \times Q^2 \times T_{\text{mean}}$$
  where:
  $$\epsilon^+ = \text{ClopperPearsonUpper}(\text{errors}, N, \log_2 \delta = -128)$$
  $$R(\epsilon) = \frac{\ln 2}{-\ln(1/2 + 2\sqrt{\epsilon})}$$
- **Exact Penalty Ladder ($N=102{,}400$):**
  - $k=0$ errors: $\epsilon^+ = 8.660587 \times 10^{-4} \implies R(0) = \mathbf{1.19126046}$
  - $k=1$ errors: $\epsilon^+ = 9.104198 \times 10^{-4} \implies R(1) = \mathbf{1.19673150}$
  - $k=2$ errors: $\epsilon^+ = 9.488156 \times 10^{-4} \implies R(2) = \mathbf{1.20138806}$
  - $k=3$ errors: $\epsilon^+ = 9.839091 \times 10^{-4} \implies R(3) = \mathbf{1.20558432}$
- **Candidate Cost (889Q Baseline):**
  - $Q = 889$, $T_{\text{mean}} = 433{,}785.6$.
  - At $k=0$: $\text{Cost} = 1.19126046 \times 889^2 \times 433{,}785.6 = 4.083996 \times 10^{11} \implies \text{Ratio} = \mathbf{59.84089\times}$.
  - At $k=0$ (un-penalized $R=1$ theoretical floor): $\text{Cost} = 3.428298 \times 10^{11} \implies \text{Ratio} = \mathbf{71.28609\times}$.

---

## 4. Benchmark III: Chemistry (`dfthcsos`)
- **File:** `verifiers/dfthcsos/verify.py`
- **Instance:** FeMoCo76o113e (76 spatial orbitals, 113 active electrons).
- **Cost Formula:**
  $$\text{Cost}_{\text{chem}} = \lambda_{\text{eff}} \times T_{\text{total}} \times Q_{\text{total}}$$
- **Champion Configuration (R=8 B143 C60):**
  - $\lambda_{\text{eff}} = 48.323649$
  - $Q_{\text{total}} = 430$
  - $T_{\text{total}} = 16{,}266.0$
  - $\text{Cost} = 337{,}993{,}966.88 \implies \text{Ratio} = \mathbf{9.927986\times}$.
