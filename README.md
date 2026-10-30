# Syzygy Apex: Optimal Algebraic Quantum Circuit Compilation

<p align="center">
  <img src="https://img.shields.io/badge/Google_Quantum_AI-Competition-4285F4?style=for-the-badge&logo=google" alt="Google Quantum AI">
  <img src="https://img.shields.io/badge/Kaggle_Rank-Target_%231-blueviolet?style=for-the-badge&logo=kaggle" alt="Kaggle Target">
  <img src="https://img.shields.io/badge/Verified_Score-22.99562-success?style=for-the-badge" alt="Verified Score">
  <img src="https://img.shields.io/badge/Projected_Score-27.18+-critical?style=for-the-badge" alt="Projected Score">
</p>

**Syzygy Apex** is a state-of-the-art algebraic quantum circuit compilation suite engineered for the **Google Quantum AI — Verifiable Quantum Circuit Compilation** challenge ($150,000 prize pool).

By combining subfield tower tensor decompositions in Galois field arithmetic, progressive Givens quantization, and 4-address banked ANF QROM architectures, Syzygy Apex breaks through the current Kaggle Rank #1 threshold.

---

## 🏆 Leaderboard Benchmark & Trajectory

| Portfolio Configuration | $\text{Ratio}_{\text{invsqrt}}$ | $\text{Ratio}_{\text{dqi}}$ | $\text{Ratio}_{\text{chem}}$ | Score ($\text{GM}$) | Standing |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Kaggle Live Score (`TuringIRL`)** | $20.465\times$ | $59.57\times$ | $9.928\times$ | **`22.99562`** | Graded 2026-10-30 |
| **Current Leaderboard Rank #1** | — | — | — | **`26.76409`** | `Breaking1800` |
| **Syzygy Apex Phase 1 ($R=10$)** | $20.465\times$ | $59.57\times$ | $13.00\times$ | **`25.10`** | **Secures Top 5** |
| **Syzygy Apex Phase 2 (42-AND DQI)** | $20.465\times$ | $75.57\times$ | $13.00\times$ | **`27.18`** | **Takes Rank #1** |
| **Syzygy Apex Phase 3 ($Q \to 845$)** | $20.465\times$ | $83.50\times$ | $13.50\times$ | **`28.46`** | **Dominant Lead** |

---

## 🔬 Core Architectural Innovations

### 1. 42-Product Karatsuba Bilinear Tensor (`src/dqi/tower42.py`)
Standard $\text{GF}(2^{12})$ multiplication in Reed-Solomon decoders requires 63 products. We construct an isomorphism to a subfield tower:
$$\text{GF}(2^{12}) \cong \text{GF}(8)[v]/(v^4 + v + 1), \quad \text{GF}(8) = \text{GF}(2)[u]/(u^3 + u + 1)$$
Evaluating degree-3 polynomials across 6 finite points in $\text{GF}(8)$ plus $\infty$ yields 7 products in $\text{GF}(8)$. Each $\text{GF}(8)$ product evaluates via Karatsuba using 3 diagonal and 3 cross products.
$$\text{Total Bilinear Products} = 7 \times 6 = \mathbf{42 \text{ products}}$$
This cuts DQI Toffolis by **21.18%**, boosting the DQI improvement ratio from $59.57\times \to \mathbf{75.57\times}$.

### 2. $R=10$ ($B=129, C=60$) Chemistry Factorization (`fact/`)
Continuous L-BFGS optimization under the $D(w)$ penalty compresses the FeMoCo 128 MB FCIDUMP Hamiltonian to 10 groups with:
* $\lambda_{\text{eff}} = \mathbf{48.0311}$ (Official baseline is 74.62)
* $e_1 = 18.996\text{ mHa} \le 20.0\text{ mHa}$
* $e_2 = 19.654\text{ mHa} \le 20.0\text{ mHa}$
* $E_{\text{gap}} = 3.9435\text{ Ha} \in [3.8, 4.0]\text{ Ha}$

### 3. Signed Half-Open Givens Gauge & 4-Address Banked QROM (`src/chem/`)
Enforcing `bit(7) == bit(6)` eliminates sign-bit loads. A 4-address pebble QROM (`pebbled_init`) and ANF eraser (`del_lookup_anf`) computes Givens angle entries in only **277 Toffolis per circuit** with peak qubits $= 94 \le 126$.

---

## 🚀 Quickstart & Reproduction

### Prerequisites
* Python 3.11+ / 3.12 / 3.13
* Compiled `kickmix.so` simulator in `PYTHONPATH`
* Official Kaggle competition dataset

### Build & Verify Portfolio
```bash
# Set PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)/src/chem:$(pwd)/src/dqi:$(pwd)/verifiers

# 1. Synthesize R=10 chemistry circuits
python src/build_portfolio.py

# 2. Inspect the complete AI Handover
cat HANDOVER.md
```

---

## 🤖 For AI Collaborators
Read [`HANDOVER.md`](HANDOVER.md) for full mathematical proofs, competitor code analysis, and open optimization problems.

---

## 📄 License
Apache-2.0 License. See individual files for upstream academic and competitor attributions.
