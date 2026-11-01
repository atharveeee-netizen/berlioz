# Official Cost Function Reconstruction — Masterloop 26 Part 2.2

**Date:** 2026-10-31T15:31Z  
**Evidence Class:** E1 (Direct source evidence from official verifiers) + E2 (Locally reproduced numerical verification)  
**Authoritative References:**  
- Benchmark I Verifier: `verifiers/invsqrt/verify_submission_invsqrt.py` (arXiv:2308.12352, arXiv:2203.10064)  
- Benchmark II Verifier: `verifiers/dqi/verify_submission_dqi.py` (arXiv:2408.08292, arXiv:2510.10967)  
- Benchmark III Verifier: `verifiers/dfthcsos/verify.py` & `SCORING_README.md` (arXiv:2011.03494, arXiv:2404.03058)  
- Official Evaluation Harness Reference: `tools/score_calc.py`  

---

## 1. Overview of the Competition Evaluation Architecture

The Google Quantum AI Verifiable Quantum Circuit Compilation (VQCC) competition scores quantum circuits across three complementary domains:
1. **Benchmark I (Invsqrt):** Precision arithmetic and fine-angle rotation synthesis.
2. **Benchmark II (DQI):** Fault-tolerant classical syndromic decoding over large Galois fields with measurement-based uncomputation.
3. **Benchmark III (Chemistry):** Double-factorized tensor hypercontraction (DF-THC) Hamiltonian simulation with banked QROM.

The composite competition score is the **geometric mean** of the improvement ratios across all three benchmarks relative to the official Google reference costs:

$$S = \left( R_{\text{inv}} \cdot R_{\text{dqi}} \cdot R_{\text{chem}} \right)^{1/3}$$

where each benchmark improvement ratio is defined as:

$$R_i = \frac{C_{\text{ref}, i}}{C_{\text{candidate}, i}}$$

The official reference costs are fixed constants certified across all competition evaluation instances:
- $C_{\text{INVSQRT\_REF}} = 2,076,774.233715282$
- $C_{\text{DQI\_REF}} = 24,439,463,583,672.93$
- $C_{\text{CHEM\_REF}} = 3,355,599,588.3155365$

---

## 2. Benchmark I: Invsqrt Cost Function Reconstruction

### 2.1 Problem Specification
The circuit implements the phasing operation:

$$|x\rangle|0\dots0\rangle \longrightarrow \exp\left(2\pi i \frac{\beta}{\sqrt{x}}\right) |x\rangle|0\dots0\rangle$$

for all integers $x \in [1, x_{\max}]$ where $x_{\max} = 3(2^{n_p} - 2)^2 = 3,133,452$ with $n_p = 10$, $\text{width} = 22$, and $\beta = 1$.

### 2.2 Mathematical Cost Formula
The official cost is:

$$C_{\text{inv}} = Q \cdot T_{\text{equiv}}$$

where:
- $Q = \text{circuit.num\_qubits}$ (total register + scratch qubits).
- $T_{\text{equiv}} = T_{\text{toffoli}} + \frac{T_{\text{count}}}{T_{\text{per\_toffoli}}}$.
- $T_{\text{per\_toffoli}} = 4.0$ (4 T-gates per Toffoli).
- $T_{\text{toffoli}}$ is the dynamic mean of Toffoli-like gates (`CCX`, `CCZ`, `CSWAP`) executed per simulated shot.
- $T_{\text{count}} = T_{\text{base}} + N_{\text{rot}} \cdot \text{Cost}(R_z(\epsilon))$.
- $T_{\text{base}}$ is the mean number of explicit T-gates executed.
- $N_{\text{rot}}$ is the mean number of non-Clifford, non-T arbitrary single-qubit rotations ($Z(\theta)$) executed per shot.
- $\epsilon = \frac{\pi \cdot \text{min\_margin}}{2^{64} \cdot N_{\text{rot}}}$ is the allowable rotation synthesis error in operator norm.
- $\text{Cost}(R_z(\epsilon)) = 0.56 \log_2(1/\epsilon) + 5.3$ (mixed fallback synthesis per arXiv:2203.10064).

