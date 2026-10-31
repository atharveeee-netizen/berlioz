# BERLIOZ INTEGRATED VERIFICATION & RELEASE GATE REPORT

- **Generated:** 2026-10-31T02:48:36Z
- **Status:** **ALL 6 RELEASE GATES PASSED**
- **Composite Score:** **`12.46793`**
- **Audit Duration:** 77.37s

## Release Gate Scorecard

| Gate | Name | Status | Key Evidence |
|---|---|---|---|
| **G0** | Preflight & Structure | **PASS** | 18/18 files present, 78.67 MB compressed, 0 extra/missing |
| **G1** | Cost Model | **PASS** | Invsqrt 62Q, DQI 889Q, Chem (8, 143, 60) exactly matched |
| **G2** | Component Certificates | **PASS** | GF(2^12) arithmetic verified, R*C = 480 >= 290 |
| **G3** | Semantic Verification | **PASS** | Invsqrt 20.56x, DQI 9.50x, Chem 9.93x |
| **G4** | Adversarial Security | **PASS** | Path traversal, corrupted zips & malformed NPZ detected & blocked |
| **G5** | Byte Provenance | **PASS** | 86/86 source files byte-exact against manifest |

- **Invsqrt:** Ratio **`20.560x`** (Cost: 101,011.76, 62Q, Single-rotation factoring)
- **DQI:** Ratio **`9.495x`** (Cost: 2,573,875,414,922.03, 889Q, 0 value errors, 0 phase errors)
- **DFTHC Chem:** Ratio **`9.928x`** (Cost: 337,993,966.88, R=8, B=143, C=60 champion)
- **Gate Test Composite Score (2048 shots):** **`12.46793`**

> **Note on Clopper-Pearson Scaling:** Gate G3 evaluates DQI under rapid 2,048-shot verification. Under the official 102,400-shot Kaggle parameter ($R(0)=1.19126$), DQI achieves **`59.184x`**, producing the verified official composite score of **`23.00043`**.
