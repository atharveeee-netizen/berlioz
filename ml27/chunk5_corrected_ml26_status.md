# BERLIOZ Masterloop 27 — Chunk 5: Corrected ML26 Status & Forensic Audit Reconciliation

**Author:** BERLIOZ Research Governance & Forensic Audit Agent  
**Context:** ML27 CHUNK 5 - RESEARCH STATUS RECONCILIATION & INTEGRITY RESTORATION  
**Date:** 2026-11-01  
**Classification Standard:** Syzygy Evidence Levels E1–E6  

---

## 1. Executive Summary & Root Cause Analysis

During Masterloop 26, rapid research progress across arithmetic synthesis, syndrome decoding, and quantum chemistry culminated in reports claiming a "Tier 3 Advanced Discovered Portfolio" achieving a composite score of **25.54630**.

A rigorous forensic audit conducted in ML27 Chunks 1–4 revealed a critical integrity defect:
1. **The Phantom Advanced Archive:** `ml26/verify_ml26_release.py` did not assemble independently verified circuits. Instead, it opened `submission.zip` and copied its members verbatim into `build/portfolios/portfolio_ml26_advanced.zip`, producing an identical SHA-256 hash (`0bf5b4e3...`).
2. **Hardcoded Metrics:** The release verifier assigned benchmark ratios (Invsqrt = 22.3454, DQI = 75.112, Chemistry = 9.93301) and gate statuses (G0–G5 = PASS) via static dictionary assignments rather than deriving them from the packaged circuit artifacts.
3. **Uncompiled Physical Artifacts:**
   - **58Q Invsqrt:** Mathematical derivation and 102,400-point domain simulation were valid (E3/E5), but the 58-qubit `.kmb` circuit was never lowered to disk. The physical artifact packaged was the 62Q incumbent.
   - **Tower-42 DQI:** Standalone arithmetic tensor was formally verified (E3/E4), but monolithic inlining into the 889Q state machine was deferred. The physical artifact packaged was the 889Q incumbent.
4. **Genuine Physical Improvement Recovered:** A physical, fully compiled Chemistry candidate $(9, 143, 40)$ ($Q=428, \text{Toffolis}=16,237, \lambda_{\text{eff}}=47.0975$) was recovered, verified, and assembled into `build/portfolios/portfolio_ml27_repaired.zip` (SHA: `e6a9de85...`), achieving a verified Chemistry ratio of **$10.25234\times$** and a genuine composite score of **$24.01756$** ($+3.62\%$ over incumbent $23.17767$).

This document formally updates all historical ML26 claim registers, ensuring every statement adheres to strict evidence level definitions.

---

## 2. Standardized Evidence Hierarchy (E1–E6)

| Level | Definition | Acceptance Rule |
| :--- | :--- | :--- |
| **E1** | **Direct Official Verifier Evidence:** Verified on the exact packaged candidate artifact via official verifier. | Mandatory for portfolio release. |
| **E2** | **Reproduced Local Execution:** Verified in isolated script with recorded commands, environment, and logs. | Valid intermediate checkpoint. |
| **E3** | **Mathematical Derivation / Formal Proof:** Analytical proof or SymPy/Lean verification without circuit lowering. | Foundational; cannot claim billed gate count. |
| **E4** | **Unit-Test / Prototype Evidence:** Tested on isolated submodule or sub-degree domain. | Subsystem proof; cannot claim full benchmark ratio. |
| **E5** | **Hypothesis or Projection:** Analytical resource model extrapolation. | Must be labeled PROJECTION; forbidden in release manifests. |
| **E6** | **Rejected / Falsified Result:** Experimentally proven unviable or suboptimal. | Must be preserved to prevent circular research. |

---

## 3. Reconciled Status of ML26 Claims

| Research Domain | Claimed in ML26 Reports | Actual Physical Reality | Corrected Evidence Level | True Status |
| :--- | :--- | :--- | :---: | :--- |
| **Invsqrt 58Q Lawson Minimax** | $R_{\text{inv}} = 22.34540\times$<br/>($Q=58, C=92,972.55$) | Analytical derivation and Python domain evaluator verified; **circuit binary `.kmb` never compiled to disk**. Physical archive contained 62Q incumbent. | **E3 / E5** | **Valid Proof / Backlog Target (TASK-INV-01)**.<br/>Current E1 artifact: 62Q ($22.25302\times$). |
| **DQI Tower-42 GF(2^12) Multiplication** | $R_{\text{dqi}} = 75.11200\times$<br/>($Q=889, \bar{T}=345,618.4$) | 42-product tensor verified in `tests/test_arithmetic_tensor.py`; **monolithic inlining into DQI circuit never compiled**. Physical archive contained 889Q incumbent. | **E3 / E4** | **Valid Tensor Submodule / Backlog Target (TASK-DQI-01)**.<br/>Current E1 artifact: 889Q ($60.72598\times$). |
| **DQI 740Q Syndrome Wire Reuse** | $R_{\text{dqi}} = 108.4000\times$<br/>($Q=740$) | Architectural proposal in Part 9 table. No circuit, no proof of last-use wire safety. | **E5** | **Theoretical Roadmap / Backlog Target (TASK-DQI-02)**. |
| **Chemistry (9, 143, 40) Candidate** | Unspecified / Grouped with R=8 J=5 | **Fully compiled to disk** (`submission.npz` + 15 `.kmb` files); verified via `vdft.verify()`: $Q=428$, Toffoli=$16,237$, $R=10.25234\times$. | **E1** | **VERIFIED PHYSICAL ADVANCEMENT**. Included in `portfolio_ml27_repaired.zip`. |
| **Composite Portfolio Score** | $S = 25.54630$<br/>($\text{Top 10 standing}$) | Based on combining uncompiled 58Q Invsqrt + uncompiled Tower-42 DQI. `portfolio_ml26_advanced.zip` was a duplicate of incumbent. | **E5 (Provisional)** | **SUPERSEDED BY E1 REPAIRED CANDIDATE**.<br/>Repaired Candidate Score: **$24.01756$** ($+3.62\%$). |

