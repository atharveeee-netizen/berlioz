# Berlioz: Discrete Algebraic Quantum Circuit Synthesis & Verification
### Google Quantum AI — Verifiable Quantum Circuit Compilation (Kaggle)

<p align="center">
  <img src="https://img.shields.io/badge/Google_Quantum_AI-Competition-4285F4?style=for-the-badge&logo=google" alt="Google Quantum AI">
  <img src="https://img.shields.io/badge/Active_Team-TuringIRL(akshit)-blueviolet?style=for-the-badge&logo=kaggle" alt="TuringIRL">
  <img src="https://img.shields.io/badge/Target_Rank-WORLD_RANK_1-gold?style=for-the-badge" alt="Rank 1">
  <img src="https://img.shields.io/badge/Submitted_Score-23.90823-success?style=for-the-badge" alt="Submitted Score">
  <img src="https://img.shields.io/badge/Newton_Rank1_Target-28.08200-brightgreen?style=for-the-badge" alt="Target Score">
</p>

**Berlioz** is an advanced algebraic quantum circuit compilation engine designed for fault-tolerant Clifford+Toffoli architectures evaluated by the official C++ Pauli simulator `kickmix`.

---

## 🧭 Essential Documentation & Audit Chronicle

* **[`research/newton_quotient_uncomputation_blueprint.md`](research/newton_quotient_uncomputation_blueprint.md)**: Masterloop 35 Newton Quotient Uncomputation Blueprint (Targeting World Rank #1, $S \ge 28.082$).
* **[`research/masterloop32_beyond30_architecture_discovery.md`](research/masterloop32_beyond30_architecture_discovery.md)**: Masterloop 32 Beyond-30 Architecture Discovery Blueprint.
* **[`scripts/pack_syzygy_rank1.py`](scripts/pack_syzygy_rank1.py)**: Certified packaging harness with automated G0–G3 release gate audits.
* **[`JOURNEY.md`](JOURNEY.md)**: Comprehensive narrative of mathematical derivations, architecture breakthroughs, and empirical milestones (Masterloops 1–35).
* **[`LEDGER.md`](LEDGER.md)**: The Empirical Truth Gate & Master Loop Tracker with verified benchmark metrics.
* **[`HANDOVER.md`](HANDOVER.md)**: Technical specifications and algorithmic dossiers.

---

## 🏆 Current Standing & Verified Score Formulation

$$\text{Score} = \left(\text{Ratio}_{\text{invsqrt}} \times \text{Ratio}_{\text{dqi}} \times \text{Ratio}_{\text{dfthcsos}}\right)^{1/3}$$

| Benchmark | Google Reference | Active Submitted Cost | Submitted Ratio | Newton Rank #1 Target | Core Algorithmic Lever |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`invsqrt`** | $2{,}076{,}774.23$ | $100{,}568.50$ | **$20.65034\times$** | **$20.65034\times$** | 62-Qubit Ehan Horner polynomial core with zero domain errors |
| **`dqi`** | $24{,}439{,}463{,}583{,}673$ | $3.7915 \times 10^{11}$ | **$64.45900\times$** | **$104.40000\times$** | In-Place Newton-Girard LFSR uncomputation + zero-cost CZ phase erasure |
| **`dfthcsos`**| $3{,}355{,}599{,}588.32$ | $3.2680 \times 10^8$ | **$10.26800\times$** | **$10.26800\times$** | $R=9, B=143, C=40, \text{brot}=8$ Apex tensor factorization |
| **Composite** | — | — | **$\text{GM} = \mathbf{23.90823}$** | **$\text{GM} = \mathbf{28.08200}$** | **World Rank #1 Target ($\Pi \ge 22{,}136.0$)** |

---

## 🔬 Core Breakthroughs Implemented in Berlioz

1. **Newton-Girard LFSR Syndrome Recomputation (`research/newton_quotient_uncomputation_blueprint.md`)**:
   Solves the 247,668-Toffoli reverse uncomputation bottleneck by regenerating all 70 Reed-Solomon syndromes in-place via $S_i = \Omega_i \oplus \sum_{j=1}^{\min(i, t)} \Lambda_j S_{i-j}$ for only **76,440 Toffolis** and **0 scratch qubits**, saving **171,228 Toffolis**.
2. **Zero-Cost Measurement Phase Erasure (`scripts/test_hmr_phase_cancellation.py`)**:
   Annihilates 825 Hadamard measurement byproduct phases $(-1)^{\text{head}_{\text{orig}} \cdot hm}$ using classical-controlled Pauli $CZ$ gates `b.cz(head_orig, hm)` for **strictly 0 Toffolis and 0 T-gates**.
3. **Forward Multiplier Uncomputation (`mul24_xor99`)**:
   Replaces 33 stages of expensive GF($2^{24}$) Euclidean divisions (`divide_fused` at 1,600 Toffolis each) with forward product uncomputation at only **99 Toffolis** per stage.
4. **Apex Chemistry Tensor Factorization ($R=9, B=143, C=40$)**:
   Compresses tensor inner dimension from $C=60 \to C=40$ while maintaining tight chemical accuracy ($e_1 = 11.82\text{ mHa}, e_2 = 19.999\text{ mHa} \le 20.0\text{ mHa}$) and $\lambda_{\text{eff}} = 47.0619$, achieving an Apex ratio of **$10.26800\times$**.
5. **62Q Ehan Horner Core (`build/harvest_busyaprime/invsqrt.kmb`)**:
   Bit-exact Remez polynomial Horner evaluation achieving **$20.65034\times$** across 200,540,928 shots with $0.00000$ error rate.
6. **Hardened Submission Validator & Atomic Packaging (`src/validate_submission.py`)**:
   Enforces all 5 competition rules and audits compliance across all 18 benchmark members with zero faults.

---

## 🛠️ Verification & Quickstart

### 1. Run the Certified Regression Suite (37 tests)
```bash
python -m pytest tests/ -v
```

### 2. Validate Official Submission Package
```bash
python src/validate_submission.py build/submission.zip
```

### 3. Verify DQI Breakthrough Core
```bash
python scripts/verify_dqi_breakthrough.py
```

### 4. Build and Audit Rank #1 Candidate Portfolio
```bash
python scripts/pack_syzygy_rank1.py
```
