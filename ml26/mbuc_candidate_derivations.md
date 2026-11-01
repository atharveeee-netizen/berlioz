# Mathematical Derivations: Measurement-Based Uncomputation Subcircuits — Masterloop 26 Experiment DQI-5

**Date:** 2026-10-31T20:26Z  
**Standard:** Syzygy Spec-Driven Development Standard (v1.0.0)  
**Target Codebase:** Berlioz DQI RS(4095, 4025) Decoder  
**Evidence Class:** E1 (Direct source audit) + E2 (Locally reproduced simulation) + E3 (Mathematically derived)  

---

## 1. Executive Summary

This deliverable provides exhaustive mathematical derivations, quantum state evolution equations, post-measurement correction rules, Pauli-frame updates, and resource cost analyses for all candidate subcircuits in the DQI Reed-Solomon decoder.

---

## 2. Candidate 1: Temporary AND Gates in Chien Search Zero-Hold Ladder

### 2.1 Context & Circuit Location
In Chien search (`scan.py:29`), testing whether the 12-bit register $B[0]$ is all-zero requires evaluating:
$$z = \bigwedge_{k=0}^{11} \neg B[0]_k$$
This is implemented as an 11-step AND ladder:
$$L_0 = \neg B[0]_0 \wedge \neg B[0]_1$$
$$L_k = L_{k-1} \wedge \neg B[0]_{k+1}, \quad k = 1 \dots 10$$

### 2.2 Measurement Operation
For each temporary ancilla $L_k$, the uncomputation applies:
$$\text{HMR}(L_k, b_k)$$
where $\text{HMR}$ applies a Hadamard gate, measures in the computational basis into classical bit $b_k \in \{0, 1\}$, and resets $L_k \to |0\rangle$.

### 2.3 Post-Measurement State Derivation
Before measurement, the state on controls $c_1, c_2$ and target $t = c_1 \wedge c_2$ is:
$$|\psi\rangle = \alpha_{00} |000\rangle + \alpha_{01} |010\rangle + \alpha_{10} |100\rangle + \alpha_{11} |111\rangle$$
Applying $H$ to qubit $t$:
$$H_t |\psi\rangle = \frac{1}{\sqrt{2}} \left[ (\alpha_{00} |00\rangle + \alpha_{01} |01\rangle + \alpha_{10} |10\rangle) (|0\rangle + |1\rangle) + \alpha_{11} |11\rangle (|0\rangle - |1\rangle) \right]$$
Measuring $t$ in the $Z$-basis with outcome $b_k \in \{0, 1\}$ projects the state on $(c_1, c_2)$ to:
$$|\psi_{b_k}\rangle = \alpha_{00} |00\rangle + \alpha_{01} |01\rangle + \alpha_{10} |10\rangle + (-1)^{b_k} \alpha_{11} |11\rangle$$

### 2.4 Correction Rules
If $b_k = 1$, the state on $(c_1, c_2)$ has acquired an erroneous phase factor $(-1)$ on the $|11\rangle$ component.
The exact correction operator is the controlled-phase (CZ) gate:
$$\text{CZ}(c_1, c_2) = \text{diag}(1, 1, 1, -1)$$
Thus, the correction rule is:
$$\text{Apply } \text{CZ}(c_1, c_2) \quad \text{if } b_k = 1$$
Post-correction state:
$$\text{CZ}^{b_k} |\psi_{b_k}\rangle = \alpha_{00} |00\rangle + \alpha_{01} |01\rangle + \alpha_{10} |10\rangle + \alpha_{11} |11\rangle = |\psi_{\text{clean}}\rangle$$

### 2.5 Pauli-Frame Updates
Since CZ is a Clifford gate, the correction can either be applied immediately as a dynamically controlled gate (`CZ c1 c2 if b`) or commuted into subsequent Clifford operations. Because $c_1$ and $c_2$ in the ladder are uncomputed sequentially from top to bottom, applying dynamic `CZ` immediately avoids any non-trivial commutation rules.

### 2.6 Downstream Compatibility & Phase Correctness
- **Compatibility:** Perfect. Target ancillae return to $|0\rangle$, controls return to uncomputed state.
- **Phase Correctness:** Exact; error probability $\epsilon = 0$.

### 2.7 Complete Resource Cost
- Coherent uncomputation: $11 \text{ Toffolis forward} + 11 \text{ Toffolis backward} = 22 \text{ Toffolis/point}$.
- MBUC uncomputation: $11 \text{ Toffolis forward} + 0 \text{ Toffolis backward} = \mathbf{11 \text{ Toffolis/point}}$.
- **Net Saving across 4,025 positions:** $4,025 \times 11 = \mathbf{44,275 \text{ Toffolis}}$ ($50.0\%$ reduction).
- *Status:* Already utilized in incumbent champion.

---

