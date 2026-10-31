# MASTERLOOP 16 EXPERIMENT RUNNER & REPRODUCIBILITY REPORT

**Harness:** Integrated Official Benchmark Verification Suite (`audit/integrated_verification_suite.py`)  
**Environment:** Python 3.12 64-bit on Windows x86_64, C++ Kickmix Backend  
**Git HEAD:** `f01cd3a70275be5f7b4ea39ef678d46fcfd74659`  

---

## 1. REPRODUCIBLE EXPERIMENT HARNESS

All benchmark experiments in Masterloop 16 are executed through the standalone canonical verifier harness:
- **No external sibling-repository dependencies:** All imports reference repository-local modules (`src/`, `official_eval/`, `extracted_dqi/`).
- **No hardcoded user paths:** All paths resolved relative to `git rev-parse --show-toplevel`.
- **Deterministic RNG & Salt Handling:** Verification runs use standardized test batches (5,120 shots for invsqrt, 256 shots for DQI, full orbital evaluation for chemistry).

---

## 2. EXECUTED EXPERIMENT SUITE SUMMARY

| Experiment ID | Benchmark | Candidate Evaluated | Q | Gate Metric | Ratio | Status |
|---|---|---|---|---|---|---|
| `EXP-ML16-01` | Portfolio | Baseline Champion | Mixed | Official Cost Suite | 23.0606 | VERIFIED |
| `EXP-ML16-02` | DQI | 11-Stage Tracing | 889 | 433,794 Dynamic Toffolis | 59.8409 | VERIFIED |
| `EXP-ML16-03` | DQI | Syndrome Recycling 740Q | 740 | - | Infeasible | FALSIFIED |
| `EXP-ML16-04` | DQI | Tower-42 Arithmetic | - | 42 Toffolis, 63 CNOTs | - | VERIFIED |
| `EXP-ML16-05` | DQI | Tower-42 Full Binary | 889 | 433,794 Dynamic Toffolis | 59.8409 | VERIFIED |
| `EXP-ML16-06` | Invsqrt | 41-Rotation Profile | 62 | 1,622.7 T_equiv | 20.6421 | VERIFIED |
| `EXP-ML16-07` | Chemistry | R=8 J=5 Banked ANF | 430 | 16,266 Toffolis | 9.9280 | VERIFIED |

---

## 3. SCRATCH BINARY MANAGEMENT & DISCIPLINE

All temporary compilation artifacts (`temp_dqi.kmb`, `temp_dqi_tower42.kmb`) generated during experimental builds were:
1. Verified semantically.
2. Verified against the official scoring module.
3. Completely purged from the repository tree to keep `git status` perfectly clean.
4. Recorded in `research/ml16_experiment_registry.json`.
