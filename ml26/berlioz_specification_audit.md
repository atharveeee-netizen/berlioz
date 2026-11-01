# Berlioz Specification Audit — Masterloop 26 Part 1.3

**Date:** 2026-10-31T15:19Z
**Evidence class:** E1 (Direct source evidence)

---

## Existing Specifications

Berlioz already has 6 of 8 SDD files in `.spec/`:

| File | Status | Content Summary |
|---|---|---|
| `PRD.md` | ✅ Present | Problem statement, 3 benchmarks, composite score formula, stretch targets |
| `TechSpec.md` | ✅ Present | kickmix API, GF(2^12), Tower-42, QROM, Newton-Raphson |
| `Architecture.md` | ✅ Present | Pipeline: Source → Compiler → KMB → Verifier → Score |
| `AppFlow.md` | ✅ Present | Build → Verify → Score → Submit flow |
| `Rules.md` | ✅ Present | Agent rules, evidence classification, submission gates |
| `Tracker.md` | ✅ Present | 14 milestones, all COMPLETED through ML18 |
| `Design.md` | ❌ Missing | Not applicable (no GUI). Will not be created. |
| `Schema.md` | ❌ Missing | Needed for experiment registry and candidate lifecycle. |

---

## Assessment

The existing specs accurately describe the real project. The PRD correctly states:
- Composite score = (R_inv × R_dqi × R_chem)^(1/3)
- Score floor S ≥ 23.000
- Stretch targets S ≥ 25.000 and S ≥ 26.800

**Action items for ML26:**
1. Create `Schema.md` defining experiment registry, candidate lifecycle states, and research memory schemas.
2. Update `Tracker.md` with ML26 milestones.
3. Do NOT create `Design.md` — not applicable to a quantum circuit compiler project.
4. All other specs remain valid and do not need modification at this time.
