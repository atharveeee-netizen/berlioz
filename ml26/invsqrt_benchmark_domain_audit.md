# ML26 INV-1: Invsqrt Benchmark & Input Domain Audit

**Author:** BERLIOZ Discovery Agent (Autonomous Reversible Circuit Co-Design Engine)  
**Context:** BERLIOZ MASTERLOOP 26 — INV-1  
**Date:** 2026-10-31  
**Status:** COMPLETE & GROUNDED IN VERIFIER SOURCE

---

## 1. Executive Summary

Benchmark I assesses the reversible quantum compilation of the continuous reciprocal square-root phase gate:

$$U_{\text{invsqrt}} |x\rangle |0^{\otimes (Q - W)}\rangle = \exp\left(2\pi i \frac{\beta}{\sqrt{x}}\right) |x\rangle |0^{\otimes (Q - W)}\rangle$$

derived from the uniform electron gas (jellium) Hamiltonian simulation (arXiv:2308.12352). In electronic structure calculations, Coulomb interaction terms scale inversely with momentum exchange transfer $q = |\mathbf{k} - \mathbf{k}'|$, requiring phase factors proportional to $1/|\nu - \nu'| = 1/\sqrt{x}$.

This audit provides a mathematically rigorous specification of:
1. The exact discrete input domain $\mathcal{D}_x$.
2. The official verifier phase-error tolerance $\text{tol}(x)$ and 64-bit fixed-point arithmetic model.
3. The register contract, clean ancilla restoration requirements, and rotation synthesis cost function.

---

## 2. Governing Problem Specifications

