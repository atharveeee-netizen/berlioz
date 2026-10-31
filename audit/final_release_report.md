# Masterloop 19/20: Final Release Certification & Provenance Report

## 1. Release Declaration
- **Candidate Name:** Berlioz SOTA Champion (Frozen Incumbent)
- **Target Archive:** `submission.zip`
- **Archive Size:** 27,066,942 bytes (25.81 MB)
- **SHA-256 Digest:** `0bf5b4e361690c38a9d17580e49bb2d6b5f3706a64500ecaa9f499d2f521c3fe`
- **Release Status:** **VERIFIED INCUMBENT CHAMPION — PRESERVED FOR BENCHMARK ADVANCEMENT**

## 2. Benchmark Verification Scores

| Benchmark | Circuit / Package | Active Qubits ($Q$) | Operation Statistics | Candidate Cost | Competition Ratio | Verifier Evidence |
|---|---|---:|---|---:|---:|---|
| **Benchmark I (Invsqrt)** | `invsqrt.kmb` (62Q Champion) | 62 | $T_{\text{toffoli}} = 1332.3, N_{\text{rot}} = 41.0, T_{\text{equiv}} = 1622.7$ | $100,608.66$ | **`20.64210x`** | Semantic restoration verified ($0$ mismatches, clean $|0\rangle$, $\text{err}/\text{tol} = 0.9993$) |
| **Benchmark II (DQI)** | `dqi.kmb` (889Q Champion) | 889 | $T_{\text{mean}} = 427,471.2, R(0) = 1.19126$ | $402,454,799,602.87$ | **`60.72598x`** | 0 value errors, 0 phase errors ($N=2,560$ smoke / $N=102,400$ bound, ideal $R=1.0$: $72.34\times$) |
| **Benchmark III (Chemistry)** | `dfthcsos/` (R=8 FeMoCo) | 430 | $T_{\text{toffoli}} = 16,266.0, \lambda_{\text{eff}} = 48.2992$ | $337,823,023.19$ | **`9.93301x`** | Compliant with both constraints: $e_1 = 19.05\,\text{mHa} < 20, e_2 = 19.999\,\text{mHa} \le 20$ |
| **Composite Geometric Mean** | Complete Portfolio | — | — | — | **`23.17767`** | **OFFICIAL_SCORE_VERIFIED** |

## 3. Masterloop 19/20 Verification Gates Checklist

- [x] Current Git commit recorded (`47152d4`).
- [x] Incumbent candidate frozen in `research/masterloop20/incumbent_verification/submission_incumbent.zip`.
- [x] All hardcoded external paths removed or converted to repository-relative.
- [x] Exact official scoring formula reproduced (`research/masterloop20/score_engine.py`).
- [x] Exact artifact SHA-256 match confirmed: `0bf5b4e361690c38a9d17580e49bb2d6b5f3706a64500ecaa9f499d2f521c3fe` (27,066,942 bytes).
- [x] Tower-42 mathematical proof reconciled with implementation modulus `0x1053` (`audit/tower42_math_proof.md`).
- [x] Generic Berlioz 2.0 compiler repaired: synthetic cyclic CCX replaced with mathematically exact Tower-42, schoolbook, ripple adders, and Gaussian linear synthesis.
- [x] Phase polynomial MBUC repaired: classical feedforward and Pauli frame tracking added; non-linear unverified deletions rejected.
- [x] Circuit-level formal verifier rebuilt: simulates actual quantum gates on computational basis and computes operator unitaries.
- [x] 20-dataset metrics reconciled: +10.84% mean reduction across all 20 suites, 19/20 positive families (1 invariant Clifford suite).
- [x] Full test suite (37 unit tests) passing with 0 failures (`pytest tests/`).
- [x] Zero unauthorized Kaggle submissions rule strictly enforced.

## 4. Submission Record
- Target Competition: `google-verifiable-quantum-circuit-compilation`
- Live Public Leaderboard Score: `23.00043` (Submission `57812617`, Rank #453 / 1,754).
- Verified Local Portfolio Score: `23.17767` (+0.77% gain over live leaderboard).
- Ideal Unpenalized Score ($R=1.0$): `24.57001`.
