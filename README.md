# Berlioz: Discrete Algebraic Quantum Circuit Synthesis & Verification
### Google Quantum AI — Verifiable Quantum Circuit Compilation (Kaggle)

<p align="center">
  <img src="https://img.shields.io/badge/Google_Quantum_AI-Competition-4285F4?style=for-the-badge&logo=google" alt="Google Quantum AI">
  <img src="https://img.shields.io/badge/Active_Team-TuringIRL(akshit)-blueviolet?style=for-the-badge&logo=kaggle" alt="TuringIRL">
  <img src="https://img.shields.io/badge/Leaderboard_Rank-275_%2F_1698_(Top_16%25)-success?style=for-the-badge" alt="Rank 275">
  <img src="https://img.shields.io/badge/Live_Verified_Score-22.99562-success?style=for-the-badge" alt="Verified Score">
  <img src="https://img.shields.io/badge/Release_Gate-MASTERLOOP_15_PASSED-blue?style=for-the-badge" alt="Masterloop 15 Passed">
</p>

**Berlioz** is an advanced algebraic quantum circuit compilation engine designed for fault-tolerant Clifford+Toffoli architectures evaluated by the official C++ Pauli simulator `kickmix`.

---

## 🧭 Essential Documentation & Audit Chronicle

* **[`audit/final_release_report.md`](audit/final_release_report.md)**: **Masterloop 15 Final Release Report**. Comprehensive audit of all release gates, benchmark results, and verification proofs.
* **[`audit/baseline.json`](audit/baseline.json)**: Machine-readable baseline configuration, environment freeze, and reference costs.
* **[`JOURNEY.md`](JOURNEY.md)**: Detailed narrative of mathematical derivations, architecture breakthroughs, and empirical milestones.
* **[`LEDGER.md`](LEDGER.md)**: The Empirical Truth Gate & Master Loop Tracker with verified benchmark metrics.
* **[`HANDOVER.md`](HANDOVER.md)**: Technical specifications and algorithmic dossiers.

---

## 🏆 Current Standing & Verified Score Formulation

$$\text{Score} = \left(\text{Ratio}_{\text{invsqrt}} \times \text{Ratio}_{\text{dqi}} \times \text{Ratio}_{\text{dfthcsos}}\right)^{1/3} = \mathbf{22.99562}$$

* **Official Public Rank:** **#275** / 1,698 Teams (**Top 16.2%**)
* **Active Graded Champion:** Submission `57811741` / `57800637`

| Benchmark | Google Reference | Active Verified Cost | Improvement Ratio | Core Algorithmic Lever | Evidence Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`invsqrt`** | $2{,}076{,}774.23$ | $100{,}517.58$ | **$20.642\times$** | 62-Qubit Newton-Raphson Seed Table + rotation synthesis | `OFFICIAL_SCORE_VERIFIED` |
| **`dqi`** | $24{,}439{,}463{,}583{,}673$ | $4.0840 \times 10^{11}$ | **$59.842\times$** | 889Q Systolic Retimed Decoder with Selective QPE | `OFFICIAL_SCORE_VERIFIED` |
| **`dfthcsos`**| $3{,}355{,}599{,}588.32$ | $3.3799 \times 10^8$ | **$9.928\times$** | $R=8$ Factorization + 4-Address Pebble QROM | `OFFICIAL_SCORE_VERIFIED` |
| **Product** | — | — | **$\text{GM} = \mathbf{23.061}$ (Verified)** | **Leaderboard Graded: $22.99562$** | `GRADED` |

---

## 🔬 Core Breakthroughs Implemented in Berlioz

1. **Quadratic-Phase Erasure (`src/dqi/quadratic_phase_erase.py`)**:
   Eliminates reverse multiplication Toffolis during uncompute by neutralizing degree-$\le 2$ kickback phases using conditional Clifford $CZ$ networks for **0 Toffolis** (`tests/test_quadratic_phase_erase.py`).
2. **Reformulated Inversionless Berlekamp-Massey (`src/dqi/ribm.py`)**:
   Classical prototype solving the RS key equation without field inversions across error weights up to capacity $t=35$ (`tests/test_inversionless_bm.py`).
3. **42-Product Bilinear Tensor in $\text{GF}(2^{12})$ (`src/dqi/tower42.py`)**:
   Decomposes Galois field multiplication into a subfield tower $\text{GF}(8)[v]/(v^4+v+1)$ with 42 bilinear products and free Frobenius squarings (`tests/test_arithmetic_tensor.py`).
4. **Hardened Submission Validator & Atomic Packaging (`src/validate_submission.py`)**:
   Enforces all 5 competition rules and defends against path traversal, absolute paths, corrupt archives, and malformed NPZ arrays (`tests/test_submission_validator.py`).

---

## 🛠️ Verification & Quickstart

### 1. Run the Certified Regression Suite (26 tests)
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```
*(All 26 tests pass in ~100 seconds).*

### 2. Package All Submission Slots Deterministically
```bash
python src/build_all_submissions.py
```

### 3. Verify and Certify Release Candidate Against Official Verifiers
```bash
python src/verify_portfolio.py submission.zip --mode quick --dqi-shots 2048
```
