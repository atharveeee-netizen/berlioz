# Hardcoding Elimination & Self-Containment Audit

## 1. Scope and Inventory of Scanned Files
The entire Berlioz repository was audited for external filesystem paths, sibling repository references, absolute user directories, and hardcoded scoring assumptions:
- `src/build_all_submissions.py`
- `src/build_portfolio.py`
- `src/build_slot1.py`
- `src/verify_portfolio.py`
- `src/validate_submission.py`
- `verify_harness.py`
- All DQI builders and extracted components.

## 2. Identified Hardcodings and Resolutions

| Location | Prior Value / Pattern | Defect Type | Resolution / Fix | Status |
|---|---|---|---|---|
| `build_all_submissions.py:33` | `../quantum-competition/current_best/invsqrt_63q.kmb` | Sibling Directory Dependency | Copied asset into `fact/components/invsqrt_63q.kmb`; referenced via `ROOT / 'fact/components/...'` | **RESOLVED** |
| `build_all_submissions.py:38` | `../quantum-competition/current_best/invsqrt_62q.kmb` | Sibling Directory Dependency | Copied asset into `fact/components/invsqrt_62q.kmb`; referenced via `ROOT / 'fact/components/...'` | **RESOLVED** |
| `build_all_submissions.py:43` | `../quantum-competition/latest_assets/yoyobar_v44` | Sibling Directory Dependency | Copied asset into `fact/components/yoyobar_v44`; referenced via `ROOT / 'fact/components/...'` | **RESOLVED** |
| `build_all_submissions.py:48` | `build/dqi_877q.kmb` | Missing local file | Relocated `dqi_877q.kmb` into `build/` | **RESOLVED** |
| `build_slot1.py:27` | `../quantum-competition/current_best/invsqrt_62q.kmb` | Sibling Directory Dependency | Switched to repository-relative `ROOT / 'fact/components/invsqrt_62q.kmb'` | **RESOLVED** |
| `build_portfolio.py:28` | `../quantum-competition/current_best/...` | Sibling Directory Dependency | Switched to repository-relative paths | **RESOLVED** |
| `verify_harness.py:18` | `../quantum-competition/submission_2299.zip` | External Path | Updated to `audit/baseline_vault/submission_2299.zip` | **RESOLVED** |
| `verify_portfolio.py:207` | `expected_gm = 25.43` | Hardcoded Projected Score | Removed completely. Composite score calculated strictly from live verifier ratios | **RESOLVED** |

## 3. Atomic Submission Packaging
Packaging logic in `src/build_all_submissions.py` and `src/build_slot1.py` now enforces strict atomicity:
1. Circuit assets written to temporary archive `*.tmp.zip`.
2. Hardened structural validator (`validate_submission`) audits the temporary archive against all 5 rules.
3. Upon 100% validator pass, atomic `rename` replaces the final archive.
4. In case of any validation or packaging failure, temporary archives are cleaned up in a `finally` block and the existing release candidate remains untouched.
