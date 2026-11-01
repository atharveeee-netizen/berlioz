# Masterloop 26 Discrepancy Register — Part 2.3

**Date:** 2026-10-31T15:33Z  
**Standard:** Syzygy Spec-Driven Development Standard (v1.0.0)  
**Status:** All 8 known discrepancies identified, audited, and resolved with direct evidence.  

---

## Discrepancy Catalog

| ID | Category | Discrepancy Description | Root Cause | Status / Resolution | Evidence Class |
|---|---|---|---|---|---|
| **DISC-01** | Artifact Hash | `build/dqi.kmb` hash does not match `submission.zip[dqi.kmb]`. | `build/dqi.kmb` is the older ML16 baseline (544MB, SHA-256 `7a378f47...`, 433,783.5 Toffolis). `submission.zip[dqi.kmb]` is the ML20-23 champion (534MB, SHA-256 `73e1b187...`, 427,471.2 Toffolis). | **RESOLVED:** `submission.zip[dqi.kmb]` is the authoritative INCUMBENT. | E1 + E2 |
| **DISC-02** | Artifact Hash | `fact/r8_champion/submission.npz` hash does not match `submission.zip[dfthcsos/submission.npz]`. | `fact/r8_champion` holds the ML16 weights ($\lambda_{\text{eff}} = 48.3236$). `submission.zip` holds the ML20 gauge-optimized weights ($\lambda_{\text{eff}} = 48.2992$). | **RESOLVED:** `submission.zip` is the authoritative INCUMBENT with lower cost. | E1 + E2 |
| **DISC-03** | Score / Metric | Historical notes claim a "386k Toffoli" DQI implementation. | Speculative forward-pass projection omitting uncomputation or an unverified early termination hypothesis. | **RESOLVED / FALSIFIED:** No compiled artifact achieves 386k with complete uncomputation. Authoritative measured dynamic mean is **427,471.2 Toffolis**. | E2 + E5 |
| **DISC-04** | Score / Metric | DQI ratio cited as both 72.34x and 60.73x. | Mathematical distinction between unpenalized theoretical cost ($R=1.0 \implies 72.33966\times$) and official Clopper-Pearson penalized cost ($R=1.19126 \implies 60.72598\times$). | **RESOLVED:** Mathematical identity $72.33966 / 1.19126046 = 60.72598$. Official score strictly uses 60.72598x. | E1 + E3 |
| **DISC-05** | Verification | Quick DQI verification with $N=256$ shots raises `AssertionError: Effective error rate 0.2929 >= 1/16`. | Exact Clopper-Pearson formula $\epsilon_+ = 1 - 2^{-128/N}$. For $\epsilon_+ < 1/16$, $N > 1,374.7$. At $N=256$, $\epsilon_+ = 0.2929$ even with zero errors. | **RESOLVED:** 256 shots can measure mean Toffolis and confirm zero value/phase errors, but official `verify()` requires $N \ge 1536$ (or $N=102,400$ for full benchmark). | E1 + E2 + E3 |
| **DISC-06** | Documentation | `audit/invsqrt_champion_report.md` states $T_{\text{per\_toffoli}} = 2.0$. | Documentation typographical error. Official verifier `verify_submission_invsqrt.py` line 65 sets `T_PER_TOFFOLI = 4`. `score_calc.py` and evaluation code correctly use 4. | **RESOLVED:** Authoritative formula is $T_{\text{per\_toffoli}} = 4$. | E1 |
| **DISC-07** | Verification | Full Invsqrt verification scope is $200,540,928$ shots ($64 \times 3,133,452$). | Testing all 3.13M domain values $\times$ 64 shots requires $> 100$ CPU-hours. | **RESOLVED:** Local verification uses representative boundary states and stratified random samples (1,024 to 5,120 shots). Full verification reserved for release certification. | E1 |
| **DISC-08** | Provenance | Kaggle public leaderboard champion graded at 23.00043, while local frozen champion is 23.17767. | Local champion `submission.zip` was completed in ML20 and marked `PENDING_HUMAN_TRIGGER` per Rule 0.6 (no automatic submissions). | **RESOLVED:** Preserved in candidate registry. Human trigger required to submit to Kaggle. | E1 + E2 |

---

## Detailed Notes on Key Discrepancies

### DISC-03: The 386k DQI Claim
In Masterloop 22 documentation, notes referenced moving toward 340.6k while mentioning a "386k claim". An exhaustive search of all compiled `.kmb` files in `build/`, `audit/`, and `scratch/` reveals:
- `build/dqi.kmb`: 441,968 static / 433,783.5 dynamic Toffolis.
- `submission.zip[dqi.kmb]`: 441,968 static / 427,471.2 dynamic Toffolis.
- `build/dqi_compact_42.kmb`: Prototype, 560,000+ Toffolis.
- `build/dqi_877q.kmb`: Prototype, 439,000+ Toffolis.

No compiled circuit exists in the repository with $\le 386\text{k}$ Toffolis that passes verification. The 386k figure is classified as **E5 (Falsified Historical Projection)**. The authoritative baseline is **427,471.2 Toffolis**.

### DISC-05: Clopper-Pearson Finite-Sample Behavior
The DQI verifier applies the one-sided Clopper-Pearson upper bound with confidence parameter $\delta = 2^{-128}$.
For zero failures ($k=0$):
$$\epsilon_+(N) = 1 - 2^{-128 / N}$$
The repetition factor $R(\epsilon_+)$ is defined as:
$$R(\epsilon_+) = \frac{\ln 2}{-\ln\left(\frac{1}{2} + 2\sqrt{\epsilon_+}\right)}$$
The argument $\frac{1}{2} + 2\sqrt{\epsilon_+}$ must be strictly $< 1$, which requires $\sqrt{\epsilon_+} < \frac{1}{4} \iff \epsilon_+ < \frac{1}{16} = 0.0625$.

Evaluating this for various sample sizes $N$:
- $N = 256 \implies \epsilon_+ = 0.292893 \ge 1/16 \implies \mathbf{FAIL}$ (`AssertionError`)
- $N = 512 \implies \epsilon_+ = 0.159104 \ge 1/16 \implies \mathbf{FAIL}$
- $N = 1024 \implies \epsilon_+ = 0.082996 \ge 1/16 \implies \mathbf{FAIL}$
- $N = 1536 \implies \epsilon_+ = 0.056126 < 1/16 \implies \mathbf{PASS}, R = 26.1253$
- $N = 2048 \implies \epsilon_+ = 0.042397 < 1/16 \implies \mathbf{PASS}, R = 7.5077$
- $N = 102400 \implies \epsilon_+ = 0.000866 < 1/16 \implies \mathbf{PASS}, R = 1.19126046$

This proves that quick verification of DQI cannot use the default verifier assertion threshold unless $N \ge 1536$ shots are simulated. For quick tests ($N=256$), the test harness must evaluate error count ($k=0$) and mean Toffolis directly, and apply the benchmark-standard $R(102400) = 1.19126046$.
