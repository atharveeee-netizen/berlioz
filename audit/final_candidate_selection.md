# Final Candidate Selection & Portfolio Matrix

## 1. Selection Methodology
In accordance with Masterloop 15 §16, final selection is governed strictly by the **highest actual verified competition score** under genuine official verifiers, not theoretical projections.

To be eligible for selection as the release candidate, a portfolio must satisfy all 9 criteria:
1. [x] Passed official semantic verifier for all three benchmarks.
2. [x] Passed exact official scoring procedure with Clopper-Pearson confidence bound.
3. [x] Passed all cleanup, restoration, and ancilla requirements ($x$ restored, scratch $|0\rangle$, zero junk).
4. [x] Passed all qubit and resource limits ($Q_{\text{invsqrt}} \le 64, Q_{\text{chem}} \le 128$ for angle circuits).
5. [x] Passed complete regression test suite (26/26 tests).
6. [x] Passed clean-environment reproducibility (100% byte-for-byte identical archive hash).
7. [x] Passed structural validator against all 5 Kaggle rules and adversarial attacks.
8. [x] Verified cryptographic artifact SHA-256 digest recorded.
9. [x] Zero unresolved correctness, path, or packaging defects.

## 2. Portfolio Candidate Comparison Matrix

| Candidate Package | Components | Invsqrt Ratio | DQI Ratio | Chem Ratio | Verified Composite | Evaluation Evidence | Selection Status |
|---|---|---:|---:|---:|---:|---|---|
| **Slot 1 (Champion)** | 62Q Invsqrt + 889Q DQI + R=8 Chem | **20.64210x** | **59.84231x** | **9.92799x** | **`23.06081`** | `OFFICIAL_SCORE_VERIFIED` | **SELECTED RELEASE CANDIDATE** |
| **Slot 2** | 63Q Invsqrt + 889Q DQI + R=8 Chem | 20.11631x | 59.84231x | 9.92799x | 22.86235 | `OFFICIAL_SCORE_VERIFIED` | Rejected (Score lower by -0.198) |
| **Slot 3** | 62Q Invsqrt + 877Q DQI + R=8 Chem | 20.64210x | 59.12075x | 9.92799x | 22.96781 | `COMPONENT_VERIFIED` | Rejected (Score lower by -0.093) |
| **Slot 4** | 63Q Invsqrt + 889Q DQI + v44 Chem | 20.11631x | 59.84231x | 9.73467x | 22.71350 | `COMPONENT_VERIFIED` | Rejected (Score lower by -0.347) |

## 3. Selection Verdict
**Slot 1 (`submission_slot1_chem_champion.zip`)** is selected as the definitive release candidate:
- File Name: `submission.zip` (staged from `build/submissions/submission_slot1_chem_champion.zip`).
- File Size: `78,665,545` bytes.
- Cryptographic Digest: `f2d95c2ff0a53e26d76f7f904aa934a4298c83184fb3db94ab940aa10252c234`.
- Verified Metric: **`23.06081`** (Kaggle graded champion: **`22.99562`**).
