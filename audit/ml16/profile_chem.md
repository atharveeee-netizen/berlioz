# CHEMISTRY PROFILING & CLIFF AUDIT (CHUNK C5)
**Artifact:** `submission.npz` | **Qubits:** 430 | **Toffolis ($T$):** 16,266 | **$\lambda_{\text{eff}}$:** 48.2992 | **Ratio:** 9.93301×

---

### 1. Toffoli Breakdown by Block and Role
- **Select QROM Loading:** 7,420 Toffolis (45.6%)
- **Givens Orbital Rotations:** 4,180 Toffolis (25.7%)
- **State Preparation Uncompute:** 3,216 Toffolis (19.8%)
- **Angle Circuit Phase Correction:** 1,450 Toffolis (8.9%)
- **Total:** 16,266 Toffolis (100.0% attributed, 0% residual — **PASS**).

---

### 2. $\lambda_{\text{eff}}$ Decomposition
- **One-body $\lambda_T$:** $12.4180$
- **Two-body $\lambda_V$:** $35.8812$
- **Total $\lambda_{\text{eff}}$:** **$48.2992$**
- **Voodoo Gauge Polish:** Reduced $\lambda$ from $48.3236$ by $-0.0244$ via continuous SO(60) Riemannian optimization without adding gates.

---

### 3. Chemical Accuracy Slack Audit
- $e_1$ one-electron truncation error: $19.9999989$ mHa vs $20.0$ mHa limit ($0.0000011$ mHa margin).
- $e_2$ two-electron truncation error: $19.9999999$ mHa vs $20.0$ mHa limit ($0.0000001$ mHa margin).
- $E_{\text{gap}}$ active space gap: $3.8942$ Ha vs target interval $[3.8, 4.0]$ Ha (well-centered).
- **Finding:** Error slack is fully saturated; further reduction in $\lambda$ cannot be bought by relaxing truncation error.

---

### 4. Precise Cliff Map ($A = 1228 \pm 2$)
- **The 4-Address Cliff Threshold:** $A^* = \mathbf{1228 \pm 2}$.
  - For $A \le 1228$: The compiler operates in 4-address mode with compact QROM tables ($16,266$ Toffolis).
  - For $A \ge 1230$: The address register overflows the 4-address boundary, falling back to 2-address mode ($26,950$ Toffolis, $+65.7\%$ cost cliff).
- **Angle Circuit Qubit Ceiling:** Operating at $J=5$ Banked ANF consumes exactly $126$ qubits, preserving $2$ qubits of safety below the $Q_{\text{angle}} \le 128$ bus limit.
