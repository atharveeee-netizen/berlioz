# BERLIOZ — CHUNK C0 BASELINE RECORD

**HEAD SHA:** `ec0534ec36a66ab5396ab6d616c275f6be300d04`  
**Branch:** `ml16`  
**Tag:** `ml16-baseline`  
**Date:** 31 October 2026  
**Status:** Frozen baseline for Masterloop 16 Chunked Execution  

---

## 1. PRODUCTION BUILDERS

| Benchmark | Builder Script / Module | Target Output | Configuration / Parameters |
|---|---|---|---|
| **Invsqrt** | `src/build_invsqrt.py` | `invsqrt.kmb` | Q=62, Degree-4 Horner, dirty-ancilla carry recycling |
| **DQI** | `src/dqi/build_dqi.py` / `src/build_submission_zip.py` | `dqi.kmb` | Q=889, One-carry pole history, infinity-product reuse |
| **Chemistry** | `dfthcsos/` / `src/build_all_submissions.py` | `submission.npz` | Q=430, T=16,266, Voodoo gauge continuous SO60 polish |
| **Unified** | `src/build_submission_zip.py` | `submission.zip` | Bundles `invsqrt.kmb`, `dqi.kmb`, `submission.npz` |

---

## 2. VERIFICATION SYSTEMS

| System | Script Path | Method / Execution Profile |
|---|---|---|
| **Official Portfolio Verifier** | `src/verify_portfolio.py` | Full multi-benchmark sandbox verification (Invsqrt, DQI, Chem) |
| **Canonical Score Calculator** | `tools/score_calc.py` | Exact Clopper-Pearson bound ($\delta = 2^{-128}$), exchange rates |
| **Test Suite** | `tools/tests/test_score_calc.py` | Unit tests verifying $S=23.060808$, $R(0)$, $\epsilon^+(k)$, failure table |
| **Invsqrt Semantic Verifier** | Embedded in `src/verify_portfolio.py` | Analytical IEEE-754 floating-point relative error oracle |
| **DQI Kickmix Simulator** | Embedded in `src/verify_portfolio.py` | Shot simulation over Fiat-Shamir salted seeds |
| **Chemistry Verifier** | Embedded in `src/verify_portfolio.py` | Active space energy and spectral norm validation |

---

## 3. UNCOMMITTED WORK & EXPERIMENT STATUS

- **Uncommitted working tree:** Clean (0 uncommitted files).
- **Unfinished experiments:** None in progress; all previous prototypes merged or archived in `audit/baseline_vault/`.
- **Champion Artifact:** `submission.zip` (SHA-256: `0bf5b4e361690c38a9d17580e49bb2d6b5f3706a64500ecaa9f499d2f521c3fe`).
- **Baseline Composite:** `23.060808` (from ML16 starting state) / `23.17767` (certified SOTA champion).
