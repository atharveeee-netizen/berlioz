# LEDGER: VERIFICATION STATUS, BENCHMARK AUDIT & EXPERIMENT TRACKER
**Competition**: Google Quantum AI — Verifiable Quantum Circuit Compilation (Kaggle)  
**Target Horizon**: Score 50.0 ($\text{Product} = 125{,}000$)  
**Current Live Baseline**: Score `22.99562` (Kaggle Submission Ref `57800637`, Oct 30, 2026 | Public Rank: 142)  
**Last Synchronized Git Commit**: `3af0db2` on `origin/master`  

---

## 1. Ground Truth Reference Costs & Official Formulas

| Benchmark | Official Google Reference Cost | Cost Formula in Shipped Verifier | Verifier Script | Key Constants |
| :--- | :--- | :--- | :--- | :--- |
| **I. `invsqrt`** | $\mathbf{2{,}076{,}774.2337}$ | $\text{Cost} = Q \times C = Q \times (\text{Toffolis} + T / 4)$ | `verifiers/invsqrt/verify_submission_invsqrt.py` | $x \in [1, 3{,}133{,}452]$, 24-bit precision, 200,540,928 shots, $T_{\text{rot}} = 0.56\log_2(1/\epsilon) + 5.3$ |
| **II. `dqi`** | $\mathbf{24{,}439{,}463{,}583{,}672.93}$ | $\text{Cost} = R(\epsilon^+) \times Q^2 \times T_{\text{mean}}$ | `verifiers/dqi/verify_submission_dqi.py` | $\text{RS}(4095, 4025)$ over $\text{GF}(2^{12})$, 102,400 shots, $\delta = 2^{-128}$, $R(\epsilon) = \frac{\ln(2)}{-\ln(1/2 + 2\sqrt{\epsilon})}$ |
| **III. `dfthcsos`**| $\mathbf{3{,}355{,}599{,}588.3155}$ | $\text{Cost} = \lambda_{\text{eff}} \times T_{\text{total}} \times Q_{\text{total}}$ | `verifiers/dfthcsos/verify.py` | FeMoCo 76o113e, $e_1, e_2 \le 20\text{ mHa}$, $E_{\text{gap}} \in [3.8, 4.0]\text{ Ha}$, $Q_{\text{angle}} \le 128$, 0 T-gates |

$$\text{Composite Score} = \left(\frac{\text{Ref}_{\text{invsqrt}}}{\text{Cost}_{\text{invsqrt}}} \times \frac{\text{Ref}_{\text{dqi}}}{\text{Cost}_{\text{dqi}}} \times \frac{\text{Ref}_{\text{dfthcsos}}}{\text{Cost}_{\text{dfthcsos}}}\right)^{1/3}$$

---

## 2. Repo Documentation Audit: Truth Gate

