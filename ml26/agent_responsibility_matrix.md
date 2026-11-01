# Agent Responsibility Matrix — Masterloop 26 Part 1.4

**Date:** 2026-10-31T15:19Z

---

## Implementation Note

SYZYGY's agent framework is designed for generic project scaffolding (web apps, IoT, hackathons) and cannot directly support quantum circuit research roles. The following roles are implemented as **explicit workflow definitions** — structured responsibility assignments enforced by the human-agent pair, not fabricated autonomous agents.

---

## Role Definitions

| Role ID | Role Name | Responsibilities | Cannot Self-Certify |
|---|---|---|---|
| `RL` | Research Lead | Literature search, competitor methods, public notebooks, mathematical alternatives, research registry curation | Own experiment results |
| `DQI-A` | DQI Architect | RiBM, projective decoder, additive FFT, direct decoding, GF(2^12) arithmetic, reversible decoder design | Own correctness claims |
| `CHEM-A` | Chemistry Architect | Factorization search, QROM design, banking, pebbling, ANF erasure, exact-gauge methods | Own verification results |
| `INV-A` | Invsqrt Architect | Approximation theory, range reduction, polynomial evaluation, rotation synthesis, workspace optimization | Own error bound claims |
| `RC-A` | Reversible Compiler Architect | Reversible scheduling, temporary AND, MBUC, arithmetic synthesis, ancilla allocation, global pebbling | Own resource claims |
| `IV` | Independent Verification Agent | Classical equivalence, quantum semantics, phase correctness, ancilla cleanup, benchmark verification | — (verifies all others) |
| `RA` | Resource Auditor | Official cost functions, resource accounting, Pareto frontiers, composite score calculation | Own cost calculations (must be verified by IV) |
| `REL` | Release Auditor | Artifact integrity, source provenance, ZIP packaging, reproducibility, build instructions | — |

---

## Ownership Rules

1. An implementation agent (DQI-A, CHEM-A, INV-A, RC-A) **cannot** certify the correctness of its own implementation.
2. All correctness claims must be verified by IV using independent evidence.
3. All resource claims must be verified by RA using official cost functions.
4. Release packaging must be verified by REL independently.
5. Research hypotheses (RL) must be backed by E1–E3 evidence before implementation begins.

---

## Practical Execution

In the current Antigravity execution environment:
- All roles are executed by the same Gemini agent.
- Role separation is enforced through **sequential workflow phases**: implement → verify → audit → certify.
- No phase may be skipped.
- Verification evidence must be recorded separately from implementation evidence.
- A candidate is never promoted in the same step that created it.
