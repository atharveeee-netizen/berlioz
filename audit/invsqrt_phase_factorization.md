# INVSQRT PHASE FACTORIZATION & WORKSPACE CO-DESIGN AUDIT

**Benchmark:** 22-bit Reversible Quantum Inverse Square Root  
**Current Champion:** 62 Qubits, 41 Rotations, $T_{\text{equiv}} = 1{,}622.72$  
**Official Cost:** 100,608.66  
**Ratio:** $20.64210\times$  

---

## 1. TARGET PHASE FUNCTION & MATHEMATICAL ERROR BUDGET

The benchmark synthesizes the continuous phase function:
$$\phi(x) = 2\pi \cdot \frac{2^{21}}{\sqrt{x}}, \quad x \in [1, 3{,}133{,}452]$$
with an exact verifier tolerance requiring the candidate state $|\psi_x\rangle$ to satisfy:
$$|\langle \psi_x | \text{diag}(e^{i\phi(x)}) |x\rangle|^2 \ge 1 - \delta_{\text{tol}}$$
scaled to $2^{-64}$ fixed-point representation.

### Empirical Error Slack Across 5,000 Domain Points:
- **Maximum Error Point:** $x = 161$
- **Worst-Case Ratio:** $0.9993$ of allowed threshold
- **Absolute Margin Slack:** $58{,}597{,}853$ units (out of $2^{64}$), corresponding to:
  $$\Delta_{\text{slack}} = 3.17 \times 10^{-12} \text{ turns}$$
- **Smallest Synthesized Rotation:** $\theta_{\text{min}} \approx 2.886 \times 10^{-11} \text{ turns}$
- **Margin Sensitivity Ratio:** $\frac{\theta_{\text{min}}}{\Delta_{\text{slack}}} \approx 9.1\times$
- **Mathematical Deduction:** The smallest rotation is nearly an order of magnitude larger than the remaining margin slack. Any naive truncation or pruning of rotations without complete algebraic re-centering immediately exceeds the allowed error bound, resulting in verifier rejection.

---

## 2. ROTATION PARTITIONING & MBUC REGISTER REUSE

The 41 rotations are partitioned into two tightly sequenced blocks:
- **Block 1 (15 rotations):** Applied to polynomial term register `q28`.
- **Block 2 (26 rotations):** Applied to cross-term registers `q50`, `q41`, `q40`, and `q28`.

### The Measurement-Based Uncomputation (MBUC) Mechanism:
Immediately following the application of rotations in Block 1, the circuit executes an `HMR` (Hadamard-Measure-Reset) primitive on `q28`:
1. Measures the ancilla in the Hadamard ($X$) basis.
2. Applies a classical-controlled Pauli-Z fixup based on the measurement outcome.
3. Reclaims the physical wire `q28` back to $|0\rangle$ in-place.
4. Block 2 reuses `q28` and `q50` for secondary term expansion.

---

## 3. FALSIFICATION OF THE "FEWER ROTATIONS / COALESCED PHASE" HYPOTHESIS

A recurring proposal in competitor research dossiers is to coalesce the 41 rotations into 1–4 rotations by expanding all 41 phase terms onto intermediate classical wires and applying a single synthesized rotation:

### Why Coalescing Fails:
1. To combine 41 distinct boolean product terms $P_k(x)$ into fewer rotations, all 15 basis monomials must be held simultaneously in live registers before applying the collective rotation.
2. This prevents the use of MBUC `HMR` intermediate resets.
3. The register requirement explodes:
   $$Q_{\text{coalesced}} = 62 + 15 = 77 \text{ to } 82 \text{ qubits}$$
4. In the official cost model $C_{\text{inv}} = Q \times T_{\text{equiv}}$:
   - Baseline ($Q=62$): $62 \times 1{,}622.72 = \mathbf{100{,}608.66}$
   - Coalesced ($Q=78$): Even if all 41 rotations were reduced to 1 rotation (saving $\approx 200$ equiv Toffolis, $T \approx 1{,}420$):
     $$78 \times 1{,}420 = \mathbf{110{,}760} \quad (+10.1\% \text{ worse})$$
5. **Conclusion:** Coalescing rotations increases total official cost due to the linear width penalty $Q \times T$. The 62Q champion with 41 MBUC rotations is strictly Pareto-optimal.
