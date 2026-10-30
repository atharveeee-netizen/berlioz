# The Berlioz Research Journey: Architectural Chronicle & Engineering Log
**Competition:** Google Quantum AI — Verifiable Quantum Circuit Compilation (Kaggle)  
**Target:** Composite Geometric Mean Score 50.0 ($\text{Improvement Product} = 125{,}000$)  
**Current Status:** **Rank #220 / 1,677 Teams (Top 13.1%)** | **Verified Live Score: `22.99562`**  
**Repository:** [https://github.com/atharveeee-netizen/berlioz](https://github.com/atharveeee-netizen/berlioz)  
**Date:** October 30, 2026  

---

## 1. Executive Overview & The "Score 50" Horizon

The **Google Quantum AI Verifiable Quantum Circuit Compilation (VQCC)** challenge ($150,000 prize pool, 1,677 global teams) evaluates quantum circuit synthesis across three fault-tolerant computational benchmarks:
1. **Benchmark I (`invsqrt`)**: Fixed-point reversible reciprocal square root $y \approx 1/\sqrt{x}$ over $x \in [1, 3{,}133{,}452]$ with 24-bit precision, tested exhaustively across 200,540,928 shots.
2. **Benchmark II (`dqi`)**: Decoded Quantum Interferometry syndrome decoder for an $\text{RS}(4095, 4025)$ code in $\text{GF}(2^{12})$, evaluated across 102,400 shots drawn from realistic error weights.
3. **Benchmark III (`dfthcsos`)**: Block-encoding and low-energy state preparation of the FeMoCo nitrogenase catalytic active site (76 orbitals, 113 electrons) via Double-Factorized Tensor Hypercontraction (DF-THC).

The competition objective is the geometric mean of improvement ratios relative to Google's official unoptimized references:
$$\text{Score} = \left(\frac{\text{Ref}_{\text{invsqrt}}}{\text{Cost}_{\text{invsqrt}}} \times \frac{\text{Ref}_{\text{dqi}}}{\text{Cost}_{\text{dqi}}} \times \frac{\text{Ref}_{\text{dfthcsos}}}{\text{Cost}_{\text{dfthcsos}}}\right)^{1/3}$$

Where fixed baselines are:
* $\text{Ref}_{\text{invsqrt}} = \mathbf{2{,}076{,}774.2337}$
* $\text{Ref}_{\text{dqi}} = \mathbf{24{,}439{,}463{,}583{,}672.93}$
* $\text{Ref}_{\text{dfthcsos}} = \mathbf{3{,}355{,}599{,}588.3155}$

Our North Star is not incremental leaderboard camping; our mission is capturing the **Composite Geometric Mean Score of 50.0**:
$$\text{Product} = \text{Ratio}_{\text{invsqrt}} \times \text{Ratio}_{\text{dqi}} \times \text{Ratio}_{\text{dfthcsos}} = 50^3 = \mathbf{125{,}000}$$
* Target $\text{Ratio}_{\text{invsqrt}} = \mathbf{25.0\times}$
* Target $\text{Ratio}_{\text{dqi}} = \mathbf{200.0\times}$
* Target $\text{Ratio}_{\text{dfthcsos}} = \mathbf{25.0\times}$

---

## 2. Phase 1: Pre-Flight Audit & Ground Truth Discovery

Before writing any speculative code, we instituted a strict **Truth Gate** by auditing the official shipped verifiers in `kickmix` and the primary literature:
* arXiv:2610.23832: Khattar, Rubin, Gidney, Low, Babbush (Google Quantum AI VQCC paper).
* arXiv:2510.10967: Maslov, Jordan et al. (DQI syndrome decoding architecture).
* arXiv:2610.22367: Gu, Kemeny, Yelin, Lukin (Harvard/Anthropic Kickmix Arena study).
* PRX Quantum 2, 030305: Lee, Berry, Babbush et al. (DF-THC FeMoCo simulation).

### Truth Gate Discoveries & Corrections
1. **Debunked DQI Terminology**: Prior community documentation claimed DQI meant "Data-Qubit-Interleaved Surface Codes". Ground-truth inspection of the Maslov-Jordan reference confirmed DQI stands for **Decoded Quantum Interferometry** (Reed-Solomon decoding bottleneck).
2. **Reconciled Cost Models**:
   * *Invsqrt:* Corrected the formula from heuristic linear bounds to the exact scorer equation:
     $$\text{Cost} = Q \times (\text{Toffolis} + T_{\text{total}}/4)$$
     Where rotation synthesis adds $T = 0.56 \log_2(1/\epsilon) + 5.3$ T-gates based on the worst-case phase error margin $\text{min\_margin}$.
   * *DQI:* Reconciled the Clopper-Pearson error penalty $R(\epsilon^+)$ across 102,400 shots with $Q^2$ live-wire scaling.
   * *Chemistry:* Reconciled the 128-qubit hard cap on angle circuits ($Q_{\text{angle}} \le 128$) and strict chemical accuracy bounds ($e_1, e_2 \le 20\text{ mHa}$).
3. **"Where the Cost Lives" Profiling**:
   * *Invsqrt:* $81.8\%$ in seed table polynomial evaluation, $18.2\%$ in phase rotations.
   * *DQI:* $>85\%$ of all executed Toffolis occur in EEA Galois field multiplications ($43.5\%$ forward, $43.5\%$ adjoint uncompute).
   * *Chemistry:* $60.6\%$ in state preparation floor, $25.5\%$ in QROM angle loads, $13.8\%$ in Givens rotations.

---

## 3. Phase 2: What We Did & The 10 Novel Blocks

Rather than running generic LLM prompt loops against the verifier, we executed the rigorous **Block Protocol** (Research $\to$ Hypothesis $\to$ Falsifier $\to$ Build $\to$ Verify $\to$ Keep/Kill):

```
       [Research & Literature]
                  │
                  ▼
         [Hypothesis Card]
                  │
                  ▼
         [Cheapest Falsifier] ──(Failed)──> [KILL & Log Lessons]
                  │ (Passed)
                  ▼
         [Parametric Builder]
                  │
                  ▼
      [Triple-Lock Verification]
   (3 Salts + Recomp + Unit Tests)
                  │
                  ▼
        [KEEP & Commit to Ledger]
```

### Block 1 — Price-Book Arbitrage
* **Thesis:** Scorer instruction pricing contains asymmetries between static circuit declarations and dynamic execution paths.
* **The Discovery:** In Kickmix simulation, instructions enclosed within `PUSH_CONDITION if b` evaluate **dynamically per shot**. When $b=0$, the operation contributes **0 Toffolis** to `sim.operation_statistics().num_toffoli_like`.
* **Empirical Proof:** Built `tests/test_pricebook.py` and exported `results/pricebook.json`. Proved that gating fix-ups behind condition bits scales by expectation $\mathbb{E}[b] \times \text{Cost}$, opening the door to speculative branch pruning.
* **Status:** **KEEP** (Documented in `research/block01_pricebook_arbitrage.md`).

### Block 3 — Quadratic-Phase Erasure (DQI)
* **Thesis:** Standard reversible algorithms waste $>40\%$ of their Toffoli budget uncomputing intermediate multiplication products backwards.
* **The Mathematical Breakthrough:**
  If a scratch wire $y$ is a degree-$\le 2$ Boolean function in surviving wires $x$:
  $$y = \sum_{(i,j) \in E} x_i x_j \pmod 2$$
  Measuring $y$ in the X-basis (`HMR(y -> b)`) projects $y$ to $|0\rangle$ and kicks a phase $(-1)^{b \cdot y}$. This phase is **biquadratic** and can be neutralized with **zero Toffolis** using a conditional Clifford $CZ$ network:
  $$\prod_{(i,j) \in E} CZ(x_i, x_j)^{\text{if } b}$$
* **Empirical Proof:** Built `src/dqi/quadratic_phase_erase.py`. Simulated across all computational basis states in `tests/test_quadratic_phase_erase.py`; verified 100% restoration to $|0\rangle$ with zero phase kickback and 0 uncompute Toffolis.
* **Status:** **KEEP** (Documented in `research/block03_quadratic_phase_erasure.md`).

### Block 6 — Algebra-First Decoder Core (DQI)
* **Thesis:** Standard 63-AND polynomial multiplication in $\text{GF}(2^{12})$ is inefficient.
* **The Breakthrough:**
  Representing $\text{GF}(2^{12})$ as an extension tower over $\text{GF}(8)$:
  $$\text{GF}(2^{12}) \cong \text{GF}(8)[v]/(v^4 + v + 1), \quad \text{GF}(8) = \text{GF}(2)[u]/(u^3 + u + 1)$$
  Degree-3 products in $v$ evaluate at 6 finite points in $\text{GF}(8)$ plus $\infty$ ($7$ products in $\text{GF}(8)$). Each product evaluates via binary Karatsuba into 6 binary products ($7 \times 6 = 42$ bilinear products).
  Furthermore, Frobenius squarings $x \mapsto x^2$ evaluate as purely linear CNOT networks (**0 Toffolis**).
* **Empirical Proof:** Unit test `tests/test_arithmetic_tensor.py` confirmed bit-exact agreement across all 144 basis products and 500 randomized trials, cutting Toffolis by **21.18%**.
* **Status:** **KEEP** (Documented in `research/block06_algebra_first_decoder.md`).

### Blocks 8 & 9 — Chemistry Co-Design, Half-Open Gauge & $J=7$ Batching
* **Thesis:** QROM angle circuits can be compressed by exploiting Givens gauge freedom and maximal batching under the 128-qubit cap.
* **The Breakthrough:**
  1. *Signed Half-Open Gauge:* Enforcing $\text{bit}(7) == \text{bit}(6)$ across all $102,450$ words in `fact/dfthc_r10_b129_c60_brot8.npz` eliminates the sign bit entirely from QROM loading.
  2. *Optimal $J=7$ Batching:* Analytical envelope for address size $A=2$:
     $$Q(J) = 20 + 15J \implies Q(7) = 125 \le 126 \le 128$$
     Batching $J=7$ reduces the angle circuit count from 15 to 11 (**26.7% reduction**).
* **Empirical Proof:** Verified via `tests/test_portfolio_coupling.py` and official chemical accuracy tests ($e_1 = 19.0\text{ mHa} \le 20\text{ mHa}$, $e_2 = 19.7\text{ mHa} \le 20\text{ mHa}$, $\lambda_{\text{eff}} = 48.0311$).
* **Status:** **KEEP** (Documented in `research/block08_table_content_codesign.md`).

---

## 4. Phase 3: Leaderboard Standing & Submission Milestones

### Submission Chronicle
| Submission ID | Timestamp | Team Name | Description | Status | Public Score |
| :---: | :---: | :---: | :--- | :---: | :---: |
| `57569888` | Oct 23, 2026 | `TuringIRL(akshit)` | Initial QROM Tower42 probe | Graded | `5.75763` |
| `57589367` | Oct 24, 2026 | `TuringIRL(akshit)` | Rotation calibration baseline | Graded | `5.78629` |
| `57711436` | Oct 27, 2026 | `TuringIRL(akshit)` | Narrowed 877Q DQI + progressive R10 | Graded | `21.87976` |
| `57800637` | Oct 30, 2026 (14:47 IST) | `TuringIRL(akshit)` | Syzygy Vault 22.99: 62Q Invsqrt + 889Q DQI + B143/C60 Chem | **Graded** | **`22.99562`** |

### Current Standing
* **Public Rank:** **#220** out of **1,677 teams** (**Top 13.12%**)
* **Submissions Used Today:** 1
* **Submissions Remaining Today:** 4 (out of 5 daily allowance)

---

## 5. Phase 4: Stealth Hardening & GitHub Synchronization

To prevent competitors from discovering our mathematical formulations or cloning our circuit pipelines:
1. **Repository Renamed:** Renamed from identifiable `TuringIRL-quantum` $\to$ **[`berlioz`](https://github.com/atharveeee-netizen/berlioz)**.
2. **Stealth Metadata:** Replaced competition descriptions with:
   > *"Berlioz: High-performance discrete algebra and symphonic state synthesis"*
3. **Comprehensive Test Suite:** 15/15 unit tests pass locally in 4.04s.
4. **Git Synchronized:** All changes committed (`dec003f`) and pushed directly to `origin/master`.

---

## 6. Master Roadmap: The Path from 22.99 to Score 50.0

```
  Current (22.99)               Milestone 1 (35.0)              Score 50.0 Target
┌──────────────────┐           ┌──────────────────┐           ┌──────────────────┐
│ Invsqrt:  20.56x │           │ Invsqrt:  22.50x │           │ Invsqrt:  25.00x │
│ DQI:      59.57x │   ───>    │ DQI:      95.00x │   ───>    │ DQI:     200.00x │
│ Chem:      9.93x │           │ Chem:     15.00x │           │ Chem:     25.00x │
└──────────────────┘           └──────────────────┘           └──────────────────┘
```

### Next Levers in Execution:
1. **DQI Linear-Scan Wire Compaction ($Q \to 520$)**:
   Because DQI cost scales quadratically ($Q^2$), compressing active wires from 889 to 520 delivers an immediate **$2.92\times$ cost reduction** independently of gate count.
2. **Speculative RS Decoder Branch Pruning (Block 5)**:
   Exploiting low error weights ($k \ll 35$) while paying a negligible Clopper-Pearson repetition penalty $R(\epsilon^+)$.
3. **Higher-Order L-BFGS Chemical Refits ($R=10 \to R=7$) (Block 9)**:
   Reducing $\lambda_{\text{eff}}$ from $48.03 \to \le 42.0$ via Riemannian Cayley optimization.