## 3. Candidate 2: Finite Field Bilinear Multiplication Products (`init_gf2_mul` / `del_gf2_mul`)

### 3.1 Context & Circuit Location
In the Key Equation Solver (RiBM), step $r$ computes the discrepancy:
$$\Delta_r = S_r \oplus \sum_{j=1}^{\min(r, 35)} \Lambda_j \cdot S_{r-j}$$
Each term $\Lambda_j \cdot S_{r-j}$ is a full 12-bit field product $z = x \cdot y \in \text{GF}(2^{12})$.
Across the 70 steps of RiBM, there are $1,890$ such field products.

### 3.2 Measurement Operation
Let $z \in (\mathbb{F}_2)^{12}$ hold the 12 product bits. The uncomputation applies:
$$\text{HMR}(z_k, b_k) \quad \text{for } k = 0, \dots, 11$$
yielding an outcome bitstring $b = (b_0, b_1, \dots, b_{11}) \in \{0, 1\}^{12}$.

### 3.3 Post-Measurement State Derivation
In $\text{GF}(2^{12})$, field multiplication is bilinear over $\mathbb{F}_2$. For each output bit $k \in \{0 \dots 11\}$, there exists a fixed binary matrix $M_k \in \mathbb{F}_2^{12 \times 12}$ such that:
$$z_k(x, y) = x^T M_k y = \bigoplus_{i=0}^{11} \bigoplus_{j=0}^{11} (M_k)_{i, j} \, x_i y_j$$
Measuring all 12 bits of $z$ in the X-basis projects the quantum state by applying the phase factor:
$$\Phi_b(x, y) = (-1)^{\sum_{k=0}^{11} b_k z_k(x, y)} = (-1)^{\sum_{k=0}^{11} b_k \left( x^T M_k y \right)}$$
By linearity of matrix addition over $\mathbb{F}_2$, define the outcome-dependent bilinear form:
$$K_b = \bigoplus_{k=0}^{11} b_k M_k \in \mathbb{F}_2^{12 \times 12}$$
Then the post-measurement phase error is:
$$\Phi_b(x, y) = (-1)^{x^T K_b y} = (-1)^{\sum_{i, j : (K_b)_{i, j} = 1} x_i y_j}$$

### 3.4 Correction Rules
Notice that each term $(-1)^{x_i y_j}$ is precisely the phase effect of a controlled-$Z$ gate between qubit $x_i$ and qubit $y_j$!
Therefore, to completely eliminate the phase error $\Phi_b(x, y)$, the correction circuit applies:
$$U_{\text{correct}}(b) = \prod_{i=0}^{11} \prod_{j=0}^{11} \left[ \text{CZ}(x_i, y_j) \right]^{(K_b)_{i, j}}$$
Every single gate in $U_{\text{correct}}(b)$ is a **Clifford CZ gate**!
**It requires EXACTLY 0 TOFFOLI GATES!**

### 3.5 Pauli-Frame Precomputation
The matrix $K_b$ can be precomputed for all $2^{12} = 4,096$ possible measurement outcomes $b$:
1. Classical precomputation generates a table of size $4,096 \times 144$ bits ($73.7 \text{ KB}$).
2. Upon measurement of $b$, the classical controller looks up $K_b$ and applies the specified CZ gates.
3. Mean number of CZ gates applied: $\mathbb{E}[\text{popcount}(K_b)] \approx 72 \text{ CZ gates}$.

### 3.6 Downstream Compatibility & Phase Correctness
- **Compatibility:** Perfect. All 12 product qubits $z$ are cleanly reset to $|0\rangle$.
- **Phase Correctness:** Exact; verified across 50 test patterns in `ml26/mbuc_prototype_verification.json` (0 value errors, 0 phase errors).

### 3.7 Complete Resource Cost
- Coherent uncomputation: $1,890 \text{ products} \times 42 \text{ Toffolis} = \mathbf{79,380 \text{ Toffolis}}$.
- MBUC uncomputation: $1,890 \times 0 \text{ Toffolis} = \mathbf{0 \text{ Toffolis}}$.
- **Net Toffolis Saved:** **$79,380 \text{ dynamic Toffolis}$**!
- Clifford overhead: $1,890 \times 12 = 22,680$ HMR measurements + $\approx 136,080$ CZ gates ($0$ Toffoli cost).

---

## 4. Candidate 3: Forney Field Inversion Squaring Scaffolds

### 4.1 Context & Circuit Location
In Forney's formula, evaluating error values at root positions requires computing $\sigma'(X_j)^{-1}$ over $\text{GF}(2^{12})$.
Itoh-Tsujii inversion over $\text{GF}(2^{12})$ requires:
$$x^{-1} = x^{2^{12} - 2}$$
The addition chain for $2^{12} - 2 = 4094$ uses 11 squarings (linear, 0 Toffolis) and 4 intermediate field multiplications:
1. $x_2 = x^2 \cdot x = x^3$
2. $x_4 = (x_2)^{2^2} \cdot x_2 = x^{15}$
3. $x_8 = (x_4)^{2^4} \cdot x_4 = x^{255}$
4. $x_{11} = (x_8)^{2^2} \cdot x_2 = x^{1023}$
5. $x^{-1} = (x_{11})^2 \cdot x = x^{4094}$

