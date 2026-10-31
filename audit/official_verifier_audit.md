# Official Verifier Audit & Certification Architecture

## 1. Audit Findings in Legacy `verify_portfolio.py`
The previous audit identified critical shortcomings in `src/verify_portfolio.py`:
1. **Invsqrt Cumulative Counter Bug:** `sim.operation_statistics()` returns total operations across all evaluated batches. Failing to divide by `eval_shots` inflated candidate cost by $1024\times$ to $8,754,026$ Toffolis, collapsing the ratio from $\sim 20.6\times$ down to $0.00377\times$.
2. **Missing Semantic Checks:** Operation counts alone were previously treated as passing without verifying $x$-register restoration, scratch qubit zero-reset, or rotation synthesis phase tolerances.
3. **DQI Shot Floor Incompatibility:** Under Clopper-Pearson $\delta = 2^{-128}$, any shot count $N < 1,375$ mathematically fails the acceptance condition $\epsilon^+ < 1/16$ even with zero errors! Quick tests with $N=256$ crashed the official verifier.
4. **Hardcoded Leaderboard Scores:** Previous scripts allowed fallback to hardcoded ratios instead of calculating live verified metrics.

## 2. Repairs Implemented
In `src/verify_portfolio.py`:
1. **Genuine Semantic Verification for Benchmark I:**
   - Validates input register $x$ bit-exact restoration across all boundary, power-of-two, and random domain samples.
   - Asserts scratch register clean zero return: `sim.read_across_shots(scratch).any(axis=1) == False`.
   - Evaluates worst-case phase error against $\text{tol}(x) = 2^{-24} \cdot \beta / \sqrt{x}$.
   - Divides cumulative simulation statistics by `eval_shots` for exact per-shot cost.
2. **Dual-Mode DQI Verification for Benchmark II:**
   - Full mode: Enforces $N = 102,400$ shots under $\log_2 \delta = -128.0$.
   - Quick mode: Supports $N \ge 2,048$ shots or relaxed $\log_2 \delta = -16.0$ for non-certifying quick smoke tests.
   - Always projects the official Clopper-Pearson bound using $N=102,400$ and $\delta = 2^{-128}$ so the displayed ratio reflects the actual competition evaluation.
3. **Genuine Chemistry Verification for Benchmark III:**
   - Directly calls `dfthcsos.verify.verify`, checking all orbital Givens rotations, orbital permutations, and $\lambda_{\text{eff}}$ calculations.
4. **Strict Certification Labeling:**
   - `OFFICIAL_SCORE_VERIFIED`: Full parameter evaluation ($N=102,400$ shots, full invsqrt grid, official salts).
   - `QUICK_TEST_PASS`: High-density sample evaluation ($N=2,048$ shots, boundary grid). Non-certifying.
   - `FAIL`: Any semantic violation, dirty ancilla, or unhandled exception.
