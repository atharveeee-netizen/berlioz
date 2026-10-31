# Final Repository Regression Report — Masterloop 15

## 1. Executive Summary
- **Execution Date:** 2026-10-31
- **Platform:** Windows 11 AMD64 / Python 3.11.9 / Kickmix 0.1.0
- **Total Tests Executed:** 26
- **Passed:** **26 / 26** (**100.0%**)
- **Failed:** **0**
- **Skipped / Disabled:** **0**
- **Total Execution Time:** 99.938s

## 2. Test Breakdown by Domain

| Test Module | Coverage Domain | Tests | Result | Duration |
|---|---|---:|---|---:|
| `test_arithmetic_tensor.py` | GF(2^12) 42-product bilinear tensor & multiplication correctness | 4 | **PASS** | 8.2s |
| `test_compactor.py` | Multiplier pooling & register allocation | 1 | **PASS** | 2.1s |
| `test_dqi_compiler.py` | Mini DQI end-to-end synthesis & ancilla leak check | 1 | **PASS** | 9.7s |
| `test_inversionless_bm.py` | RiBM key equation solver up to capacity $t=35$ | 3 | **PASS** | 2.1s |
| `test_portfolio_coupling.py` | Chemistry tensor shapes, J=7 Givens circuits, qubit bounds | 4 | **PASS** | 4.5s |
| `test_pricebook.py` | Kickmix gate cost model, Clifford/non-Clifford marginal accounting | 1 | **PASS** | 0.8s |
| `test_quadratic_phase_erase.py` | Degree-2 quadratic-phase erasure & phase kickback cancellation | 4 | **PASS** | 1.9s |
| `test_submission_validator.py` | Path traversal, absolute paths, corrupt zips, 5-rule compliance | 8 | **PASS** | 17.4s |

## 3. Official Benchmark Verifiers Summary
In addition to the unit regression suite, all three genuine competition verifiers were executed end-to-end via `src/verify_portfolio.py`:
- **Benchmark I (Invsqrt):** 62Q Champion evaluated across 1,024 shots $\to$ **PASS** (Ratio: 20.64210x).
- **Benchmark II (DQI):** 889Q Champion evaluated across 2,048 shots $\to$ **PASS** (0 value errors, 0 phase errors, Ratio: 59.84231x).
- **Benchmark III (Chemistry):** R=8 FeMoCo76o113e evaluated across all Givens angles $\to$ **PASS** (Ratio: 9.92799x).
- **Composite Verified Score:** **`23.06081`**
