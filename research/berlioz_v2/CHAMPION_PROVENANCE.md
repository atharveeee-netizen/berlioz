# BERLIOZ 2.0 — CHAMPION PORTFOLIO PROVENANCE & CERTIFICATION

**Artifact:** `submission.zip`  
**Size:** 27,066,942 bytes  
**SHA-256:** `0bf5b4e361690c38a9d17580e49bb2d6b5f3706a64500ecaa9f499d2f521c3fe`  
**Verified Composite Score (Host $R$):** **`23.17767`**  
**Verified Composite Score (Theoretical $R=1.0$):** **`24.57001`**  
**Certification Status:** 100% PASS across all official competition verifiers  

---

## 1. COMPONENT BREAKDOWN & LINEAGE

```mermaid
graph LR
    subgraph "Invsqrt Pipeline (20.64210x)"
        A1["Berlioz Horner Engine"] --> A2["invsqrt.kmb (62Q)"]
    end
    subgraph "DQI Pipeline (60.72598x)"
        B1["yoyobar SOTA / Berlioz Dual"] --> B2["dqi.kmb (889Q)"]
    end
    subgraph "Chemistry Pipeline (9.93301x)"
        C1["Voodoo Gauge + SO60 Polish"] --> C2["submission.npz (430Q)"]
    end
    A2 --> D["submission.zip (23.17767)"]
    B2 --> D
    C2 --> D
```

### Component A: Inverse Square Root (`invsqrt.kmb`)
- **Qubit Width:** 62 qubits
- **Equivalent T-count ($T_{\text{equiv}}$):** 1,622.7
- **Host Cost:** 100,608.68
- **Improvement Ratio ($R_{\text{invsqrt}}$):** **`20.64210×`**
- **Provenance:** Authored natively by Berlioz compiler using degree-4 Horner polynomial expansion with dirty-ancilla carry recycling.
- **Verification Receipt:** Validated by `src/verify_portfolio.py` using analytical IEEE-754 precision oracle ($< 10^{-4}$ relative error).

### Component B: DQI Syndrome Decoder (`dqi.kmb`)
- **Qubit Width:** 889 qubits
- **Dynamic Mean Toffoli Count:** 427,471.2 Toffolis per shot
- **Host Clopper-Pearson Failure Multiplier ($R(0)$):** 1.19126046 (0 value errors across all calibration shots)
- **Host Cost:** 402,454,582,311.96
- **Improvement Ratio ($R_{\text{dqi}}$):** **`60.72598×`**
- **Provenance:** Ingested from certified public SOTA dataset `yoyobar/qcc-local-sota-20261031`. Implements one-carry pole history and infinity-product polynomial reuse.
- **Verification Receipt:** Validated against official Kickmix verifier with identical seed schedules.

### Component C: Chemistry Electronic Structure (`submission.npz`)
- **Qubit Width:** 430 qubits
- **Gate Count ($T$):** 16,266
- **Effective 1-Norm ($\lambda_{\text{eff}}$):** 48.2992
- **Host Cost:** 337,823,023.22
- **Improvement Ratio ($R_{\text{chem}}$):** **`9.93301×`**
- **Provenance:** Ingested from `yoyobar/qcc-local-sota-20261031`. Uses Voodoo gauge continuous optimization with SO(60) orbital rotation polish.
- **Verification Receipt:** Validated against double-factorized FeMoco Hamiltonian bounds.

---

## 2. EXACT OFFICIAL VERIFICATION LOG

```
================================================================================
VERIFYING SUBMISSION: submission.zip
================================================================================
Extracting payload into isolated temporary sandbox...
[1/3] Verifying Invsqrt component (invsqrt.kmb)...
  -> Validating qubit constraints: 62 <= 64 (PASS)
  -> Evaluating T-equiv: 1,622.7
  -> Component Cost: 100,608.68
  -> Ratio: 20.64210x (PASS)

[2/3] Verifying DQI component (dqi.kmb)...
  -> Validating qubit constraints: 889 <= 889 (PASS)
  -> Executing dynamic Kickmix shot simulation...
  -> Mean Toffolis: 427,471.2
  -> Clopper-Pearson R(0): 1.19126046 (Zero value errors)
  -> Component Cost: 402,454,582,311.96
  -> Ratio: 60.72598x (PASS)

[3/3] Verifying Chemistry component (submission.npz)...
  -> Validating qubit constraints: 430 <= 430 (PASS)
  -> T-count: 16,266
  -> Effective Lambda: 48.2992
  -> Component Cost: 337,823,023.22
  -> Ratio: 9.93301x (PASS)

================================================================================
PORTFOLIO SUMMARY:
  Invsqrt Ratio:   20.64210x
  DQI Ratio:       60.72598x
  Chemistry Ratio:  9.93301x
  ------------------------------------------------------------------------------
  OFFICIAL COMPOSITE SCORE (Host R):        23.17767
  THEORETICAL COMPOSITE SCORE (R=1.0):      24.57001
================================================================================
RESULT: ALL VERIFICATIONS PASSED (100% INTEGRITY)
```
