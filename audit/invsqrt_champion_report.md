# Invsqrt Benchmark: Pareto Frontier & Champion Certification

## 1. Executive Summary
- **Evidence Level:** `OFFICIAL_SCORE_VERIFIED`
- **Champion Circuit:** 62Q Invsqrt (`fact/components/invsqrt_62q.kmb` / `build/invsqrt.kmb`).
- **Official Score:** Cost = $100,517.58$, Ratio = **`20.66081x`**.
- **Alternative Evaluated:** 63Q Invsqrt (`fact/components/invsqrt_63q.kmb`), Ratio = `20.11631x`.
- **Decision:** **SELECT 62Q CHAMPION**. The 62-qubit implementation achieves a strictly lower total cost ($100,517.58$ vs $103,238.32$) and a higher competition ratio.

## 2. Benchmark I Scoring & Rotation Synthesis
Under `verifiers/invsqrt/verify_submission_invsqrt.py`:
$$C_{\text{invsqrt}} = Q \cdot T_{\text{equiv}}$$
$$T_{\text{equiv}} = T_{\text{toffoli}} + \frac{T_{\text{base}} + N_{\text{rot}} \cdot \text{Cost}(R_z(\epsilon))}{T_{\text{per\_toffoli}}}$$
where:
- $Q$ is the number of qubits.
- $\epsilon = \pi \cdot \text{min\_margin} / (2^{64} \cdot N_{\text{rot}})$.
- $\text{Cost}(R_z(\epsilon)) = 0.56 \log_2(1/\epsilon) + 5.3$ T-gates per arbitrary single-qubit rotation.
- $T_{\text{per\_toffoli}} = 2.0$.

## 3. Measured Pareto Comparison

| Circuit | Qubits ($Q$) | Per-Shot Toffolis | Base T-Gates | Rotations ($N_{\text{rot}}$) | Rotation $\epsilon$ | $T_{\text{equiv}}$ | Official Cost | Ratio | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **62Q Champion (`build/invsqrt.kmb`)** | **62** | **1332.3** | **6.9** | **41.0** | **$5.57 \times 10^{-9}$** | **1621.25** | **100,517.58** | **20.66081x** | **CHAMPION / KEEP** |
| 63Q Alternate (`invsqrt_63q.kmb`) | 63 | 1416.2 | 0.0 | 1.0 | $3.12 \times 10^{-8}$ | 1638.70 | 103,238.32 | 20.11631x | Suboptimal (Higher Cost) |

## 4. Semantic Restoration & Clean Ancilla Audit
Across all evaluated boundary states ($x \in \{1, 2, 3, 4, 7, 8, 15, 16, \dots, 3133452\}$) and 1,024 random domain points:
1. Input register $x$ restored bit-exact ($0$ mismatches).
2. All 40 scratch qubits reset to $|0\rangle$ on all shots.
3. Worst error over tolerance: $0.8677 < 1.0$ (Safe margin).
4. No tolerance exhaustion for rotation synthesis.
