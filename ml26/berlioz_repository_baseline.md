# Berlioz Repository Baseline — Masterloop 26 Part 1.1

**Date:** 2026-10-31T15:18Z
**Evidence class:** E1 (Direct source evidence) + E2 (Locally reproduced)

---

## 1. Repository Identity

| Property | Value |
|---|---|
| Absolute path | `C:\Users\noobg\.gemini\antigravity-ide\scratch\berlioz` |
| Git remote | `https://github.com/atharveeee-netizen/berlioz.git` |
| Branch | `master` |
| HEAD commit | `f083d01086e8f79a395985aa115b43c3744fed9d` |
| Commit message | `feat(masterloop-19-20): complete compiler correctness, verification reconciliation, and ML20 experiment engine` |
| Uncommitted changes | 24 untracked files (ML20-23 deliverables), 1 modified (`audit/official_verification_results.json`) |

---

## 2. Environment

| Component | Version |
|---|---|
| Python | 3.10.11 |
| kickmix | 0.1 |
| numpy | 2.2.6 |
| OS | Windows |

---

## 3. Source Structure

### 3.1 DQI (`src/dqi/`)

| File | Size | Purpose |
|---|---|---|
| `build_dqi.py` | 2,768 B | Standard DQI decoder builder |
| `build_compact_dqi.py` | 4,435 B | Compact decoder with Tower-42 multipliers |
| `compactor.py` | 3,500 B | Circuit compaction utilities |
| `ribm.py` | 2,262 B | Inversionless Berlekamp-Massey |
| `tower42.py` | 12,518 B | Tower-42 bilinear GF(2^12) multipliers |
| `quadratic_phase_erase.py` | 1,689 B | Phase erasure optimization |

### 3.2 Chemistry (`src/chem/`)

Includes `angles_qrom.py` — 4-address banked QROM with pebbled init and ANF erasure.

### 3.3 Invsqrt (`src/invsqrt/`)

Implementation details in `build/invsqrt.kmb` (468 KB compiled).

### 3.4 Build Artifacts (`build/`)

| File | Size | Purpose |
|---|---|---|
| `dqi.kmb` | 544 MB | Production DQI circuit (889Q) |
| `dqi_877q.kmb` | 530 MB | Alternative 877Q DQI |
| `dqi_compact_42.kmb` | 828 MB | Tower-42 compact DQI |
| `dqi_full_42.kmb` | 945 MB | Tower-42 full DQI |
| `invsqrt.kmb` | 468 KB | Production Invsqrt (62Q) |
| `r8_words.npy` | 732 KB | R=8 Chemistry factorization words |

### 3.5 Tests (`tests/`)

12 test files covering RiBM, Tower-42, compactor, DQI compiler, portfolio coupling, score engine, quadratic phase erasure, submission validator, pricebook, experiment engine, and inversionless BM.

### 3.6 Verifiers (`verifiers/`)

| Verifier | Path | Lines |
|---|---|---|
| DQI | `verifiers/dqi/verify_submission_dqi.py` | 502 |
| Invsqrt | `verifiers/invsqrt/verify_submission_invsqrt.py` | 403 |
| Chemistry | `verifiers/dfthcsos/verify.py` | 745 |

### 3.7 Incumbent Artifact

| Property | Value |
|---|---|
| File | `submission.zip` |
| Size | 27,066,942 bytes |
| SHA-256 | `0bf5b4e361690c38a9d17580e49bb2d6b5f3706a64500ecaa9f499d2f521c3fe` |
| Verification | QUICK_TEST_PASS (256 DQI shots, 5120 Invsqrt shots) |

---

## 4. Existing Specifications (`berlioz/.spec/`)

| File | Exists | Size |
|---|---|---|
| `PRD.md` | Yes | 1,678 B |
| `TechSpec.md` | Yes | 1,666 B |
| `Architecture.md` | Yes | 1,631 B |
| `AppFlow.md` | Yes | 1,509 B |
| `Rules.md` | Yes | 1,372 B |
| `Tracker.md` | Yes | 1,923 B (14 milestones, all COMPLETED) |
| `Design.md` | Missing | — |
| `Schema.md` | Missing | — |

---

## 5. Previous Masterloop Deliverables (Uncommitted)

24 untracked files from Masterloops 20-23 including RiBM proofs, chemistry R=10 reports, invsqrt 58Q design, MBUC proofs, score frontiers, and dependency graphs. All preserved in working directory.
