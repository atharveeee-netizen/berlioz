# MATHEMATICAL PROOF & REVERSIBILITY CONTRACT: MEASUREMENT-BASED UNCOMPUTATION (MBUC)

**Date:** October 31, 2026  
**Scope:** Decoded Quantum Interferometry (DQI) Temporary Ancilla Uncomputation  
**Objective:** Replace coherent uncomputation Toffolis with measurement-based uncomputation (HMR) under rigorous Pauli-frame tracking without phase corruption.

---

## 1. The Fundamental MBUC Theorem for Quadratic Ancillae

### Theorem (Jones-Gidney MBUC Phase Equivalence)
Let $|a, c\rangle \in \mathbb{C}^2 \otimes \mathbb{C}^2$ be arbitrary quantum control qubits in superposition:
$$|\psi_0\rangle = \sum_{a, c \in \{0, 1\}} \alpha_{a, c} |a, c\rangle$$
Let $|p\rangle = |0\rangle$ be a clean scratch ancilla. Suppose the forward operation computes the non-linear AND into $p$:
$$|\psi_1\rangle = \sum_{a, c} \alpha_{a, c} |a, c\rangle |a \wedge c\rangle$$
Suppose a unitary circuit $U_{\text{target}}$ acts on other registers conditioned on $p$, leaving $a$ and $c$ unaltered.
Then, applying a Hadamard transform $H$ to $p$ and measuring $p$ in the computational basis yields outcome $m \in \{0, 1\}$.
Post-measurement, the residual state on $(a, c)$ is:
$$|\psi_{\text{post}}\rangle = \sum_{a, c} \alpha_{a, c} (-1)^{m \cdot (a \wedge c)} |a, c\rangle$$

### Proof of Phase Debt:
1. Apply $H$ on qubit $p$:
   $$H |a \wedge c\rangle = \frac{1}{\sqrt{2}} \left( |0\rangle + (-1)^{a \wedge c} |1\rangle \right)$$
2. The total state becomes:
   $$|\Psi\rangle = \frac{1}{\sqrt{2}} \sum_{a, c} \alpha_{a, c} |a, c\rangle |0\rangle + \frac{1}{\sqrt{2}} \sum_{a, c} \alpha_{a, c} (-1)^{a \wedge c} |a, c\rangle |1\rangle$$
3. Projective measurement of $p$ in basis $\{|0\rangle, |1\rangle\}$:
   - If outcome $m = 0$: $|\psi_{m=0}\rangle = \sum_{a, c} \alpha_{a, c} |a, c\rangle$ (Zero phase error).
   - If outcome $m = 1$: $|\psi_{m=1}\rangle = \sum_{a, c} \alpha_{a, c} (-1)^{a \wedge c} |a, c\rangle$ (Phase debt of $(-1)^{a \wedge c}$).
4. The phase factor $(-1)^{a \wedge c}$ is precisely the action of a Controlled-Z gate:
   $$CZ(a, c) |a, c\rangle = (-1)^{a \wedge c} |a, c\rangle$$
5. Therefore, applying the classically controlled gate $CZ(a, c)^{m}$ restores the exact coherent state:
   $$CZ(a, c)^{m} |\psi_{\text{post}}\rangle \equiv |\psi_0\rangle \quad \forall m \in \{0, 1\}$$
   $\blacksquare$

---

## 2. Invalidation Boundary: When MBUC is Forbidden

MBUC is strictly **invalid and mathematically corrupting** if any of the following conditions hold:

1. **Control Mutation Invalidation:** If register $a$ or $c$ has been modified (via CNOT, rotation, or arithmetic) between the initialization of $p$ and the measurement of $p$:
   $$CZ(a', c') \neq CZ(a, c)$$
   Applying $CZ$ to the mutated registers entangles the Pauli frame with corrupted basis states, causing fatal phase errors.
2. **Non-Clifford Invalidation:** If $p$ was computed from a degree-3 term $p = a \wedge c \wedge d$, the phase debt is $(-1)^{a \wedge c \wedge d} = CCZ(a, c, d)$.
   A CCZ is a non-Clifford gate requiring 1 Toffoli. Thus, MBUC on degree-3 terms saves 0 Toffolis.
3. **Syndrome Coherence Invalidation:** In DQI, the input syndrome registers $S_0 \dots S_{69}$ must be restored bit-exact in their coherent superposition. Any unmeasured ancilla entangled with $S_i$ that is discarded will trace out the syndrome density matrix and destroy DQI interference.

---

## 3. Register-by-Register Eligibility Audit for 889Q DQI

| Ancilla Group | Function in Decoder | Controls Preserved? | Phase Debt Order | Eligible for MBUC? | Justification |
|---|---|---|---|---|---|
| `W840-W863` (24Q) | Hankel Power Sums | YES | Quadratic ($CZ$) | **YES** | Input syndromes $S_i$ are preserved; $CZ(S_j, S_k)$ cancels phase with 0 Toffolis. |
| `W864-W887` (24Q) | Padé Root Basis | YES | Quadratic ($CZ$) | **YES** | Monic root normalizers preserve control basis; relative phase tracked by `phase_token`. |
| `W850-W885` (36Q) | BM Polynomials | NO | Cubic ($CCZ$) | **NO** | Polynomial coefficients are modified in-place during recurrence. MBUC requires CCZ (0 gain). |
| `W878-W888` (11Q) | Chien Zero Ladder | YES | Linear ($Z$) | **YES** | Self-uncomputing ephemeral ladder can measure early when root count reaches $k$. |
| `W840-W882` (43Q) | Forney Evaluator | NO | Rational Norm | **NO** | Norm inversion requires exact reciprocal pairs; phase erasure handled by `phase_inverse36_pivot`. |

---

## 4. Resource Accounting: Coherent vs MBUC Uncomputation

For eligible Padé root basis and Hankel power sums:
- **Coherent Uncomputation:**
  - $N_{\text{AND}} = 105$ per multiplication $\implies 105$ CCX gates per block.
  - Toffoli Cost: $105$ Toffolis.
- **MBUC Uncomputation:**
  - Forward: $105$ CCX (initialization).
  - Uncompute: $105$ Hadamard + Measure ($HMR$) + $105$ conditioned $CZ$ gates.
  - Toffoli Cost: **0 Toffolis**.
  - T-Gate Cost: **0 T-gates** (CZ is strictly Clifford, Clifford hierarchy level 2).
- **Net Saving:** **$105$ Toffolis saved per uncomputed multiplication**, with zero phase distortion.
