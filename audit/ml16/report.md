# MASTERLOOP 16 REPORT: PRICE · MEASURE · SEARCH · CALIBRATE

1. **Commits:** Start `f01cd3a` | Current `7800e6e` | Branch `ml16` / `master`.
2. **Lane Summary:**
   - Lane A (Multiplier Swap): VERIFIED_EQUIVALENT. ΔQ=0, ΔT=0, ΔCNOT=-357 (-85%). Evidence: `audit/tower42_dqi_integration.md`.
   - Lane B (DQI Rarity & Pricing): LANDED_NEW_SOTA. ΔQ=0, ΔT_mean=-6,322.9 (-1.48%), DQI ratio 59.84x -> 60.73x. Evidence: `audit/ml16/lanes.jsonl`.
   - Lane C (DQI Width): KILLED. Q < 840 impossible under coherent syndrome preservation. Evidence: `audit/dqi_recycling_proof.md`.
   - Lane D (Invsqrt): RETAINED. 62Q MBUC strictly superior to 78Q coalesced (+10.1% worse). Ratio 20.64210x. Evidence: `audit/invsqrt_phase_factorization.md`.
   - Lane E (Chemistry): LANDED_NEW_SOTA. ΔQ=0, ΔT=0, Δlambda=-0.0244, Chem ratio 9.928x -> 9.933x. Evidence: `audit/ml16/lanes.jsonl`.
   - Lane F (Search Harness): OPERATIONAL. Evaluator-guided loop deployed. Evidence: `src/syzygy_ai_quantum_optimizer.py`.
3. **Per-Benchmark Before vs After:**
   - Invsqrt: 20.64210x -> 20.64210x (Cost: 100,608.66)
   - DQI: 59.84086x -> 60.72598x (Cost: 408,407,643,922 -> 402,458,332,610)
   - Chemistry: 9.92799x -> 9.93301x (Cost: 337,993,967 -> 337,823,023)
4. **Local Composite Score:**
   - Before: 23.06062
   - After: **23.17767** (Gain: +0.11705 points, +0.508%)
5. **Kaggle Ledger:**
   - 57800637: Graded 22.99562
   - 57811741: Graded 22.80575
   - 57812617: Graded 23.00043 (Historical best)
   - 57823923: Graded 22.99562
   - Current Champion: **23.17767** (Unsubmitted, locked)
6. **Flaw Register:** F1–F11 ALL CLOSED with evidence in `audit/ml16/flaws_and_resolutions.md`.
7. **Best Candidate Artifact:** `submission.zip` (SHA-256: `0bf5b4e361690c38a9d17580e49bb2d6b5f3706a64500ecaa9f499d2f521c3fe`).
8. **Submissions Left Today:** 4 daily submissions remaining. Submission lock active.
9. **Ranked Backlog for ML17/ML18:**
   - Priority 1: MBUC phase-peeling for DQI backward uncompute (247k Toffolis, worth up to +6.5 score points).
   - Priority 2: 20-dataset cross-generalization framework.
   - Priority 3: Angle circuit grouping for chemistry (16 -> 12 circuits under Q_angle <= 128).
10. **Unexplained:** Residual variance of ~0.005 on Kaggle public leaderboard across identical payloads explained by Monte Carlo syndrome sample variance.
