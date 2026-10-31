# GOOGLE QUANTUM AI: VERIFIABLE QUANTUM CIRCUIT COMPILATION
## Comprehensive Problem Specification, Mathematical Formulation & System Dossier

> **Prompt-Ready AI Briefing Document**  
> *Feed this document into any frontier LLM (Claude 3.5 Sonnet, GPT-4o, Gemini 1.5 Pro) to provide complete context, exact mathematical formulas, compiler contracts, verified baselines, disproven traps, and open optimization frontiers.*

---

# 1. Executive Overview & Competition Contract

### 1.1 The Competition Mandate
The **Google Quantum AI — Verifiable Quantum Circuit Compilation (VQCC)** competition challenges researchers to synthesize, optimize, and compile quantum circuits for fault-tolerant architectures evaluated by Google's official C++ Pauli-frame simulator `kickmix` (inside `github.com/quantumlib/Qualtran`).

### 1.2 The Scoring Metric
The competition evaluates submissions across three distinct quantum computational benchmarks. The overall score is the **geometric mean of three improvement ratios** relative to Google's fixed reference baseline costs:

$$\text{Score} = \left( R_{\text{invsqrt}} \times R_{\text{DQI}} \times R_{\text{chem}} \right)^{1/3} = \left( \frac{C_{\text{invsqrt}}^{\text{ref}}}{C_{\text{invsqrt}}^{\text{candidate}}} \times \frac{C_{\text{DQI}}^{\text{ref}}}{C_{\text{DQI}}^{\text{candidate}}} \times \frac{C_{\text{chem}}^{\text{ref}}}{C_{\text{chem}}^{\text{candidate}}} \right)^{1/3}$$

### 1.3 Fixed Reference Costs (Google Ground Truth)
* $C_{\text{invsqrt}}^{\text{ref}} = \mathbf{2{,}076{,}774.233715282}$
* $C_{\text{DQI}}^{\text{ref}} = \mathbf{24{,}439{,}463{,}583{,}672.93}$
* $C_{\text{chem}}^{\text{ref}} = \mathbf{3{,}355{,}599{,}588.3155365}$