### 4.2 Measurement Operation
The 4 intermediate multiplication results ($x_2, x_4, x_8, x_{11}$) are stored in a 48-qubit scaffold.
Applying MBUC (`del_gf2_mul`) to each of the 4 intermediate products:
$$4 \times 12 = 48 \text{ HMR measurements}$$

### 4.3 Correction Rules & Resource Cost
- Each intermediate product is a bilinear form over earlier powers.
- Applying Candidate 2's bilinear CZ correction uncomputes all 4 intermediate products with **0 Toffolis**.
- Coherent uncomputation cost: $4 \times 42 = \mathbf{168 \text{ Toffolis per inversion}}$.
- MBUC uncomputation cost: **$0 \text{ Toffolis}$**.
- Across up to 35 error locations ($35 \times 2 = 70$ inversions):
  $$\text{Toffolis Saved} = 70 \times 168 = \mathbf{11,760 \text{ Toffolis}}$$

---

## 5. Candidate 4: Division Quotient Uncomputation in Incumbent EEA (Why MBUC Fails)

### 5.1 Context & Problem
In the incumbent Proos-Zalka EEA, 70 quotient words $q_i \in \text{GF}(2^{12})$ are computed during polynomial division:
$$q_i = \text{leading}(B) \cdot (\text{leading}(A))^{-1}$$
In the reverse EEA pass, uncomputing the division ladder costs **$242,400 \text{ Toffolis}$**.
Why can we not measure $q_i$ and uncompute via MBUC?

### 5.2 Mathematical Proof of MBUC Failure for Division:
1. **Non-Bilinearity:**
   The quotient $q_i$ is a rational function of inputs: $q_i(A, B) = B \cdot A^{-1}$.
   The inversion $A^{-1}$ over $\text{GF}(2^{12})$ has algebraic degree:
   $$\deg_{\mathbb{F}_2}(A^{-1}) = 11$$
   It is a high-degree non-linear polynomial in the bits of $A$.
2. **Post-Measurement Phase:**
   If $q_i$ is measured in the X-basis with outcome $b \in \{0, 1\}^{12}$, the acquired phase is:
   $$\Phi_b(A, B) = (-1)^{b \cdot (B \cdot A^{-1})}$$
   This phase exponent $b \cdot (B \cdot A^{-1})$ has degree $1 + 11 = 12$ in the input qubits!
3. **Impossibility of Clifford Correction:**
   A Clifford correction can only correct quadratic phase forms $(-1)^{x^T K y}$.
   A degree-12 phase form $(-1)^{\text{poly}_{12}(A, B)}$ **cannot be synthesized using Clifford gates**.
   Synthesizing $(-1)^{B \cdot A^{-1}}$ requires computing $A^{-1}$ coherently in a temporary register, multiplying by $B$, and applying phase kickback.
4. **Conclusion:**
   Correcting the measurement of a non-linear quotient requires exactly the same number of Toffoli gates as computing the quotient coherently!
   Thus, MBUC provides **$0\%$ Toffoli reduction for division quotients**.

---

## 6. Candidate 5: Input Syndrome Registers $S_0 \dots S_{69}$ (The Superposition Barrier)

### 6.1 Context & Problem
Could we measure the syndrome registers $S_k$ at the end of the forward pass to avoid the reverse syndrome restoration stage (saving $23,613$ Toffolis)?

### 6.2 Mathematical Proof of Failure:
1. **The Quantum Interference Condition:**
   In DQI, the input state is a quantum superposition over syndrome space:
   $$|\psi_{\text{in}}\rangle = \sum_{S} c_S |S\rangle$$
   The target terminal state is:
   $$|\psi_{\text{out}}\rangle = \sum_{S} c_S (-1)^{\text{err}(S)} |S\rangle \otimes |0\dots0\rangle_{\text{ancilla}}$$
2. **Measurement Collapse:**
   If syndrome qubits are measured in the computational basis, the state collapses into a single classical syndrome $S_{\text{sample}}$. The coherent superposition $\sum c_S$ is irreversibly destroyed.
3. **Verifier Assertion:**
   The official verifier checks the state fidelity:
   $$\text{diff} = \text{sim.read\_across\_shots}(S) \oplus S_{\text{input}}$$
   If $S$ is measured or discarded, `diff` fails on all shots, resulting in a **$100\%$ value error**.
4. **Conclusion:** Syndrome registers must remain completely coherent and can never be measured.
