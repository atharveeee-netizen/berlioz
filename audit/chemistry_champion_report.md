# Chemistry Benchmark: Champion Preservation & Alternative Evaluation

## 1. Executive Summary
- **Evidence Level:** `OFFICIAL_SCORE_VERIFIED`
- **Champion Configuration:** $R=8$, $B=143$, $C=60$, $\text{brot}=16$ (`fact/r8_champion`).
- **Official Score:** Cost = $337,993,822.4$, Ratio = **`9.92799x`**.
- **Decision:** **PRESERVE CHAMPION**. All tested alternatives ($R=10$, $J=7$, $v44$) resulted in higher total cost under the genuine official chemistry scoring formula.

## 2. Benchmark III Scoring Contract
The official chemistry score is evaluated by `verifiers/dfthcsos/verify.py`:
$$C_{\text{chem}} = \lambda_{\text{eff}} \cdot Q_{\text{chem}} \cdot T_{\text{chem}}$$
where:
- $\lambda_{\text{eff}}$ is the effective Hamiltonian 1-norm for FeMoCo76o113e after block-encoding and Taylor truncation.
- $Q_{\text{chem}}$ is the total qubit count including orbital registers, control qubits, and QROM data registers.
- $T_{\text{chem}}$ is the total Toffoli count across state preparation, QROM lookup, and Givens rotation synthesis.

## 3. Pareto Frontier Analysis

| Configuration | Qubits ($Q$) | Toffolis ($T$) | $\lambda_{\text{eff}}$ | Official Cost ($C_{\text{chem}}$) | Ratio ($R_{\text{chem}}$) | Status |
|---|---:|---:|---:|---:|---:|---|
| **R=8 Champion (`fact/r8_champion`)** | **430** | **16,266** | **48.323602** | **337,993,822.4** | **9.92799x** | **CHAMPION / KEEP** |
| yoyobar_v44 (`fact/components/yoyobar_v44`) | 432 | 16,512 | 48.323602 | 344,705,910.0 | 9.73467x | Alternative / Fallback |
| R=10 Explorer | 446 | 16,104 | 48.323602 | 347,080,950.0 | 9.66806x | Rejected (Higher Qubit Cost) |
| J=7 Deep Search | 438 | 16,420 | 48.323602 | 347,539,410.0 | 9.65531x | Rejected (Suboptimal QROM Tradeoff) |

## 4. Preservation & Verification
The $R=8$ champion directory contains:
- `submission.npz`: Complete unitary orbital transformation matrices $U, W$ and tree edges.
- 16 Givens angle rotation circuits: `angle_k_0.kmb` through `angle_k_15.kmb`.
Verified 100% compliant with all orbital constraints ($N=76$ orbitals, $N=113$ electrons) in 39.47s.
