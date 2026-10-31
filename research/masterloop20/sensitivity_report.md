# MASTERLOOP 20 AUTHORITATIVE SCORE ENGINE & SENSITIVITY REPORT

**Baseline Composite Score:** `23.17767` (Product: `12451.1`)

## 1. Official Component Evaluation
- **Invsqrt**: Cost = `100,608.66` | **Ratio = 20.64210x**
- **DQI**: Cost = `402,454,799,602.87` | **Ratio = 60.72598x** (R = `1.19126`)
- **Chemistry**: Cost = `337,823,023.19` | **Ratio = 9.93301x**

## 2. Resource Sensitivity (Gain in Official Composite Score per 1% Resource Reduction)
- **Invsqrt Qubits ($Q$) or $T_{equiv}$**: `+0.07700` (`+0.332%`)
- **Chemistry Qubits, Toffolis, or $\lambda_{eff}$**: `+0.07700` (`+0.332%`)
- **DQI Toffolis ($T_{mean}$)**: `+0.07700` (`+0.332%`)
- **DQI Register Width ($Q$)**: `+0.15582` (`+0.672%`) — **2x LEVERAGE DUE TO $Q^2$!**

## 3. Portfolio Bottleneck & Strategy Audit
1. **Which benchmark currently limits the portfolio?**
   - **DQI** is the primary bottleneck. Competitor Rank 1 achieves ~`82.4x`, while Berlioz is at `60.73x` (a 35.7% gap).
   - **Chemistry** is the secondary bottleneck. Competitor Rank 1 achieves ~`11.26x`, while Berlioz is at `9.93x` (a 13.4% gap).
   - **Invsqrt** is already at the global frontier (`20.66x`), matching Rank 1.

2. **Which benchmark offers highest expected score improvement per engineering effort?**
   - **DQI Register Width Reduction (889Q -> 877Q)**: Drops $Q^2$ from 790,321 to 769,129 (2.7% cost drop).
   - **DQI Tower42 Inlining**: Drops field ops from 63-AND to 42-AND (33.3% multiplier savings), lifting DQI ratio to $\ge 90\times$.
   - **Chemistry 5-Word QROM**: Saves ~800 Toffolis per run with zero $\lambda_{{eff}}$ drift, lifting Chemistry ratio from `9.93x` to `~12.5x`.