### 2.3 Verification & Tolerance Check
- Tracked phase $\theta$ is compared in 64-bit fixed point against $r = \lfloor 2^{65} |\beta| / \sqrt{x} \rfloor$.
- Error must satisfy $|\theta - \text{target}| \le \text{tol}(x) = 2^{-24} \beta / \sqrt{x}$.
- Scratch qubits must return to $|0\rangle$ on all simulated shots.
- Register $x$ must be restored bit-exact.

### 2.4 Incumbent Evaluation (E2 Locally Verified)
For `fact/components/invsqrt_62q.kmb`:
- $Q = 62$
- $T_{\text{toffoli}} = 1332.3818$
- $T_{\text{base}} = 6.9180$
- $N_{\text{rot}} = 41.0$
- $\epsilon = 2.4340 \times 10^{-13} \implies \text{Cost}(R_z(\epsilon)) = 28.78$ T-gates
- $T_{\text{equiv}} = 1332.3818 + \frac{6.9180 + 41 \times 28.78}{4} = 1628.95$ (on 1024-shot sample)
- On official full domain sample: $T_{\text{equiv}} = 1622.7203$
- Cost: $C_{\text{inv}} = 62 \times 1622.7203 = 100,608.66$
- Ratio: $R_{\text{inv}} = \frac{2,076,774.233715282}{100,608.66} = \mathbf{20.64210\times}$

---

## 3. Benchmark II: DQI Cost Function Reconstruction

### 3.1 Problem Specification
The circuit implements the measurement-based uncomputation (MBUC) syndrome decoder for Reed-Solomon codes over $\text{GF}(2^{12})$ with $m = 4095$ codeword positions and $n = 70$ syndromes, correcting up to $l = 35$ errors.
Contract:
- Input syndrome registers $S_0 \dots S_{69}$ must be restored.
- All ancilla qubits must return to $|0\rangle$.
- Global phase multiplied by $(-1)^{\sum_j \text{popcount}(e_j \ \& \ M_j)}$.
- $Z_{\text{POW}}$ gates are strictly prohibited.

### 3.2 Mathematical Cost Formula
The official cost is:

$$C_{\text{dqi}} = R(\epsilon_+) \cdot Q^2 \cdot T_{\text{mean}}$$

where:
- $Q = \text{circuit.num\_qubits}$ (all quantum registers + ancillae).
- $T_{\text{mean}}$ is the dynamic mean number of Toffoli-like gates (`CCX`, `CCZ`, `CSWAP`) executed per shot.
- $k = \text{value\_errors} + \text{phase\_errors}$ total failed shots out of $N$ benchmark shots.
- $\epsilon_+$ is the one-sided Clopper-Pearson upper confidence bound at significance level $\delta = 2^{-128}$ ($\log_2 \delta = -128.0$).
- $R(\epsilon_+) = \frac{\ln 2}{-\ln\left(\frac{1}{2} + 2\sqrt{\epsilon_+}\right)}$ is the repetition overhead factor.

### 3.3 Clopper-Pearson Confidence Upper Bound & Feasibility Boundary
The Clopper-Pearson bound $\epsilon_+$ satisfies:
- For $k = 0$:

$$\epsilon_+ = 1 - \delta^{1/N} = 1 - 2^{-128 / N}$$

- For $k > 0$: $\epsilon_+$ is the $(1 - \delta)$ quantile of the Beta distribution $\text{Beta}(k+1, N-k)$.

**Crucial Acceptance Threshold:**  
The official verifier enforces:

$$\epsilon_+ < \frac{1}{16} = 0.0625$$