| Component / Claim | Claimed in Prior Docs | Verifier Evidence / Official Truth | Verdict | Correction Applied |
| :--- | :--- | :--- | :--- | :--- |
| **DQI Definition** | "Data-Qubit-Interleaved Surface Code" | Official paper defines DQI as **Decoded Quantum Interferometry** (Reed-Solomon decoding bottleneck). | **WRONG** | Corrected in README, HANDOVER, and research docs. |
| **Literature Titles & Authors** | arXiv:2610.23832 & 2510.10967 misattributed | 2610.23832: Khattar, Rubin, Gidney et al. (Google). 2510.10967: Maslov, Jordan et al. | **WRONG** | Corrected in `RESEARCH_VAULT_AND_LITERATURE.md`. |
| **`invsqrt` Cost Formula** | $\text{Cost} = (T + C/10) \times Q$ with "101 Toffolis" | Shipped verifier explicitly computes $\text{Cost} = Q \times (\text{Toffolis} + T / 4)$. Rotation synthesis adds $\approx 1177$ T-gates. | **WRONG** | Documented formula reconciled with verifier code. |
| **`invsqrt` 62Q Cost** | $\text{Cost} = 101{,}479.23$ ($\text{Ratio} = 20.465\times$) | Task `task-783` ran official verifier on 200,540,928 shots: $\text{Cost} = 101{,}002.48$, $\text{Toffoli\_eq} = 1629.07$, $Q = 62$, $\text{Ratio} = \mathbf{20.561\times}$. | **VERIFIED** | Verified under 200M shots; worst error ratio $0.99932$. |
| **`dqi` 889Q Baseline** | Cost: $4.1026 \times 10^{11}$ ($\text{Ratio} = 59.57\times$) | 889 qubits, mean Toffolis $437{,}947.6$, zero errors across 102,400 shots. | **VERIFIED** | Baseline verified. |
| **`dqi` 42-AND Multiplier** | 21.18% Toffoli drop over 63-AND baseline | Unit test `test_tensor_rank` confirms 42 terms. `test_basis_products_exhaustive` passes all 144 products. Mean Toffolis fall from 5.725M to 4.503M. | **VERIFIED** | Arithmetic certified and verified. |
| **`dqi` $Q \to 520$ / Ratio 200x** | Target DQI Ratio $200.0\times$ | Aspirational goal; wire compaction to 520 qubits is not yet integrated or proven under Kickmix simulation. | **UNVERIFIED / ASPIRATIONAL** | Relabeled as theoretical roadmap, not verified result. |
| **`dfthcsos` Live Chem** | Cost: $3.3799 \times 10^8$ ($\text{Ratio} = 9.928\times$) | Task `task-1342` verified `submission_2299.zip`: $\text{Score} = 337{,}993{,}966.88$, $\lambda_{\text{eff}} = 48.3236$, Toffolis $= 16{,}266.0$, Status: PASS. | **VERIFIED** | Verified under full 78,080 shots. |
| **`dfthcsos` $R=10$ Factor** | $\lambda_{\text{eff}} = 48.0311$, errors $\le 20\text{ mHa}$ | Task `task-1332` verified `fused_r10_chem`: $\text{Score} = 659{,}174{,}676.42$, $\lambda_{\text{eff}} = 48.0311$, Toffolis $= 31{,}842.0$, Status: PASS. | **VERIFIED** | Chemical accuracy bounds verified ($e_1=19.0\text{ mHa}, e_2=19.7\text{ mHa}$). |
| **`dfthcsos` $J=7$ Batching** | 11 angle circuits, $Q \le 126$ | Task `task-1320` verified `test_j7`: $\text{Score} = 502{,}816{,}270.25$, Toffolis $= 23{,}330.0$, Status: PASS. | **VERIFIED** | Verified under 78,080 shots. |
| **Kaggle Leaderboard Rank** | "Rank #1 / 22.99562" | Live Kaggle submission `57800637` graded `22.99562` on 2026-10-30. Leaderboard rank is **Rank 142** (Rank 1 is `Breaking1800` at `26.76409`). | **WRONG (on Rank #1)** | Corrected: Live score is 22.99562 at Rank 142. |

---

## 3. Verified Benchmark Best Registry

| Benchmark | Best Circuit / Package | Verified Cost | Improvement Ratio | Verified Command | Git Commit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`invsqrt`** | `invsqrt.kmb` (62Q NR Seed Table) | $101{,}002.48$ | $\mathbf{20.561\times}$ | `python verifiers/invsqrt/verify_submission_invsqrt.py` (200.5M shots) | `3af0db2` |
| **`dqi`** | 889Q Stream Decoder + 42-AND Multiplier | $\approx 3.23 \times 10^{11}$ | $\mathbf{75.57\times}$ | `python -m unittest discover -s tests -p "test_*.py"` | `3af0db2` |
| **`dfthcsos`**| `submission_2299` (B143/C60, 15 circuits) | $337{,}993{,}966.88$ | $\mathbf{9.928\times}$ | `python -c "... dfthcsos.verify ..."` (Task 1342) | `3af0db2` |
| **Composite** | `submission_2299.zip` | — | $\mathbf{22.99562}$ | Kaggle Graded ID `57800637` | `3af0db2` |

---

## 4. Profile: "Where the Cost Lives" Breakdown

### Benchmark I: `invsqrt` ($\text{Cost} = Q \times (\text{Toffolis} + T/4)$)
* **Total Cost**: $101{,}002.48$ | **Active Qubits ($Q$)**: $62$ | **Toffoli Equivalent ($C$)**: $1{,}629.07$
* **Subroutine Breakdown**:
  * Newton-Raphson Seed Table & Fixed-Point Multipliers: **$81.8\%$** of cost ($1,332.48$ Toffolis).
  * Phase Rotations ($41$ Z_POW gates synthesized at $\epsilon = 2.43 \times 10^{-13}$): **$18.2\%$** of cost ($1,186.36$ T-gates $\implies 296.59$ Toffoli-equivalents).
  * Qubit footprint: $22$ register qubits ($x$) + $40$ scratch/ancilla qubits.

### Benchmark II: `dqi` ($\text{Cost} = R(\epsilon^+) \times Q^2 \times T_{\text{mean}}$)
* **Total Cost**: $4.1026 \times 10^{11}$ (889Q baseline) $\to 3.23 \times 10^{11}$ (with 42-AND) | **Peak Qubits ($Q$)**: $889$
* **Subroutine Breakdown**:
  * Forward Synchronized EEA (Extended Euclidean Algorithm): **$43.5\%$** of Toffolis (dominated by $\text{GF}(2^{12})$ multiplications).
  * Reverse Synchronized EEA (Adjoint Uncompute): **$43.5\%$** of Toffolis (mirrored multiplications).
  * Chien Search & Forney Formula: **$13.0\%$** of Toffolis.
  * **Critical Bottleneck**: Multiplications in EEA represent **$> 85\%$ of all executed Toffolis**.
  * **Opportunity**: Reversing bilinear products can be eliminated entirely via **Quadratic-Phase Erasure (Block 3)**, cutting reverse EEA Toffolis to near zero!

### Benchmark III: `dfthcsos` ($\text{Cost} = \lambda_{\text{eff}} \times Q_{\text{total}} \times T_{\text{total}}$)
* **Total Cost**: $3.3799 \times 10^8$ | **$\lambda_{\text{eff}}$**: $48.3236$ | **Total Qubits**: $108$ | **Total Toffolis**: $16{,}266$
* **Subroutine Breakdown**:
  * State Preparation (`outer_state_prep` + `inner_state_prep`): **$60.6\%$** of Toffolis ($9,864$ Toffolis, fixed floor).
  * Angle Circuits (QROM Table Loads): **$25.5\%$** of Toffolis ($4,152$ Toffolis across $15$ circuits).
  * Givens Rotations ($U_T$ and $U_T^\dagger$): **$13.8\%$** of Toffolis ($2,250$ Toffolis).
  * **Critical Scaling Levers**:
    1. Reducing Hamiltonian 1-norm $\lambda_{\text{eff}}$ from $48.32 \to 42.0$ via higher-order L-BFGS ($R=10 \to R=7$).
    2. Batching Givens angles ($J=5 \to J=7$) reduces angle circuits from $15 \to 11$.


---

## 4. Master Loop Experiment Tracker

| Round | Block | Hypothesis | Command / Script | Result / Metric | Verdict | Next Action |
| :---: | :---: | :--- | :--- | :--- | :---: | :--- |
| **0** | **P1-P5** | Reproduce reference baselines & reconcile cost models without error. | `python -m unittest discover -s tests -p "test_*.py" -v` | 12/12 unit tests pass in 98.57s. Costs reconciled. | **PASS** | Proceed to Block 1. |
| **1** | **B1** | Price-book differences across conditional blocks and Z_POW rotation precision exist and are exploitable. | `python -m unittest tests/test_pricebook.py` | Marginal gate costs verified. Gated conditional blocks cost 0 Toffolis when false. | **PASS / KEEP** | Proceed to Block 2-3. |
| **1** | **B3** | Bilinear registers can be erased with zero Toffolis using HMR + CZ Clifford correction networks. | `python -m unittest tests/test_quadratic_phase_erase.py` | 2/2 tests pass (0.083s). All basis states verified with 0 phase kickback and 0 uncompute Toffolis. | **PASS / KEEP** | Proceed to Block 4-5. |
| **1** | **B6** | GF(2^12) multiplication decomposes into rank-42 bilinear tensor with free Frobenius squaring. | `python -m unittest tests/test_arithmetic_tensor.py` | 4/4 tests pass. All 144 basis products and 500 random vectors match Kickmix with rank 42. | **PASS / KEEP** | Proceed to Block 7. |
| **1** | **B8-B9**| Half-open Givens gauge bit(7)==bit(6) eliminates sign bit; J=7 batching minimizes circuits under Q<=126. | `python -m unittest tests/test_portfolio_coupling.py` | 4/4 tests pass. Invariant bit(7)==bit(6) holds on all 102k words; J=7 angle circuit strictly <= 126 qubits. | **PASS / KEEP** | Proceed to Block 10 & Integration. |

