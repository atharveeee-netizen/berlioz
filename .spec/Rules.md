# RULES & AGENT DIRECTIVES
## Berlioz — Verifiable Quantum Circuit Compilation Engine

**Framework:** Syzygy Spec-Driven Development Standard (v1.0.0)  

---

### 1. Mandatory Verifier Rules
1. **Zero Tolerance for Unverified Claims:** A lower evidence status must never be represented as a higher one. Theoretical projections do not constitute verified results.
2. **Never Weaken Official Verifiers:** Never lower shot counts, alter confidence bounds, modify error tolerances, or substitute mock tests for official verifier scripts.
3. **Coherent Input Preservation:** All quantum input registers (including the 840 syndrome qubits in DQI and the 22 input bits in invsqrt) must be fully restored upon circuit completion.
4. **Ancilla Projection Rule:** All scratch ancillas must be cleanly projected back to $|0\rangle$ with fidelity $1.0000000000$. Zero residual entanglement is permitted.

---

### 2. Submission Gate & Operational Hygiene
1. **Submission Lock:** Zero submissions permitted during local exploration, optimization, or benchmarking.
2. **Preserve Daily Allowance:** Protect remaining Kaggle daily submissions.
3. **Working Tree Cleanliness:** Clean all intermediate compilation binaries (`.kmb`, `.npz`, scratch scripts) before committing.
4. **Deterministic Hashes:** All submitted archives must be hashed (SHA-256) and verified against clean builds.
