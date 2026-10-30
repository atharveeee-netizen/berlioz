# Berlioz: Discrete Algebraic Quantum Circuit Synthesis & Verification
### Google Quantum AI — Verifiable Quantum Circuit Compilation (Kaggle)

<p align="center">
  <img src="https://img.shields.io/badge/Google_Quantum_AI-Competition-4285F4?style=for-the-badge&logo=google" alt="Google Quantum AI">
  <img src="https://img.shields.io/badge/Active_Team-TuringIRL(akshit)-blueviolet?style=for-the-badge&logo=kaggle" alt="TuringIRL">
  <img src="https://img.shields.io/badge/Leaderboard_Rank-220_%2F_1677_(Top_13%25)-success?style=for-the-badge" alt="Rank 220">
  <img src="https://img.shields.io/badge/Live_Verified_Score-22.99562-success?style=for-the-badge" alt="Verified Score">
  <img src="https://img.shields.io/badge/Grand_Target-Score_50.0-critical?style=for-the-badge" alt="Grand Target">
</p>

**Berlioz** is an advanced algebraic quantum circuit compilation engine designed for fault-tolerant Clifford+Toffoli architectures evaluated by the official C++ Pauli simulator `kickmix`.

Our mission targets the grand theoretical frontier: **capturing a composite Geometric Mean Score of 50.0** (Improvement Product $= 50^3 = \mathbf{125{,}000}$) across all three competition benchmarks.

---

## 🧭 Essential Documentation & Research Chronicle

* **[`JOURNEY.md`](JOURNEY.md)**: **The Complete Research Chronicle**. Detailed narrative of what we approached, what we did, how we derived the mathematics, our verification milestones, and the roadmap to Score 50.
* **[`LEDGER.md`](LEDGER.md)**: **The Empirical Truth Gate & Master Loop Tracker**. Contains every verified benchmark result, cost breakdowns, and unit test evidence.
* **[`research/`](research/)**: Research novelty cards (Block 1 Price-Book Arbitrage, Block 3 Quadratic-Phase Erasure, Block 6 Algebra-First Decoder, Block 8-9 Chemistry Co-Design).
* **[`HANDOVER.md`](HANDOVER.md)**: Deep technical specifications and algorithmic dossiers for collaborators.

---

## 🏆 Current Standing & Score Formulation

$$\text{Score} = \left(\text{Ratio}_{\text{invsqrt}} \times \text{Ratio}_{\text{dqi}} \times \text{Ratio}_{\text{dfthcsos}}\right)^{1/3} = \mathbf{22.99562}$$

* **Official Public Rank:** **#220** / 1,677 Teams (**Top 13.12%**)
* **Current Live Graded Submission:** `57800637` (Oct 30, 2026)

| Benchmark | Google Reference | Active Verified Cost | Improvement Ratio | Core Algorithmic Lever |
| :--- | :--- | :--- | :--- | :--- |
| **`invsqrt`** | $2{,}076{,}774.23$ | $101{,}002.48$ | **$20.561\times$** | 62-Qubit Newton-Raphson Seed Table (Verified on 200.5M shots) |
| **`dqi`** | $24{,}439{,}463{,}583{,}673$ | $4.1026 \times 10^{11}$ | **$59.57\times$** | 889Q Stream Decoder + 42-AND Bilinear Tensor ($\to 75.57\times$) |
| **`dfthcsos`**| $3{,}355{,}599{,}588.32$ | $3.3799 \times 10^8$ | **$9.928\times$** | $R=10$ Factorization ($\lambda_{\text{eff}} = 48.0311$) + $J=7$ Batching |
| **Product** | — | — | **$\text{GM} = \mathbf{22.99562}$** | **Product $= 12{,}158$** |

---

## 🔬 Core Breakthroughs Implemented in Berlioz

1. **Price-Book Arbitrage (`tests/test_pricebook.py`)**:
   Proved that gates enclosed in `PUSH_CONDITION if b` blocks execute dynamically per shot. Gates on false branches cost **0 Toffolis**.
2. **Quadratic-Phase Erasure (`src/dqi/quadratic_phase_erase.py`)**:
   Eliminated 100% of reverse multiplication Toffolis during uncompute by neutralizing degree-$\le 2$ kickback phases using conditional Clifford $CZ$ networks for **0 Toffolis**.
3. **42-Product Bilinear Tensor in $\text{GF}(2^{12})$ (`src/dqi/tower42.py`)**:
   Decomposed Galois field multiplication into a subfield tower $\text{GF}(8)[v]/(v^4+v+1)$ with 42 bilinear products and free Frobenius squarings.
4. **Signed Half-Open Givens Gauge & $J=7$ Batching (`fact/`, `src/chem/`)**:
   Enforced `bit(7) == bit(6)` to eliminate sign bits during QROM loading, and proved $J=7$ ($Q=125 \le 126$) is the global maximum batch size under the 128-qubit ceiling.

---

## 🛠️ Verification & Quickstart

Run the complete certified test suite:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```
*(All 15 tests pass in ~4 seconds).*
