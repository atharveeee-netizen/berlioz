# Benchmark Constraint Matrix — Masterloop 26 Part 2.1 & 2.4

**Date:** 2026-10-31T15:33Z  
**Evidence Class:** E1 (Direct verifier source audit)  
**Standard:** Syzygy Spec-Driven Development Standard (v1.0.0)  

---

## 1. Global Constraint Matrix

| Dimension | Benchmark I: Invsqrt | Benchmark II: DQI | Benchmark III: Chemistry |
|---|---|---|---|
| **Problem Type** | Phasing $|x\rangle \to e^{2\pi i \beta / \sqrt{x}} |x\rangle$ | Reed-Solomon MBUC syndromic decoder | Double-factorized THC QROM streaming oracle |
| **System Instance** | $n_p = 10, \beta = 1$ | $m = 4095, n = 70, b = 12, r = 2016$ | FeMoCo76o113e ($N=76, \eta=113$) |
| **Domain Size** | $x \in [1, 3,133,452]$ | $t \le 35$ errors across 4,095 positions | 1,220 orbital addresses (76 1-body + 1144 2-body) |
| **Input Register Contract** | `x`: 22 distinct qubits, little-endian | `S0`..`S69`: 70 12-qubit registers | `selection`: $\lceil \log_2(76 + R\cdot B) \rceil$ qubits |
| **Output / MBUC Register Contract** | None (in-place phase on $|x\rangle$) | `E0`..`E4094`: 4,095 12-bit classical registers | `word_0`..`word_{J-1}`: $J$ registers of width $\text{brot}$ |
| **Scratch / Ancilla Rule** | All other qubits must return to $|0\rangle$ | All ancilla qubits must return to $|0\rangle$ | Workspace must return to $|0\rangle$ after each circuit |
| **Input Restoration Rule** | `x` must be restored bit-exact | `S0`..`S69` must be restored bit-exact | `selection` restored; reverse pass must clear words |
| **Hard Qubit Cap** | None (penalized linearly in cost) | None (penalized quadratically in cost) | **Strict $\le 128$ qubits** on each `ANGLE_k` circuit |
| **Gate Restrictions** | Any Clifford + T + $Z(\theta)$ | **Strictly NO $Z_{\text{POW}}$ allowed** | **Strictly NO $Z_{\text{POW}}$ allowed** |
| **Tolerance / Error Floor** | $|\text{error}| \le 2^{-24} \beta / \sqrt{x}$ | Total failed shots must satisfy $\epsilon_+ < 1/16$ | $\text{error}_1 \le 0.020$ Ha, $\text{error}_2 \le 0.020$ Ha |
| **Physical Floor Gates** | $\text{tol}(x_{\max}) \ge 2^{-48}$ turns | $\delta = 2^{-128}$ Clopper-Pearson bound | Raw $\Lambda > 49.0$ Ha, $E_{\text{gap}} > 3.914898$ Ha |
| **Official Benchmark Shots** | $200,540,928$ shots ($64 \times 3,133,452$) | $102,400$ shots ($400 \times 256$) | $78,080$ shots ($64 \times 1,220$ addresses) |
| **Official Objective** | $\min Q \cdot T_{\text{equiv}}$ | $\min R(\epsilon_+) \cdot Q^2 \cdot T_{\text{mean}}$ | $\min \lambda_{\text{eff}} \cdot T_{\text{total}} \cdot Q_{\text{total}}$ |
| **Reference Cost ($C_{\text{ref}}$)** | $2,076,774.233715282$ | $24,439,463,583,672.93$ | $3,355,599,588.3155365$ |

---

## 2. Rejection Conditions and Failure Modes

### 2.1 Benchmark I (Invsqrt) Rejection Conditions
1. **Schema Violation:** Any register other than `x`, or `x` having fewer/more than 22 qubits, or containing non-qubit elements.
2. **Semantic Corruption:** Register `x` not restored bit-exact at the end of execution.
3. **Dirty Ancilla:** Any scratch qubit not returning to $|0\rangle$.
4. **Tolerance Exceeded:** Phase error exceeding $2^{-24}/\sqrt{x}$ on any simulated shot.
5. **Tolerance Exhaustion:** Remaining phase margin insufficient for rotation synthesis ($\epsilon \le 0$).

### 2.2 Benchmark II (DQI) Rejection Conditions
1. **Schema Violation:** Any register other than `S0`..`S69` (qubits) and `E0`..`E4094` (classical bits).
2. **Forbidden Gates:** Any $Z_{\text{POW}}$ gate detected in the circuit statistics.
3. **Syndrome Corruption:** Syndrome registers $S_i$ not restored to input values.
4. **Dirty Ancilla:** Any ancilla qubit failing to return to $|0\rangle$.
5. **Phase Failure:** Global phase not matching $(-1)^{\sum_j \text{popcount}(e_j \& M_j)}$.
6. **Clopper-Pearson Bound Failure:** Effective error rate $\epsilon_+ \ge 1/16$ at confidence $\delta = 2^{-128}$.
7. **Shot Count Misalignment:** Number of shots not a multiple of `batch_size = 256`.

### 2.3 Benchmark III (Chemistry) Rejection Conditions
1. **Qubit Cap Exceeded:** Any `ANGLE_k` circuit with $> 128$ qubits (`QUBIT_CAP`).
2. **Forbidden Gates:** Any $Z_{\text{POW}}$ gate detected in any circuit.
3. **Residual Gate Exceeded:** $\text{error}_1 > 0.020$ Ha or $\text{error}_2 > 0.020$ Ha.
4. **LCU Normalization Gate:** Raw $\Lambda \le 49.0$ Ha (`LAMBDA_FLOOR`).
5. **SOS Energy Gap Gate:** $E_{\text{gap}} \le 3.914898$ Ha (`E_GAP_FLOOR`).
6. **SOS Boundary Gate:** $E_{\text{gap}} \le 0$ or $E_{\text{gap}} \ge 2\Lambda$.
7. **Format Rejection:** Any pickle-formatted factorization file (`allow_pickle=False` mandatory).
8. **Word Inconsistency:** Different random seeds producing divergent recovered angle words.

---

## 3. Candidate Lifecycle and State Definitions

All optimization branches and candidates in Masterloop 26 must strictly adhere to the following six states:

```
[EXPERIMENTAL] 
      │
      ▼ (local unit/property tests pass)
[LOCALLY VERIFIED]
      │
      ▼ (passes full official verifier harness)
[OFFICIALLY VERIFIED]
      │
      ▼ (outperforms incumbent + verified provenance + reproducible package)
[PROMOTABLE]
      │
      ▼ (human promotion sign-off)
[INCUMBENT]
```

If any requirement fails at any stage:
$$\longrightarrow \mathbf{[REJECTED]}$$ with documented root cause in `discrepancy_register.md`.