If $\epsilon_+ \ge 1/16$, the verifier raises `AssertionError: Effective error rate >= 1/16`.

**Minimum Shot Derivation:**  
For zero failures ($k=0$):

$$1 - 2^{-128/N} < \frac{1}{16} \iff 2^{-128/N} > \frac{15}{16} \iff -\frac{128}{N} > \log_2\left(\frac{15}{16}\right) \iff N > \frac{128}{-\log_2(15/16)} \approx 1374.7$$

Therefore, a quick verification with $N \le 1024$ shots will **always fail the Clopper-Pearson assertion**, regardless of whether the circuit has zero errors.  
At the official benchmark instance $N = 102,400$ shots:

$$\epsilon_+(k=0, N=102400) = 1 - 2^{-128/102400} = 8.660587301657926 \times 10^{-4}$$

$$R(\epsilon_+) = \frac{\ln 2}{-\ln(0.5 + 2\sqrt{8.6605873 \times 10^{-4}})} = \mathbf{1.1912604648115832}$$

### 3.4 Unpenalized Theoretical Ratio vs Official Ratio
- If $R = 1.0$ (theoretical zero-overhead bound):  
  $C_{\text{dqi, ideal}} = 1.0 \times 889^2 \times 427,471.2 = 337,837,645,996.80$  
  $R_{\text{dqi, ideal}} = \frac{24,439,463,583,672.93}{337,837,645,996.80} = \mathbf{72.33966\times}$
- Official penalized cost ($R = 1.19126046$):  
  $C_{\text{dqi}} = 1.19126046 \times 889^2 \times 427,471.2 = 402,454,611,307.23$  
  $R_{\text{dqi}} = \frac{24,439,463,583,672.93}{402,454,611,307.23} = \mathbf{60.72598\times}$

---

## 4. Benchmark III: Chemistry Cost Function Reconstruction

### 4.1 Problem Specification
The circuit implements the banked QROM streaming oracle family for FeMoCo76o113e ($N=76$ spatial orbitals, $\eta=113$ electrons) against reference FCIDUMP integrals.
Acceptance Gates:
- $\max_k \text{num\_qubits}(\text{ANGLE}_k) \le 128$ (`QUBIT_CAP`).
- $\text{error}_1 \le 0.020$ Ha (one-body residual).
- $\text{error}_2 \le 0.020$ Ha (two-body Frobenius residual).
- $\text{raw } \Lambda > 49.0$ Ha (`LAMBDA_FLOOR`).
- $E_{\text{gap}} > 3.914898$ Ha (`E_GAP_FLOOR`), where $E_{\text{gap}} = E_{\text{upper}} - E_{\text{SOS}}$ with $E_{\text{upper}} = -22140.27335$ Ha.
- $0 < E_{\text{gap}} < 2\Lambda$.
- No $Z_{\text{POW}}$ gates permitted.

### 4.2 Mathematical Cost Formula
The official cost is:

$$C_{\text{chem}} = \lambda_{\text{eff}} \cdot T_{\text{total}} \cdot Q_{\text{total}}$$

where:
1. **Effective normalization:**

$$\lambda_{\text{eff}} = \sqrt{E_{\text{gap}} (2\Lambda - E_{\text{gap}})}$$

2. **Total Toffolis ($T_{\text{total}}$):**

$$T_{\text{total}} = T_{\text{angles}} + T_{\text{outer}} + T_{\text{inner}} + 2(N - 1)(2\beta - 1)$$

- $T_{\text{angles}}$ is the dynamic mean Toffolis executed across forward ($U_T$) and reverse ($U_T^\dagger$) passes by the submitted `ANGLE_k` family.
- $T_{\text{outer}} + T_{\text{inner}} = 846 + 9461 = 10,307$ Toffolis (costed by `SpinFreeData_V1`).
- $2(N - 1)(2\beta - 1) = 2 \times 75 \times (2 \times 16 - 1) = 4,650$ Toffolis for Givens rotations at $\beta = \text{brot} = 16$.
- Heuristic total: $10,307 + 4,650 = 14,957$ Toffolis.
- For baseline $R=8$, $B=143$, $C=60$: $T_{\text{angles}} = 1,309.0 \implies T_{\text{total}} = 16,266.0$ Toffolis.

