# Masterloop 27 — Chunk 2: Advanced Candidate Component Recovery Report

**Date:** 2026-11-01T05:10:00Z  
**Execution Environment:** Antigravity IDE, Windows x86_64  
**Framework:** Syzygy Spec-Driven Autonomous Co-Design Standard (v1.0.0)  

---

## 1. Executive Summary

This report performs an uncompromising forensic search across the Berlioz repository to locate, verify, and authenticate the physical artifacts behind the reported advanced candidate metrics from Masterloop 26:
- **Invsqrt:** Claimed $Q=58$, Cost $92,972.55$, Ratio $22.3454\times$.
- **DQI:** Claimed $Q=889$, Mean Toffolis $345,618.4$, Ratio $75.112\times$.
- **Chemistry:** Claimed $Q=430$, Toffolis $16,266$, Ratio $9.93301\times$.

---

## 2. Benchmark-by-Benchmark Forensic Findings

### 2.1 Invsqrt: The 58Q Lawson Minimax Investigation
- **Mathematical Derivation (E3):** Verified in [`ml26/invsqrt_58q_reclamation_proof.md`](file:///c:/Users/noobg/.gemini/antigravity-ide/scratch/berlioz/ml26/invsqrt_58q_reclamation_proof.md). The proof demonstrates that lower 2 bits of range normalization can be reused for 4-subinterval indexing, and top-carry folded into the Horner accumulator.
- **Numerical Full-Domain Simulation (E2/E4):** Verified in [`ml26/invsqrt_candidate_evaluator.py`](file:///c:/Users/noobg/.gemini/antigravity-ide/scratch/berlioz/ml26/invsqrt_candidate_evaluator.py) across $102,004$ points. Maximum relative error is $6.1057 \times 10^{-9}$ (limit: $5.9605 \times 10^{-8}$), passing all precision constraints.
- **Physical Circuit Binary (`.kmb`):** **NOT AVAILABLE (E5: Model Projection).**
  - Scanning all 115 circuit binaries in [`ml27/chunk0_artifact_inventory.json`](file:///c:/Users/noobg/.gemini/antigravity-ide/scratch/berlioz/ml27/chunk0_artifact_inventory.json) reveals only 62Q circuits (`a568bc79...`) and 63Q circuits (`0766a111...`).
  - No standalone `invsqrt_58q.kmb` was ever compiled to disk.
- **Smallest Reproducible Route to Rebuild:**
  Implement the compiler lowering pass in `src/berlioz_v2/compiler/two_level_compiler.py` to emit the 58-qubit instruction stream and compile to `build/invsqrt_58q.kmb` via Kickmix.

### 2.2 DQI: The Tower-42 Multiplier Investigation
- **Mathematical & Algorithmic Formulation (E3):** Derived in `audit/tower42_math_proof.md` and implemented in [`src/dqi/tower42.py`](file:///c:/Users/noobg/.gemini/antigravity-ide/scratch/berlioz/src/dqi/tower42.py). Decomposes $\text{GF}(2^{12})$ multiplication over $\text{GF}(8)[v]/(v^4+v+1)$ into 42 bilinear multiplications.
- **Standalone Tensor Unit Test (E2):** Verified in [`tests/test_arithmetic_tensor.py`](file:///c:/Users/noobg/.gemini/antigravity-ide/scratch/berlioz/tests/test_arithmetic_tensor.py). All 42 products match classical ground truth with zero value and phase errors.
- **Monolithic Inlined DQI Binary (`dqi.kmb`):** **NOT AVAILABLE (E5: Model Projection).**
  - The $75.112\times$ ratio was derived by analytically replacing 144 naive bilinear products with 42 in the DQI mean cost model ($427,471.2 \to 345,618.4$ Toffolis).
  - The monolithic 534 MB `dqi.kmb` state machine binary was never reinlined. In fact, Part 11 of ML26 explicitly registered this in the backlog as:
    `TASK-DQI-01: Inline Tower-42 State Machine Lowering (Target Ratio: 75.11x)`.
- **Existing Physical Binaries:**
  - `audit/frozen_incumbent_dqi/dqi.kmb`: $Q=889$, $T_{\text{mean}}=427,471.2$, Ratio $60.72598\times$ (Certified Incumbent).
  - `build/dqi_877q.kmb`: $Q=877$, $T=500,054$, Ratio $54.80\times$ (Rejected, higher cost).
  - `build/dqi_compact_42.kmb`: $Q=1907$, $T=5,044,893$ (Rejected, width blowup due to unpebbled intermediate wires).
- **Smallest Reproducible Route to Rebuild:**
  Execute `TASK-DQI-01`: Direct in-place lowering of `tower42` into the modular conversion and synthesis stages of `src/dqi/` without allocating global persistent scratch registers.

### 2.3 Chemistry: Recovered & Verified Components
- **Incumbent Component ($R=8, J=5$):**
  - Path: `submission.zip:dfthcsos/`
  - Total Qubits: $Q = 430$, Toffolis: $16,266$, $\lambda_{\text{eff}} = 48.3236$.
  - Official Chemistry Ratio: **$9.93301\times$**.
  - Status: **E1 (Directly Certified & Verified)**.
- **Newly Recovered Advanced Candidate ($R=9, B=143, C=40$):**
  - Source: Helios Li & Lera (`heliosli_ds/dfthcsos__submission.npz` and 15 angle circuits).
  - Total Qubits: $Q = 428$, Toffolis: $16,237$, $\lambda_{\text{eff}} = 47.0975$.
  - Official Chemistry Ratio: **$10.25234\times$** (Score: $327,300,810.34$).
  - Official Verifier Status: **E2 (Verified Live via Task 303 in Kickmix)**.
  - Status: **Genuinely Available & Superior Candidate (+3.2% over incumbent)**.

---

## 3. Reconciliation of Evidence Classification

| Component | Target Architecture | Claimed Ratio | Verified Status | True Evidence Tier | Real Artifact Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Invsqrt** | 58Q Lawson Minimax | $22.3454\times$ | Model Projected | **E3 / E5** | Missing standalone `.kmb` |
| **Invsqrt** | 62Q NR Seed Table | $20.6421\times$ | Officially Verified | **E1** | [`submission.zip:invsqrt.kmb`](file:///c:/Users/noobg/.gemini/antigravity-ide/scratch/berlioz/submission.zip) |
| **DQI** | 889Q Inlined Tower-42 | $75.1120\times$ | Model Projected | **E3 / E5** | Missing inlined monolithic `.kmb` |
| **DQI** | 889Q Fused Decoder | $60.72598\times$ | Officially Verified | **E1** | [`submission.zip:dqi.kmb`](file:///c:/Users/noobg/.gemini/antigravity-ide/scratch/berlioz/submission.zip) |
| **Chemistry** | $R=8, J=5$ 4-Addr | $9.93301\times$ | Officially Verified | **E1** | [`submission.zip:dfthcsos/`](file:///c:/Users/noobg/.gemini/antigravity-ide/scratch/berlioz/submission.zip) |
| **Chemistry** | $R=9, C=40, J=5$ | $10.25234\times$ | Officially Verified | **E2** | `scratch/heliosli_ds/` |

Chunk 2 is complete. All physical artifact realities are mapped without speculation or invented evidence.
