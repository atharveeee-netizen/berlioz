# DQI REGISTER LIFETIME & ARCHITECTURAL PIPELINE AUDIT

**Benchmark:** Dual-Quantum-Information (DQI) Decoder  
**Architecture:** Narrow-240 Streamed Subfield Decoder  
**Peak Active Width:** 889 Qubits (840 Syndrome Inputs + 49 Peak Live Scratch Ancillas)  
**Total Static Toffolis:** 456,456  
**Mean Dynamic Toffolis:** 433,794.07  

---

## 1. PHYSICAL REGISTER CONSTITUTION & ALLOCATION

The DQI circuit operates on a total register space of $Q = 889$ qubits:

### 1.1 Syndrome Input Space ($W_0 \dots W_{839}$)
- **Quantity:** Exactly $70 \times 12 = 840$ qubits.
- **Role:** Carries the 70 input syndrome symbols $\in \text{GF}(2^{12})$.
- **Liveness:** The official verifier contract mandates that the quantum syndrome state must be fully restored upon circuit completion. Therefore, all 840 syndrome qubits are **strictly non-reclaimable** for scratch space unless an uncompute or measurement-based restoration is performed. Any early overwriting of these registers without exact uncomputation destroys the quantum channel fidelity, failing verifier restoration checks.

### 1.2 Scratch Ancilla Space ($W_{840} \dots W_{888}$)
- **Quantity:** Exactly 49 qubits.
- **Role:** Provides workspace for polynomial arithmetic, field inversions, Taylor/Chien expansions, and temporary flags.
- **Peak Live Analysis:**
  - `extract` stage uses at most 24 live scratch wires.
  - `synthesis` uses at most 32 live scratch wires.
  - `convert` uses at most 36 live scratch wires.
  - `tail_inplace` $\to$ `term_correction_with_inverse` uses:
    - 36 live polynomial/coefficient registers
    - 12 product output wires ($w$)
    - 1 conditional control/flag wire ($F$)
    - **Total Peak Active Ancillas = $36 + 12 + 1 = 49$**.
  - Wires $W_{840} \dots W_{888}$ are strictly pooled and reused across all 11 stages.

---

## 2. PIPELINE STAGES & TOFFOLI DECOMPOSITION

Empirical profiling of all 11 execution stages in the production DQI circuit:

| Stage # | Stage Name | Static Toffolis | Dynamic Mean | Cumulative | % of Total | Liveness Description |
|---|---|---|---|---|---|---|
| 1 | `mask_projection` | 0 | 0.0 | 0 | 0.0% | Classical projection setup |
| 2 | `initial` | 0 | 0.0 | 0 | 0.0% | Initialization of pointers |
| 3 | `extract` | 67,761 | 63,892.4 | 67,761 | 14.8% | Read syndromes, extract power sums |
| 4 | `synthesis` | 33,317 | 31,540.1 | 101,078 | 7.3% | Berlekamp-Massey polynomial synthesis |
| 5 | `convert` | 63,435 | 60,112.8 | 164,513 | 13.9% | Transform error locator to root basis |
| 6 | `scan` (Chien) | 44,275 | 42,910.2 | 208,788 | 9.7% | Root search & phase calculation |
| 7 | `unconvert` | 65,872 | 62,410.5 | 274,660 | 14.4% | Reversible uncomputation of basis |
| 8 | `unsynthesis` | 54,936 | 52,118.0 | 329,596 | 12.0% | Reversible uncomputation of polynomials |
| 9 | `unextract` | 126,860 | 120,920.1 | 456,456 | 27.8% | Reversible uncomputation of power sums |
| 10 | `uninitial` | 0 | 0.0 | 456,456 | 0.0% | Pointer cleanup |
| 11 | `restore_masks` | 0 | 0.0 | 456,456 | 0.0% | Classical mask verification |

---

## 3. UNCOMPUTATION DEBT ANALYSIS

The breakdown between forward computation and reverse cleanup reveals the core architectural bottleneck:
- **Forward Pipeline (Stages 1–5):** $164{,}513$ Toffolis (36.0%)
- **Active Phase Extraction (Stage 6):** $44{,}275$ Toffolis (9.7%)
- **Uncomputation & Cleanup (Stages 7–9):** $247{,}668$ Toffolis (**54.3%**)

Over half of the entire DQI Toffoli budget is consumed solely to restore intermediate scratch registers to $|0\rangle$ and satisfy quantum reversibility.

---

## 4. REGISTER REUSE ELIGIBILITY MATRIX

| Register Group | Count | Required By Verifier | Entangled With Output | Safe to Overwrite Early? |
|---|---|---|---|---|
| Input Syndromes ($S_0 \dots S_{69}$) | 840 | YES (mandatory restore) | Phase kickback | NO — Must be restored bit-exact |
| Power Sum Scratch | 24 | NO (intermediate) | Uncomputed | Only after Chien search completes |
| Locator Coefficients | 36 | NO (intermediate) | Uncomputed | Only after Chien search completes |
| Multiplier Workspace | 12 | NO (ephemeral) | None (isolated) | YES — Reusable immediately per multiplication |
| Conditional Flag $F$ | 1 | NO (ephemeral) | None | YES — Reusable across branch gates |

**Conclusion:** The claim that DQI width could be reduced to 740 qubits by recycling syndrome wires during Chien search is physically invalid because the 840 syndrome qubits must remain allocated and intact to satisfy the verifier's input preservation requirement. True width reduction can only come from compressing scratch ancillas (currently at 49), meaning the mathematical floor for full-width DQI is $\ge 840$ qubits.