Under [`verifiers/invsqrt/verify_submission_invsqrt.py`](file:///c:/Users/noobg/.gemini/antigravity-ide/scratch/berlioz/verifiers/invsqrt/verify_submission_invsqrt.py):

| Parameter | Symbol | Value | Derivation / Meaning |
| :--- | :---: | :---: | :--- |
| **Momentum Bits per Axis** | $n_p$ | 10 | Resolution of 3D momentum space grid |
| **Electron Count** | $\eta$ | 218 | Benchmark physical system electron count |
| **Input Register Width** | $W$ | **22 qubits** | $W = 2 n_p + 2$ (little-endian binary integer) |
| **Domain Minimum** | $x_{\min}$ | **1** | Non-zero momentum transfer floor |
| **Domain Maximum** | $x_{\max}$ | **3,133,452** | $x_{\max} = 3(2^{n_p} - 2)^2 = 3(1022)^2 = 3 \times 1,044,484$ |
| **Phase Scaling Factor** | $\beta$ | **1.0** (Fraction(1)) | Unit phase amplitude |
| **Precision Parameter** | $p_{\text{bits}}$ | **24 bits** | Fractional bitwidth governing relative tolerance |
| **Target Function** | $\theta(x)$ | $\beta / \sqrt{x} \pmod 1$ | Continuous target phase in turns ($[0, 1)$) |
| **Allowed Tolerance** | $\text{tol}(x)$ | $2^{-24} \cdot \beta / \sqrt{x}$ | Strict relative error bound floor |

---

## 3. Mathematical Phase & Fixed-Point Arithmetic Model

The verifier compares the simulated circuit phase $\theta_{\text{sim}}$ with the exact mathematical target in 64-bit unsigned fixed-point representation (units of $2^{-64}$ turns, represented as `uint64` modulo 1 turn):

### 3.1 Exact Reference Values
For each integer $x \in [1, x_{\max}]$:
$$r(x) = \left\lfloor \frac{2^{65} |\beta|}{\sqrt{x}} \right\rfloor = \text{isqrt}\left( \left\lfloor \frac{2^{130} \beta^2}{x} \right\rfloor \right)$$

The exact target phase $\theta_{\text{target}}(x)$ rounded to nearest at bit 0 is:
$$\theta_{\text{target}}(x) = \text{sign}(\beta) \cdot \left(\frac{r(x) + 1}{2}\right) \pmod{2^{64}}$$

The allowed phase tolerance in units of $2^{-64}$ turns is:
$$\text{tol}_{64}(x) = \min\left( \left\lfloor \frac{r(x)}{2^{25}} \right\rfloor, 2^{63} \right)$$

### 3.2 Boundary Tolerance Extremes
1. **At $x = 1$:**
   $$\theta(1) = 1.0 \pmod 1 \equiv 0.0 \text{ turns}$$
   $$\text{tol}(1) = 2^{-24} \approx 5.960464 \times 10^{-8} \text{ turns}$$
   $$\text{tol}_{64}(1) \approx 1.100 \times 10^{12} \text{ units of } 2^{-64}$$

2. **At $x = x_{\max} = 3,133,452$:**
   $$\sqrt{x_{\max}} = 1,770.155925$$
   $$\theta(x_{\max}) \approx 5.649219 \times 10^{-4} \text{ turns}$$
   $$\text{tol}(x_{\max}) = \frac{2^{-24}}{1770.155925} \approx 3.367197 \times 10^{-11} \text{ turns}$$
   $$\text{tol}_{64}(x_{\max}) \approx 6.211 \times 10^8 \text{ units of } 2^{-64}$$

The minimum tolerance $\text{tol}_{64}(x_{\max}) = 6.211 \times 10^8$ is well above the verifier's lower bound threshold of $2^{16} = 65,536$, confirming that 64-bit integer arithmetic has more than 13 bits of numerical safety margin against roundoff noise.

---

## 4. Register Contract & Strict Reversibility Invariants

The verifier executes every test shot in a zero-initialized state $|x\rangle |0\dots 0\rangle$:
1. **Primary Input Preservation:** The 22-qubit register `x` must be restored bit-exact to its initial computational state:
   $$\text{read}(x_{\text{reg}}) = x_{\text{input}} \quad (\text{Contract Violation} \implies \text{Immediate Rejection})$$
2. **Scratch Ancilla Cleanup:** Every auxiliary qubit outside the 22-qubit input register is classified as `scratch` and must return unconditionally to $|0\rangle$ on every execution shot:
   $$\forall q \in \text{scratch}: \quad \langle \psi | (|0\rangle\langle 0|_q) | \psi \rangle = 1 \quad (\text{Dirty Ancilla} \implies \text{Immediate Rejection})$$
3. **No Auxiliary Registers:** No extra persistent registers or leakage lines are permitted.

---

## 5. Official Cost & Synthesis Metric Formulation

The overall benchmark score is the product of active circuit width ($Q$) and the compiled Toffoli-equivalent cost ($C$):

$$\text{Score} = Q \times C$$

Where:
$$C = \text{Toffolis} + \frac{T_{\text{total}}}{4}$$
$$T_{\text{total}} = T_{\text{base}} + N_{\text{rot}} \cdot \text{Cost}(R_z(\varepsilon))$$

### 5.1 Synthesis Error Budget Allocation
The verifier does not simulate continuous angle synthesis error dynamically; instead, it bounds the worst-case collective error across all $N_{\text{rot}}$ non-Clifford rotations:
$$N_{\text{rot}} \cdot 2\varepsilon \le 2\pi \cdot \text{min\_margin}$$
$$\varepsilon = \frac{\pi \cdot \text{min\_margin}}{2^{64} \cdot N_{\text{rot}}}$$

Where the remaining phase margin is defined as:
$$\text{min\_margin} = \min_{x \in [1, x_{\max}]} \left( \text{tol}_{64}(x) - |\theta_{\text{sim}}(x) - \theta_{\text{target}}(x)| \right)$$

### 5.2 Discrete Rotation Cost
Each non-Clifford rotation approximated to precision $\varepsilon$ costs (under mixed fallback synthesis, arXiv:2203.10064):
$$\text{Cost}(R_z(\varepsilon)) = 0.56 \log_2\left(\frac{1}{\varepsilon}\right) + 5.3 \quad \text{T-gates}$$

### 5.3 The Two Failure Modes
1. **Tolerance Violation:** If for any $x$, $|\theta_{\text{sim}}(x) - \theta_{\text{target}}(x)| > \text{tol}_{64}(x)$, the simulation halts with `AssertionError: phase error exceeds tolerance`.
2. **Margin Exhaustion:** If $\text{min\_margin} \le 0$ across all shots, $\varepsilon \le 0$, halting with `AssertionError: No tolerance left for rotation synthesis error`.

---

## 6. Structural Implication: The $Q \times C$ Co-Design Trade-Off

The multiplicative metric $\text{Score} = Q \times C$ establishes an unavoidable architectural tension:
- Reducing circuit width $Q$ (e.g. from 62 to 58 qubits) provides a direct **$6.45\%$ reduction** in score if $C$ can be held constant.
- However, if reducing $Q$ requires holding fewer intermediate terms, serializing operations, or truncating polynomials, $T_{\text{total}}$ and Toffolis increase.
- Conversely, coalescing rotations into fewer single-qubit gates requires holding all product monomials in live registers simultaneously, expanding $Q$ from $62 \to 78+$ and degrading the score by $+10.1\%$.
- The optimal architecture must co-design the numerical polynomial degree, interval partitioning, and reversible register reclamation to hit the global Pareto frontier.
