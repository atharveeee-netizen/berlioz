# BERLIOZ — NEGATIVE RESULTS & FALSIFIED HYPOTHESES LEDGER
## Masterloop 11 Post-Mortem and Failure-First Analysis

In scientific research, negative results are as valuable as positive discoveries. Recording exactly why an intuitive or mathematically promising approach failed prevents costly regressions and preserves the integrity of the live submission portfolio.

---

### NEG-001: The $R=10$ Continuous Factorization Trap

- **Date:** 2026-10-30
- **Context:** Transition from $R=8, B=143, C=60$ factor matrix to $R=10, B=129, C=60$ (`fact/dfthc_r10_b129_c60_brot8.npz`).
- **Hypothesis:** A higher tensor rank ($R=10$ vs $R=8$) provides greater representational flexibility in continuous optimization, reducing the effective 1-norm $\lambda_{\text{eff}}$ from $48.32$ to $48.03$. Since chemistry cost $C = \lambda_{\text{eff}} \times Q \times T$, a smaller $\lambda_{\text{eff}}$ was assumed to produce a better quantum circuit.
- **Experimental Outcome:** **FALSIFIED / HARMFUL REGRESSION**.
  - Live $R=8$ Official Verifier Score: **`337,993,966.88`** (Ratio: **`9.928x`**).
  - $R=10, J=7$ Official Verifier Score: **`559,892,578.19`** (Ratio: **`5.993x`**).
  - Net Performance: **+65.7% Cost Explosion (Ratio degraded by 39.6%)**.
- **Root Cause Analysis:**
  The continuous optimizer reduced $\lambda_{\text{eff}}$ by only $0.6\%$ ($48.32 \to 48.03$).
  However, increasing $R$ from 8 to 10 expanded the total address table size from $A = 1220$ to $A = 1366$ rows.
  In 4-address pebble mode (`pebbled_init`), $A = 1366$ with $J \ge 4$ requires $Q = 161$ qubits, violating the competition's strict 128-qubit ceiling.
  Consequently, the compiler was forced to fall back to 2-address linear mode (`build_qroam2`), where $H = A / 2 \approx 683$ high addresses.
  This increased 2-pass Toffolis from **8,336** (in $R=8$) to **17,006** (in $R=10, J=7$).
  **The continuous optimization gain was completely overwhelmed by the discrete compiler penalty.**
- **Enforced Policy:**
  **DO NOT overwrite the live $R=8$ submission artifact with the $R=10$ artifact.**
  Continuous factorizations must be evaluated jointly with their discrete QROM compiler constraints, not by continuous $\lambda_{\text{eff}}$ alone.

---

### NEG-002: Monolithic 4-Address Pebble QROM at $J=5$ on Unconstrained Tables

- **Date:** 2026-10-30
- **Hypothesis:** 4-address pebble QROM (`pebbled_init`) can be scaled directly to $J=5$ on $A = 1366$ by allocating $3 \times (brot - 1) \times J$ bank wires.
- **Experimental Outcome:** **FALSIFIED / CEILING VIOLATION**.
  - Required Qubits: $n (11) + W (40) + \text{bank} (105) + \text{scratch} (5) = \mathbf{161\text{ qubits}}$.
  - Legal Cap: $\le 128$ qubits (QUBIT_CAP).
  - Result: `AssertionError: {'num_qubits': 161, 'static_toffoli': 439}`.
- **Root Cause Analysis:**
  Monolithic 4-address QROM requires 3 difference words per word index $j \in [0, J)$. When $J=5$ and $brot=8$, $3 \times 7 \times 5 = 105$ bank wires. Because $105 + 51 = 156 > 128$, $J=5$ cannot run in 4-address mode unless differences are compressed into sub-spaces or higher bits are proven identically zero across all rows.

---

### NEG-003: Hardcoded $J=5$ in `build_portfolio.py`

- **Date:** 2026-10-30
- **Hypothesis:** $J=5$ was assumed to be an optimal tradeoff between circuit count and qubit count.
- **Experimental Outcome:** **FALSIFIED**.
  - On $R=10$ with 2-address linear mode:
    - $J=5$: 15 circuits, 22,770 2-pass Toffolis, Score: $659,100,000$ (Ratio: 5.09x).
    - $J=7$: 11 circuits, 17,006 2-pass Toffolis, Score: $559,892,578.19$ (Ratio: 5.993x).
  - $J=7$ saved **5,764 Toffolis** and **99.2M score points** (15.1% improvement) while staying within 124 qubits ($\le 126 \le 128$).
- **Resolution:**
  Updated `src/build_portfolio.py` to parameterize $J$ dynamically with $J=7$ as default for 2-address mode.

---

### NEG-004: In-Place Itoh-Tsujii Inversion in Reversible Logic

- **Date:** 2026-10-30
- **Context:** DQI syndrome decoding via Extended Euclidean Algorithm.
- **Hypothesis:** Reversible in-place field inversion using Itoh-Tsujii addition chains can be made competitive by optimizing Frobenius squarings.
- **Experimental Outcome:** **ARCHITECTURALLY DEFICIENT**.
  - While Frobenius squarings are linear in normal bases, the Itoh-Tsujii addition chain for $\mathbb{F}_{2^{12}}$ strictly requires 11 field multiplications per inversion ($16 \times 11 = 176$ multiplications across 16 syndrome steps).
  - In comparison, Andi Gu's Inversionless Berlekamp-Massey eliminates field inversions entirely via discrepancy cross-multiplications, requiring $\sim 192$ multiplications for the entire recurrence.
- **Resolution:**
  Abandon EEA inversion optimization. Focus research on Inversionless Berlekamp-Massey architectures.
