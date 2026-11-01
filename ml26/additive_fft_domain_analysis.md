# Additive FFT Domain Analysis — Masterloop 26 Experiment DQI-2

**Date:** 2026-10-31T20:03Z  
**Standard:** Syzygy Spec-Driven Development Standard (v1.0.0)  
**Field:** $\text{GF}(2^{12})$ with primitive polynomial $p(x) = x^{12} + x^6 + x^4 + x + 1$ (`0x1053`)  
**Target Subroutine:** Chien Search Root Evaluation across $m = 4,025$ Codeword Positions  
**Evidence Class:** E1 (Direct source audit) + E3 (Mathematically derived)  

---

## 1. Mathematical Structure of the Chien Search Domain

In the DQI RS(4095, 4025) syndrome decoder over $\text{GF}(2^{12})$, the error locator polynomial $\Lambda(x)$ has degree at most $t = 35$:
$$\Lambda(x) = \lambda_0 \oplus \lambda_1 x \oplus \lambda_2 x^2 \oplus \dots \oplus \lambda_t x^t$$
The codeword positions correspond to $j \in \{0, 1, \dots, m-1\}$ with $m = 4,025$ (the full block length has $N = 2^{12} - 1 = 4,095$ positions, of which 4,025 are data symbols).

### The Multiplicative Evaluation Domain:
By definition of Reed-Solomon codes, the evaluation points in Chien search are powers of the primitive element $\alpha = 2$:
$$\mathcal{D}_{\text{chien}} = \{ X_j = \alpha^{-j} \mid j = 0, 1, \dots, m-1 \} \subset \text{GF}(2^{12})^\times$$
Key Algebraic Properties of $\mathcal{D}_{\text{chien}}$:
1. **Multiplicative Structure:** $\mathcal{D}_{\text{chien}}$ is a subset of the cyclic multiplicative group $\text{GF}(2^{12})^\times = \langle \alpha \rangle$ of order 4,095.
2. **Successive Ratio:** Successive evaluation points satisfy a constant multiplicative ratio:
   $$X_j = \alpha^{-j} = \alpha^{-1} \cdot X_{j-1}$$
3. **Additive Structure:** $\mathcal{D}_{\text{chien}}$ is **NOT an additive subspace** of $\text{GF}(2^{12})$ over $\mathbb{F}_2$. It is not closed under addition (e.g. $\alpha^a \oplus \alpha^b \neq \alpha^c$ in general), and it excludes the zero element $0$.

---

## 2. Mathematical Definition of Additive FFT Domains

An **Additive Fast Fourier Transform (AFFT)** (Cantor 1989, Gao & Mateer 2010) evaluates a polynomial over an **affine $\mathbb{F}_2$-subspace** $V \subseteq \mathbb{F}_{2^b}$.

### Additive Subspace Requirements:
1. $V$ must be closed under $\mathbb{F}_2$-vector addition: $\forall u, v \in V, u \oplus v \in V$.
2. The size of an additive subspace must be a power of two: $|V| = 2^d$ for some dimension $d \le 12$.
3. The basis of $V$ is a set of $\mathbb{F}_2$-linearly independent elements $\{v_0, v_1, \dots, v_{d-1}\} \subset \text{GF}(2^{12})$.
4. The decomposition operator is the linearized Frobenius operator:
   $$L_i(x) = x^2 \oplus \beta_i x$$
   which maps an additive subspace of dimension $d$ to a subspace of dimension $d-1$.

---

## 3. Discrepancy Between Multiplicative and Additive Domains

The prompt specifically directs:
> *"Do not assume the 4,025 positions form a convenient additive FFT domain. Derive whether the actual evaluation domain supports: Additive FFT, Subspace polynomial decomposition, Recursive multipoint evaluation, Pruned transforms, Hybrid structured evaluation."*

### Mathematical Incompatibility:
| Property | Chien Multiplicative Domain $\mathcal{D}_{\text{chien}}$ | Additive Subspace Domain $V$ |
|---|---|---|
| **Domain Definition** | Geometric progression $X_j = \alpha^{-j}$ | Linear span $\text{span}_{\mathbb{F}_2}\{v_0, \dots, v_{d-1}\}$ |
| **Cardinality** | $4,025$ points | Must be $2^d \in \{16, 32, 64, \dots, 4096\}$ |
| **Zero Element** | $0 \notin \mathcal{D}_{\text{chien}}$ | $0 \in V$ always |
| **Successive Relation** | $X_{j+1} = \alpha^{-1} \cdot X_j$ (Field mult) | $v_{i+1} = v_i \oplus \beta$ (Vector XOR) |
| **Ordering** | Codeword index order $j = 0 \dots 4024$ | Gray code or bit-reversed basis order |

### Embedding Analysis:
To apply an Additive FFT to Chien search, the domain $\mathcal{D}_{\text{chien}}$ of 4,025 points must be embedded into the full field:
$$V_{\text{full}} = \text{GF}(2^{12}) \cong (\mathbb{F}_2)^{12} \quad (|V_{\text{full}}| = 4,096)$$
The embedding requires:
1. Appending the missing 70 non-codeword points plus $x = 0$ (71 padding points).
2. Permuting the outputs from the additive basis order to the discrete logarithm permutation $\pi(v) = -\log_\alpha(v) \pmod{4095}$.

---

## 4. The Quadratic Qubit Penalty Barrier

Even if mathematically embeddable, a quantum circuit implementation of a full Additive FFT encounters a fatal physical barrier:

### Theorem (The Memory-Qubit Explosion Theorem):
An Additive FFT over $V_{\text{full}}$ evaluates $\Lambda(v)$ for all $4,096$ points in parallel.
- If all 4,096 field values are retained:
  $$Q_{\text{output}} = 4,096 \times 12 \text{ bits} = \mathbf{49,152 \text{ logical qubits}}$$
- Even if each point is collapsed in-place to a 1-bit zero indicator ($z_v = [\Lambda(v) == 0]$):
  $$Q_{\text{output, collapsed}} = 4,096 \times 1 \text{ bit} = \mathbf{4,096 \text{ logical qubits}}$$

### Benchmark II Scoring Impact:
The official DQI cost formula is:
$$C_{\text{dqi}} = R(\epsilon_+) \cdot \mathbf{Q^2} \cdot T$$
The incumbent champion uses $Q = 889$ qubits ($Q^2 = 790,321$).
If $Q$ increases to $4,096$ qubits:
$$\frac{Q_{\text{new}}^2}{Q_{\text{incumbent}}^2} = \left(\frac{4096}{889}\right)^2 = \mathbf{21.23\times \text{ increase in total cost}}$$
If $Q$ increases to $49,152$ qubits:
$$\frac{Q_{\text{new}}^2}{Q_{\text{incumbent}}^2} = \left(\frac{49152}{889}\right)^2 = \mathbf{3,056.7\times \text{ increase in total cost}}$$

**Conclusion:**  
Even if an Additive FFT reduced Toffolis to absolute zero ($T=0$), the $Q^2$ qubit penalty would make the candidate $> 21\times$ worse than the incumbent. Therefore, a parallel Additive FFT is fundamentally incompatible with the official Benchmark II objective function.
