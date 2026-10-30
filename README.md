# TuringIRL Quantum: Architectural Blueprint for Score 50

<p align="center">
  <img src="https://img.shields.io/badge/Google_Quantum_AI-Competition-4285F4?style=for-the-badge&logo=google" alt="Google Quantum AI">
  <img src="https://img.shields.io/badge/Active_Team-TuringIRL(akshit)-blueviolet?style=for-the-badge&logo=kaggle" alt="TuringIRL">
  <img src="https://img.shields.io/badge/Verified_Live_Score-22.99562-success?style=for-the-badge" alt="Verified Score">
  <img src="https://img.shields.io/badge/Grand_Target-Score_50.0-critical?style=for-the-badge" alt="Grand Target">
</p>

**TuringIRL Quantum** is a research-grade quantum circuit compilation framework built for the **Google Quantum AI — Verifiable Quantum Circuit Compilation** challenge ($150,000 prize pool).

Rather than targeting incremental leaderboard ranks, this codebase focuses on the grand theoretical frontier: **achieving a Geometric Mean Score of 50.0** (Improvement Product $= 50^3 = \mathbf{125{,}000}$) across all three competition benchmarks.

---

## 🏆 The Grand Objective: The Score 50 Architecture

$$\text{Score} = \left(\text{Ratio}_{\text{invsqrt}} \times \text{Ratio}_{\text{dqi}} \times \text{Ratio}_{\text{chem}}\right)^{1/3} = \mathbf{50.0}$$

$$\text{Improvement Product} = 25.0 \times 200.0 \times 25.0 = \mathbf{125{,}000}$$

| Benchmark | Google Reference | Active TuringIRL Cost | Current Ratio | Score 50 Target Cost | Score 50 Target Ratio | Primary Scaling Lever |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`invsqrt`** | $2{,}076{,}774.23$ | $101{,}479.23$ | **$20.465\times$** | $\approx 83{,}000$ | **$\mathbf{25.0\times}$** | 56-Qubit NR Seed Table + Clifford pipelining |
| **`dqi`** | $24{,}439{,}463{,}583{,}673$ | $4.1026 \times 10^{11}$ | **$59.57\times$** | $\approx 1.22 \times 10^{11}$ | **$\mathbf{200.0\times}$** | 42-AND Tensor + Min-Heap Wire Compaction ($Q \to 520$) |
| **`dfthcsos`**| $3{,}355{,}599{,}588.32$ | $3.3799 \times 10^8$ | **$9.928\times$** | $\approx 1.34 \times 10^8$ | **$\mathbf{25.0\times}$** | $R=7$ Factorization ($\lambda_{\text{eff}} \le 42$) + 8-Address ANF QROM |
| **Product** | — | **$12{,}104$** | **$\text{GM} = 22.995$** | — | **$\mathbf{125{,}000}$** | **$\text{GM} = \mathbf{50.0}$** |

---

## 🔬 Core Architectural Breakthroughs

### 1. 42-Product Bilinear Multiplier in $\text{GF}(2^{12})$ (`src/dqi/tower42.py`)
Standard $\text{GF}(2^{12})$ multiplication in Reed-Solomon decoders requires 63 products. We construct an isomorphism to a subfield tower:
$$\text{GF}(2^{12}) \cong \text{GF}(8)[v]/(v^4 + v + 1), \quad \text{GF}(8) = \text{GF}(2)[u]/(u^3 + u + 1)$$
Evaluating degree-3 polynomials across 6 finite points in $\text{GF}(8)$ plus $\infty$ yields 7 products in $\text{GF}(8)$. Each $\text{GF}(8)$ product evaluates via Karatsuba using 3 diagonal and 3 cross products ($6$ binary products).
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

## 📂 Repository Layout

```text
TuringIRL-quantum/
├── HANDOVER.md                    # Comprehensive AI Handover & Architectural Dossier
├── RESEARCH_VAULT_AND_LITERATURE.md # Deep research literature, papers, proofs, and theory
├── README.md                      # High-level architecture, metrics, and roadmap
├── top_solutions/                 # Scraped notebooks & codebases from all top competitors
│   ├── README.md                  # Detailed index and analysis of competitor methods
│   ├── avazaku_*.ipynb            # 42-AND multiplier and gauge descent notebooks
│   ├── michaelrustad_*.ipynb      # R=10 merged group chemistry notebooks
│   ├── somejoint_*.ipynb          # 889Q stream decoder notebooks
│   └── yoyobar_*.ipynb            # 62Q invsqrt notebooks
├── src/
│   ├── build_portfolio.py         # Master fusion & Kaggle submission.zip packager
│   ├── dqi/
│   │   └── tower42.py             # Exact 42-AND Bilinear Multiplier & Kickmix Adapter
│   └── chem/                      # Complete DF-THC chemistry engine
│       ├── angles_qrom.py         # Half-open Givens gauge + 4-address pebble QROM
│       ├── banked_lab.py          # ANF eraser & pebble init
│       ├── cont_lbfgs.py          # Continuous L-BFGS group refits
│       └── pq.py                  # 64-stage progressive Givens quantization
├── fact/
│   └── dfthc_r10_b129_c60_brot8.npz  # Verified R=10 factorization (lambda_eff = 48.0311)
└── verifiers/                     # Official Google Quantum AI verification suites
```

---

## 🚀 Quickstart & Verification

```bash
# Set PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)/src/chem:$(pwd)/src/dqi:$(pwd)/verifiers

# 1. Synthesize R=10 chemistry circuits
python src/build_portfolio.py

# 2. Inspect the complete AI Handover
cat HANDOVER.md

# 3. Read the research vault and academic foundations
cat RESEARCH_VAULT_AND_LITERATURE.md
```

---

## 🤖 For AI Collaborators
Review [`HANDOVER.md`](HANDOVER.md) and [`RESEARCH_VAULT_AND_LITERATURE.md`](RESEARCH_VAULT_AND_LITERATURE.md) for full mathematical formulations, competitor analysis, and open optimization problems.

---

## 📄 License
Apache-2.0 License.