3. **Total Logical Qubits ($Q_{\text{total}}$):**

$$Q_{\text{total}} = Q_{\text{outer,persist}} + Q_{\text{inner,persist}} + J \cdot \beta + \max(Q_{\text{outer,temp}}, Q_{\text{inner,temp}}, Q_{\text{angles,temp}})$$

- Shared temporary workspace across sequentially executed stages: $\max(Q_{\text{outer,temp}}, Q_{\text{inner,temp}}, Q_{\text{angles,temp}})$.
- For the incumbent: $Q_{\text{total}} = 430$ qubits.

### 4.3 Incumbent Evaluation (E2 Locally Verified)
Evaluated on `scratch/incumbent_dfthcsos` against `FeMoCo76o113e.fcidump`:
- $\lambda_{\text{eff}} = 48.29920925404513$
- $T_{\text{total}} = 16,266.0$
- $Q_{\text{total}} = 430$
- Cost: $C_{\text{chem}} = 48.29920925 \times 16266.0 \times 430 = 337,823,023.22$
- Ratio: $R_{\text{chem}} = \frac{3,355,599,588.3155365}{337,823,023.22} = \mathbf{9.933010\times}$

---

## 5. Composite Score & Marginal Exchange Rates

### 5.1 Authoritative Incumbent Score
With the three independently verified ratios:
- $R_{\text{inv}} = 20.64210$
- $R_{\text{dqi}} = 60.72598$
- $R_{\text{chem}} = 9.933010$

$$S = \left( 20.64210 \cdot 60.72598 \cdot 9.933010 \right)^{1/3} = (12,450.933)^{1/3} = \mathbf{23.17767}$$

### 5.2 Marginal Exchange Rates
Because $S = (R_{\text{inv}} R_{\text{dqi}} R_{\text{chem}})^{1/3}$, the log-differential is:

$$d\ln S = \frac{1}{3} d\ln R_{\text{inv}} + \frac{1}{3} d\ln R_{\text{dqi}} + \frac{1}{3} d\ln R_{\text{chem}}$$

1. **Uniform 1% Ratio Improvement:**  
   A 1% reduction in any single benchmark cost yields:
   $$\Delta S = S \cdot \left( 1.01^{1/3} - 1 \right) \approx 23.17767 \times 0.003322 = \mathbf{+0.0770 \text{ points}}$$

2. **DQI Qubit vs Toffoli Trade-off:**  
   Because $C_{\text{dqi}} \propto Q^2 T$, a change $\Delta Q$ alters cost as $\approx \frac{2 \Delta Q}{Q}$.  
   At $Q = 889$, reducing 1 qubit is equivalent to saving:
   $$\Delta T_{\text{equiv}} = \frac{2}{889} \times 427,471.2 = \mathbf{961.7 \text{ dynamic Toffolis}}$$

3. **Register Compaction Breakeven Budget:**  
   Reducing register width from $Q_{\text{old}} = 889$ to $Q_{\text{new}}$ permits an increase in dynamic Toffolis up to:
   $$\Delta T_{\max} = T_{\text{old}} \left[ \left(\frac{Q_{\text{old}}}{Q_{\text{new}}}\right)^2 - 1 \right]$$
   - $889 \to 880$: $\Delta T_{\max} = +8,788$ Toffolis
   - $889 \to 860$: $\Delta T_{\max} = +29,315$ Toffolis
   - $889 \to 840$: $\Delta T_{\max} = +51,326$ Toffolis
   - $889 \to 740$: $\Delta T_{\max} = +189,474$ Toffolis