### 1.4 Current State of the Art (October 2026)
* **World Leader (#1):** `26.76409` (Team *Breaking1800*, Total Product $\approx 19,173$)
* **Top 10 Threshold:** $\ge \mathbf{24.96}$
* **Our Team (`TuringIRL(akshit)`):** Rank **#377** / 1,731 teams (Top 21.8%)
  * Official Public Leaderboard Score: **`23.00043`** (Submission Ref `57812617`)
  * Local Verified Candidate (Slot 1): **`23.06081`** (Product $\approx 12,275$)
  * In-Flight Submission: Ref `57823923`

---

# 2. Benchmark I: Fixed-Point Inverse Square Root (`invsqrt`)

### 2.1 Problem Definition
Reversibly evaluate the phase function:
$$f(x) = \frac{\beta}{\sqrt{x}}$$
across 22-bit fixed-point positive integers $x \in [1, x_{\max}]$ where $x_{\max} = 3{,}133{,}452$ (problem instance $n_p = 10$).

### 2.2 Semantic Correctness Contract
1. **Input Register Restoration:** On every shot, the input register $x$ must be perfectly restored to its initial value ($0$ bit flips).
2. **Clean Ancilla Condition:** All scratch qubits must deterministically return to $|0\rangle$ at circuit termination.
3. **Phase Accuracy:** For every input $x$, the simulated global phase $\theta(x)$ must match the target within relative precision tolerance:
   $$|\theta(x) - \text{target}(x)| \le \text{tol}(x) = 2^{-24} \cdot \frac{\beta}{\sqrt{x}}$$
4. **No Uncompute Leaks:** $\text{min\_margin} = \min_{x} (\text{tol}(x) - |\text{error}(x)|) > 0$.

### 2.3 Cost Function
$$C_{\text{invsqrt}} = Q \times T_{\text{equiv}}$$
$$T_{\text{equiv}} = T_{\text{toffoli}} + \frac{T_{\text{base}} + N_{\text{rot}} \cdot \text{Cost}(R_z(\epsilon))}{T_{\text{per\_toffoli}}}$$
where:
* $Q$: Total allocated qubits (register width).
* $T_{\text{toffoli}}$: Mean Toffoli-like gates (`ccx`, `ccz`) executed per shot.
* $T_{\text{base}}$: Mean Clifford+T basis T-gates ($Z^{1/4}$).
* $N_{\text{rot}}$: Number of arbitrary non-Clifford single-qubit rotations ($Z_{\text{pow}}$ with hierarchy level $\ge 4$).
* $T_{\text{per\_toffoli}} = \mathbf{2.0}$ (2 T-gates per Toffoli).
* Rotation synthesis cost:
  $$\text{Cost}(R_z(\epsilon)) = 0.56 \log_2(1/\epsilon) + 5.3 \quad \text{T-gates}$$
  where $\epsilon = \frac{\pi \cdot \text{min\_margin}}{2^{64} \cdot N_{\text{rot}}}$.

### 2.4 Current Implementation vs. Top 10 Frontier
* **Our Champion (62Q):**
  * $Q = 62$, $T_{\text{toffoli}} = 1332.3$, $T_{\text{base}} = 6.9$, $N_{\text{rot}} = 41.0$, $\epsilon = 5.57 \times 10^{-9}$
  * $T_{\text{equiv}} = 1621.25 \implies \text{Cost} = 100{,}517.58 \implies \mathbf{R_{\text{invsqrt}} = 20.642\times}$
* **Top 10 Frontier (56Q – 58Q):**
  * $Q \to 56 - 58$ by folding the initial seed polynomial table into the first multiplier workspace.
  * Factoring phase synthesis into **1 single global rotation** ($N_{\text{rot}} = 1$), eliminating 40 rotation synthesis penalties.
  * Target $T_{\text{equiv}} \le 1380 \implies \mathbf{R_{\text{invsqrt}} \to 24.2\times - 25.0\times}$.

---

# 3. Benchmark II: Decoded Quantum Interferometry (`dqi`)

### 3.1 Problem Definition
Implement a syndrome decoder for a $(m=4095, n=70)$ Reed-Solomon code over the finite field $\text{GF}(2^{12})$ correcting up to $l = 35$ errors from $n = 70$ quantum syndrome registers $S_0, \dots, S_{69}$ (width 12 each, totaling 840 syndrome qubits).

### 3.2 Semantic Correctness Contract
1. **Syndrome Restoration:** Syndrome registers $S_0 \dots S_{69}$ must be restored bit-exact to their input values.
2. **Zero Dirty Scratch:** All scratch qubits must return to $|0\rangle$.
3. **Phase Kickback:** Global phase must be multiplied by:
   $$(-1)^{\sum_{j=0}^{m-1} \text{popcount}(e_j \ \& \ M_j)}$$
   where $e = \text{decode}(S)$ is the decoded error polynomial and $M_j$ are classical MBUC registers.
4. **Strict Gate Restrictions:** `Z_POW` gates are strictly **forbidden**. Only Clifford + Toffoli + `HMR` (Hadamard-Measure-Reset) are allowed.
5. **Acceptance Floor:** Under $N = 102{,}400$ shots, the one-sided Clopper-Pearson failure rate bound must satisfy:
   $$\epsilon^+ < \frac{1}{16} = 0.0625 \quad \text{at confidence } 1 - \delta \text{ with } \delta = 2^{-128}$$

### 3.3 Cost Function
$$C_{\text{DQI}} = R(\epsilon^+) \times \mathbf{Q^2} \times T_{\text{mean}}$$
where:
* $Q$: Peak active qubits (circuit width).
* $T_{\text{mean}}$: Mean Toffolis executed per shot (dynamic gates inside false condition blocks cost 0).
* $R(\epsilon^+)$: Clopper-Pearson repetition penalty:
  $$R(\epsilon) = \frac{\ln 2}{-\ln(1/2 + 2\sqrt{\epsilon})}$$
  * At $k=0$ failures in $N=102,400$ shots: $\epsilon^+ = 8.660587 \times 10^{-4} \implies \mathbf{R(0) = 1.19126046}$.
  * At $k=1$ failure: $\epsilon^+ = 9.104198 \times 10^{-4} \implies R(1) = 1.19673150$.
  * At $k=2$ failures: $\epsilon^+ = 9.488156 \times 10^{-4} \implies R(2) = 1.20138806$.

### 3.4 Current Implementation vs. Top 10 Frontier
* **Our Champion (889Q):**
  * $Q = 889$ ($Q^2 = 790{,}321$), $T_{\text{mean}} = 433{,}783.5$, $R(0) = 1.19126$
  * $\text{Cost} = 4.084 \times 10^{11} \implies \mathbf{R_{\text{DQI}} = 59.842\times}$
* **Top 10 Frontier ($Q \to 740$, $T \to 340\text{k}$):**
  * **Wire Recycling:** Reusing syndrome registers in-place during Chien search root-finding drops $Q$ from 889 to $\le 740$.
    * Because of $Q^2$, $(889 / 740)^2 = \mathbf{1.443\times}$ automatic cost reduction!
  * **42-Product Bilinear Tensor:** Compiling the rank-42 subfield multiplication tensor into the streamed decoder drops Toffolis from $433\text{k} \to 340\text{k}$ ($\mathbf{1.275\times}$ reduction).
  * Combined Frontier: $\text{Cost} \to 2.70 \times 10^{11} \implies \mathbf{R_{\text{DQI}} \to 86.0\times - 92.0\times}$!

---

# 4. Benchmark III: Electronic Structure Chemistry (`dfthcsos`)

### 4.1 Problem Definition
Low-energy simulation of the FeMoCo active nitrogenase catalytic site ($N = 76$ orbitals, $N = 113$ electrons) from `FeMoCo76o113e.fcidump`. Double factorizes the two-electron Coulomb tensor:
$$V_{pqrs} \approx \sum_{t=1}^M \zeta_{pq}^t \zeta_{rs}^t, \quad \zeta_{pq}^t = \sum_{\mu=1}^N \sum_{\nu=1}^N \chi_\mu(p) \chi_\nu(q) W_{\mu\nu}^t$$

### 4.2 Semantic Correctness Contract
1. **Chemical Accuracy:**
   * One-body error: $e_1 \le 20.0 \text{ mHa}$
   * Two-body error: $e_2 \le 20.0 \text{ mHa}$
   * Energy gap: $E_{\text{gap}} \in [3.8, 4.0] \text{ Ha}$
2. **Angle Circuit Rules:**
   * Maximum qubits per angle circuit: strictly $Q_{\text{angle}} \le 128$ (competition ceiling).
   * Gate restriction: strictly **0 T-gates** (Clifford+Toffoli only).
3. **Submission Package Structure:**
   * Directory `dfthcsos/` containing `submission.npz` (orbital transformation matrices $U, W$, tree edges) and Givens rotation circuits `angle_k_0.kmb` through `angle_k_{K-1}.kmb`.

### 4.3 Cost Function
$$C_{\text{chem}} = \lambda_{\text{eff}} \times Q_{\text{total}} \times T_{\text{total}}$$
where:
* $\lambda_{\text{eff}}$: Effective 1-norm of the block-encoded Hamiltonian after truncation.
* $Q_{\text{total}}$: Persistent orbital qubits + QROM control registers.
* $T_{\text{total}}$: Total Toffoli cost across state preparation and Givens angle rotations.

### 4.4 Current Implementation vs. Top 10 Frontier
* **Our Champion ($R=8$):**
  * $R=8, B=143, C=60, \text{brot}=16$, 16 angle circuits ($J=5$, 4-address pebble QROM).
  * $Q = 430, T = 16{,}266, \lambda_{\text{eff}} = 48.3236 \implies \text{Cost} = 337{,}993{,}822.4 \implies \mathbf{R_{\text{chem}} = 9.928\times}$.
* **Top 10 Frontier ($J=7 / 8$ Packed Pebble Mode):**
  * Maximizing batch size to $J=7$ ($Q=124 \le 126$) reduces angle circuits from 16 to 11.
  * Table-native Algebraic Normal Form (ANF) monomial factoring cuts QROM data loading Toffolis.
  * Target $T \le 14{,}000 \implies \mathbf{R_{\text{chem}} \to 11.2\times - 11.8\times}$.

---

# 5. Critical Traps & Negative Results (Do NOT Repeat)

| Myth / Disproven Hypothesis | Why It Fails (The Ground Truth Physics & Math) | Correct Architectural Reality |
|---|---|---|
| **"Unpenalized DQI score is 25.43"** | Omits the mandatory Clopper-Pearson repetition penalty $R(\epsilon^+)$. At $\delta = 2^{-128}$ and $N=102,400$, $R(0) = 1.19126$. $R=1.0$ is physically impossible. | Score with $R(0)=1.19126$ is $\mathbf{23.06}$. |
| **"QPE saves an additional 225k Toffolis"** | The 889Q circuit *already includes* QPE in `replay_erase.py` and `synth_stream.py`. Attempting to erase forward operands where control wires are modified corrupts syndrome evaluation. | $433\text{k}$ Toffolis is the real count with QPE already active. |
| **"Continuous $R=10$ Chem improves score"** | While $R=10$ slightly drops continuous $\lambda_{\text{eff}}$ ($48.32 \to 48.03$), the address explosion ($A=1366$ vs $1220$) forces the compiler from 4-address pebble mode into 2-address linear mode, increasing cost by $+65.7\%$! | **$R=8$ pebble mode is strictly superior ($9.928\times$ vs $5.993\times$)**. |
| **"Invsqrt $T_{\text{per\_toffoli}} = 4.0$"** | The official verifier code explicitly sets `T_PER_TOFFOLI = 2.0`. | Always divide base T-gates by $2.0$. |
| **"RiBM is ready for production deployment"** | RiBM is proven classically over $GF(2^{12})$, but quantum reversible registers for $B(x)$, $\gamma$, and Chien/Forney root evaluation are not yet compiled. Deploying it now causes semantic failure. | Keep Proos-Zalka champion in production; use RiBM as classical baseline. |

---

# 6. The Actionable AI Roadmap to World Rank #1 ($26.76+$)

To beat the current world record (`26.76409`), an AI agent must execute three specific engineering milestones:

```
TARGET COMPOSITE METRICS FOR WORLD RANK #1:
┌──────────────┬──────────────────┬─────────────────┬────────────────────┐
│ Benchmark    │ Current Champion │ Target Metric   │ Architectural Path │
├──────────────┼──────────────────┼─────────────────┼────────────────────┤
│ Invsqrt      │ 20.64x (62Q)     │ 24.20x (56Q)    │ 1-rotation seed tab│
│ DQI          │ 59.84x (889Q)    │ 86.50x (740Q)   │ In-place wire reuse│
│ Chemistry    │ 9.93x (R=8, J=5) │ 11.20x (J=7)    │ ANF pebble batching│
├──────────────┼──────────────────┼─────────────────┼────────────────────┤
│ COMPOSITE GM │ 23.00 – 23.06    │ 28.62 (RANK #1!)│ Improvement: +24%  │
└──────────────┴──────────────────┴─────────────────┴────────────────────┘
```

### Directive for the Next AI Agent:
1. **Focus 80% of effort on DQI Qubit Reduction ($Q \to 740$):**
   Open [`extracted_dqi/blocks/dqi/team-1028-narrow240/source/exp/r-main/narrow240/decode_retimed.py`](file:///C:/Users/noobg/.gemini/antigravity-ide/scratch/berlioz/extracted_dqi/blocks/dqi/team-1028-narrow240/source/exp/r-main/narrow240/decode_retimed.py). Analyze where syndrome registers $S_0 \dots S_{69}$ become idle after evaluator calculation, and reuse those exact wire indices for Chien search instead of allocating 49 fresh scratch qubits.
2. **Compile `tower42.py` into the Streamed Decoder:**
   Replace the 63-AND subfield multipliers in [`final_decoder/`](file:///C:/Users/noobg/.gemini/antigravity-ide/scratch/berlioz/extracted_dqi/blocks/dqi/team-1028-narrow240/source/playbook/kit/decoder/final_decoder/) with the rank-42 bilinear tensor from [`src/dqi/tower42.py`](file:///C:/Users/noobg/.gemini/antigravity-ide/scratch/berlioz/src/dqi/tower42.py).
3. **Execute Clean Verification:**
   Run `python src/verify_portfolio.py submission.zip --mode quick --dqi-shots 2048` before staging any archive.
