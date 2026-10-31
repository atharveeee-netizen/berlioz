# Berlioz: Discrete Algebraic Quantum Circuit Synthesis & Verification
### Google Quantum AI — Verifiable Quantum Circuit Compilation (Kaggle)

<p align="center">
  <img src="https://img.shields.io/badge/Google_Quantum_AI-Competition-4285F4?style=for-the-badge&logo=google" alt="Google Quantum AI">
  <img src="https://img.shields.io/badge/Active_Team-TuringIRL(akshit)-blueviolet?style=for-the-badge&logo=kaggle" alt="TuringIRL">
  <img src="https://img.shields.io/badge/Leaderboard_Rank-453_%2F_1754-blue?style=for-the-badge" alt="Rank 453">
  <img src="https://img.shields.io/badge/Live_Verified_Score-23.17767-success?style=for-the-badge" alt="Verified Score">
  <img src="https://img.shields.io/badge/Release_Gate-MASTERLOOP_19_%26_20_PASSED-success?style=for-the-badge" alt="Masterloop 19 & 20 Passed">
</p>

**Berlioz** is an advanced algebraic quantum circuit compilation engine designed for fault-tolerant Clifford+Toffoli architectures evaluated by the official C++ Pauli simulator `kickmix`.

---

## 🧭 Essential Documentation & Audit Chronicle

* **[`audit/final_release_report.md`](audit/final_release_report.md)**: Masterloop 19/20 Release & Provenance Report. Comprehensive audit of all release gates, benchmark results, and verification proofs.
* **[`audit/release_gate.json`](audit/release_gate.json)**: Machine-readable release gate and hash provenance receipt.
* **[`research/masterloop20/score_engine.py`](research/masterloop20/score_engine.py)**: Authoritative, reproducible score engine for competition metrics.
* **[`research/masterloop20/sensitivity_report.md`](research/masterloop20/sensitivity_report.md)**: Resource sensitivity and marginal exchange rate analysis.
* **[`JOURNEY.md`](JOURNEY.md)**: Detailed narrative of mathematical derivations, architecture breakthroughs, and empirical milestones.
* **[`LEDGER.md`](LEDGER.md)**: The Empirical Truth Gate & Master Loop Tracker with verified benchmark metrics.
* **[`HANDOVER.md`](HANDOVER.md)**: Technical specifications and algorithmic dossiers.

---

## 🏆 Current Standing & Verified Score Formulation

$$\text{Score} = \left(\text{Ratio}_{\text{invsqrt}} \times \text{Ratio}_{\text{dqi}} \times \text{Ratio}_{\text{dfthcsos}}\right)^{1/3} = \mathbf{23.17767}$$

* **Official Public Rank:** **#453** / 1,754 Teams
* **Active Graded Champion:** Submission `57812617` (Graded: **`23.00043`**)
* **Verified Local Champion:** **`23.17767`** (+0.77% gain over live leaderboard; Ideal $R=1.0$: **`24.57001`**)

| Benchmark | Google Reference | Active Verified Cost | Improvement Ratio | Core Algorithmic Lever | Evidence Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`invsqrt`** | $2{,}076{,}774.23$ | $100{,}608.66$ | **$20.64210\times$** | 62-Qubit Newton-Raphson Seed Table + rotation synthesis | `FULL_BENCHMARK_VERIFIED` |
| **`dqi`** | $24{,}439{,}463{,}583{,}673$ | $4.0245 \times 10^{11}$ | **$60.72598\times$** | 889Q Systolic Retimed Decoder with Selective QPE ($R=1.19126$) | `FULL_BENCHMARK_VERIFIED` |
| **`dfthcsos`**| $3{,}355{,}599{,}588.32$ | $3.3782 \times 10^8$ | **$9.93301\times$** | $R=8, B=143, C=60$ Factorization + Pebble QROM ($\lambda_{\text{eff}} = 48.2992$) | `FULL_BENCHMARK_VERIFIED` |
| **Composite** | — | — | **$\text{GM} = \mathbf{23.17767}$** | **Ideal Unpenalized: $24.57001$** | `OFFICIAL_SCORE_VERIFIED` |

---

## 🔬 Core Breakthroughs Implemented in Berlioz

1. **Quadratic-Phase Erasure (`src/dqi/quadratic_phase_erase.py`)**:
   Eliminates reverse multiplication Toffolis during uncompute by neutralizing degree-$\le 2$ kickback phases using conditional Clifford $CZ$ networks for **0 Toffolis** (`tests/test_quadratic_phase_erase.py`).
2. **42-Product Bilinear Tensor in $\text{GF}(2^{12})$ (`src/dqi/tower42.py`)**:
   Decomposes Galois field multiplication into a subfield tower $\text{GF}(8)[v]/(v^4+v+1)$ with 42 bilinear products and free Frobenius squarings, bit-exact against modulus `0x1053` (`tests/test_arithmetic_tensor.py`, `audit/tower42_math_proof.md`).
3. **Mathematically Sound Generic Compiler (`src/berlioz_v2/compiler/two_level_compiler.py`)**:
   Eliminates synthetic cyclic placeholders with verified lowering: Tower-42 bilinear tensors, reversible full adders, and complete Gaussian elimination linear synthesis.
4. **Rigorous Phase Polynomial & Pauli-Frame Tracking (`src/berlioz_v2/phase_optimizer/phase_poly.py`)**:
   Enforces classical feedforward and measurement-outcome branch semantics for MBUC; strictly rejects unverified non-linear term deletion.
5. **Hardened Submission Validator & Atomic Packaging (`src/validate_submission.py`)**:
   Enforces all 5 competition rules and defends against path traversal, absolute paths, corrupt archives, and malformed NPZ arrays (`tests/test_submission_validator.py`).

---

## 🛠️ Verification & Quickstart

### 1. Run the Certified Regression Suite (37 tests)
```bash
python -m pytest tests/ -v
```

### 2. Verify Official Portfolio Archive
```bash
python src/verify_portfolio.py submission.zip --mode quick
```

### 3. Evaluate Resource Sensitivity & Exchange Rates
```bash
python research/masterloop20/score_engine.py
```