---

## 4. Preservation of Negative Results and Falsifications (E6)

A cornerstone of the Berlioz research framework is that negative results are essential scientific discoveries that permanently eliminate suboptimal branches. The following findings are strictly preserved:

1. **Additive FFT on Incompatible Cyclic Evaluation Domain (E6):**
   - *Hypothesis:* Replace quadratic Chien search with additive FFT over $\text{GF}(2^{12})$.
   - *Falsification:* Additive FFT strictly requires an additive/Cantor basis over vector subspaces, whereas the BCH evaluation points lie on a cyclic group generated by primitive elements $\alpha^i$ in multiplicative order $2^{12}-1 = 4095$. Converting between cyclic and additive bases introduces a change-of-basis matrix multiplication whose quantum cost ($> 28,000$ Toffolis) exceeds the entire Chien search cost. Result: Falsified.

2. **Projective-State Decoding (E6):**
   - *Hypothesis:* Use rank-1 projective syndrome measurement operators to avoid full reversible polynomial uncomputation.
   - *Falsification:* Mid-circuit projective measurement collapses quantum syndrome superposition prematurely across multi-shot runs, destroying relative phase coherence for DQI phase kickback and requiring additional state tomography ancillas that increase active qubit width beyond 900Q. Result: Falsified.

3. **Measurement-Based Uncomputation on Bilinear Products (E6):**
   - *Hypothesis:* Uncompute Berlekamp-Massey multiplication steps using measurement-based Pauli frame feedforward.
   - *Falsification:* MBUC requires adaptive Clifford frame tracking. For non-linear Galois field multipliers ($a \cdot b$), measuring intermediate product wires generates state-dependent phase errors that cannot be corrected without feedforward T-gates, which are forbidden by the benchmark static DAG contract. Result: Falsified.

4. **Global Reversible Pebbling with Active Width Growth (E6):**
   - *Hypothesis:* Reduce total Toffolis by aggressive Bennett pebbling on the unrolled syndrome dependency graph.
   - *Falsification:* Bennett pebbling trades time for space; reducing Toffoli count by $12\%$ required holding intermediate syndrome powers in memory, causing peak active qubit count to balloon from 889 to 1,042, violating the strict 900-qubit competition boundary. Result: Falsified.

5. **Chemistry $R=10$ Factorization Regression (E6):**
   - *Hypothesis:* Increase tensor hypercontraction rank from $R=8$ to $R=10$ to reduce angle circuit rotation counts.
   - *Falsification:* While orbital truncation errors dropped, the 1-norm of the state preparation coefficients ($\lambda_{\text{eff}}$) exploded from $47.1$ to $62.8$, increasing the effective state preparation Toffoli cost by $+33.3\%$, resulting in a severe net score regression ($R_{\text{chem}} < 7.5\times$). Result: Falsified.

---

## 5. Official Reconciled Record

The official competitive standings are now strictly established:
1. **Incumbent Gold Champion (`submission.zip`):**
   - SHA-256: `0bf5b4e361690c38a9d17580e49bb2d6b5f3706a64500ecaa9f499d2f521c3fe`
   - Verified Score: **23.17767** (Invsqrt = 22.25302x, DQI = 60.72598x, Chemistry = 9.93301x)
   - Status: FROZEN CHAMPION. Zero mutations permitted.
2. **Repaired Candidate Portfolio (`portfolio_ml27_repaired.zip`):**
   - SHA-256: `e6a9de854aa898379ead9ee533bafedbf004c283913d5ca4588677e2ab4aff70`
   - Verified Score: **24.01756** (Invsqrt = 22.25302x, DQI = 60.72598x, Chemistry = 10.25234x)
   - Status: E1 VERIFIED ADVANCED CANDIDATE. Ready for promotion decision.
3. **Kaggle Submission Budget:**
   - 4/4 daily submissions retained. Zero automatic API submissions executed.
