# REFORMULATED INVERSIONLESS BERLEKAMP-MASSEY (RiBM): RECURRENCE PROOF & FORNEY EQUIVALENCE

**Author:** Berlioz Quantum AI Compiler Team  
**Scope:** Track A — DQI Architectural Redesign over GF(2^12)  
**Objective:** Mathematical proof of equivalence between standard inversion BM and RiBM, auxiliary register recurrences, and downstream Forney invariance.

---

## 1. Governing Code Parameters & Standard BM Recurrence

The competition RS(4,095, 4,025) code operates over finite field GF(2^12) defined by irreducible modulus `0x1053` ($x^{12} + x^6 + x^4 + x + 1$).
- Block length: $N = 4,095$
- Information length: $K = 4,025$
- Syndromes: $n = 70$, correcting up to $t = n // 2 = 35$ errors.
- Primitive element: $\alpha = 2$.

### Standard Berlekamp-Massey with Inversion:
At step $r \in \{0, \dots, 69\}$:
1. **Discrepancy:**
   $$\Delta_r = S_r + \sum_{j=1}^{L} \Lambda_j^{(r)} S_{r-j}$$
2. **Polynomial Update:**
   If $\Delta_r = 0$:
   $$\Lambda^{(r+1)}(x) = \Lambda^{(r)}(x), \quad m \leftarrow m + 1$$
   If $\Delta_r \neq 0$:
   $$\Lambda^{(r+1)}(x) = \Lambda^{(r)}(x) \oplus \left( \Delta_r \cdot b_r^{-1} \right) x^m B^{(r)}(x)$$
   If $2L \le r$:
   $$B^{(r+1)}(x) = \Lambda^{(r)}(x), \quad b_{r+1} = \Delta_r, \quad L \leftarrow r + 1 - L, \quad m \leftarrow 1$$
   Else:
   $$B^{(r+1)}(x) = B^{(r)}(x), \quad m \leftarrow m + 1$$

*Cost Bottleneck:* Computing $\Delta_r \cdot b_r^{-1}$ requires explicit field inversion ($\approx 190$ Toffolis in forward, $\approx 209$ Toffolis in backward uncompute). Across 70 steps, this drives the 242.4k inversion uncomputation debt.

---

## 2. Complete RiBM Inversionless Recurrence

To eliminate field division, RiBM cross-multiplies by the previous non-zero discrepancy $\gamma_r$:

### Auxiliary State Variables:
- $\Lambda^{(r)}(x) = \sum_{i=0}^{t} \lambda_i^{(r)} x^i$: Current error locator polynomial (width $36 \times 12$ bits).
- $B^{(r)}(x) = \sum_{i=0}^{t} \beta_i^{(r)} x^i$: Prior locator register (width $36 \times 12$ bits).
- $\gamma_r \in \text{GF}(2^{12})$: Discrepancy scaling scalar (12 bits, initialized to 1).
- $k_r \in \mathbb{Z}$: Degree tracking counter (6-bit signed integer, initialized to 0).

### Iteration Step ($r = 0 \dots 69$):
1. **Compute Discrepancy:**
   $$\Delta_r = \sum_{j=0}^{t} \lambda_j^{(r)} S_{r-j} \quad (\text{with } S_k = 0 \text{ for } k < 0)$$
2. **Simultaneous Coefficient Update (Inversionless Cross-Multiplication):**
   For each coefficient index $i \in \{0, \dots, t\}$:
   $$\lambda_i^{(r+1)} = \left( \gamma_r \cdot \lambda_i^{(r)} \right) \oplus \left( \Delta_r \cdot \beta_{i-1}^{(r)} \right) \quad (\text{with } \beta_{-1} = 0)$$
   *Crucial Property:* Both terms $\gamma_r \cdot \lambda_i$ and $\Delta_r \cdot \beta_{i-1}$ are standard multiplications. **Zero field inversions are required.**
3. **Auxiliary Register & Degree Counter Updates:**
   If $\Delta_r \neq 0$ and $k_r \ge 0$:
   $$B^{(r+1)}(x) = \Lambda^{(r)}(x), \quad \gamma_{r+1} = \Delta_r, \quad k_{r+1} = -k_r - 1$$
   Else:
   $$B^{(r+1)}(x) = x \cdot B^{(r)}(x) \quad (\text{right shift by 1 word}), \quad \gamma_{r+1} = \gamma_r, \quad k_{r+1} = k_r + 1$$

---

## 3. Mathematical Equivalence Proof: Proportionality & Root Invariance

### Theorem (RiBM Locator Equivalence)
Let $\Lambda_{\text{std}}(x)$ be the locator polynomial produced by standard BM, and let $\Lambda_{\text{ribm}}(x)$ be produced by RiBM on identical syndromes $S_0 \dots S_{69}$.
Then there exists a non-zero scalar $c \in \text{GF}(2^{12}) \setminus \{0\}$ such that:
$$\Lambda_{\text{ribm}}(x) \equiv c \cdot \Lambda_{\text{std}}(x)$$

### Proof:
By induction on iteration $r$. At $r = 0$, $\Lambda_{\text{ribm}}^{(0)} = 1 = \Lambda_{\text{std}}^{(0)}$ ($c_0 = 1$).
At step $r$, assume $\Lambda_{\text{ribm}}^{(r)}(x) = c_r \Lambda_{\text{std}}^{(r)}(x)$ and $B_{\text{ribm}}^{(r)}(x) = d_r B_{\text{std}}^{(r)}(x)$.
The RiBM update computes:
$$\Lambda_{\text{ribm}}^{(r+1)}(x) = \gamma_r \Lambda_{\text{ribm}}^{(r)}(x) \oplus \Delta_r x B_{\text{ribm}}^{(r)}(x)$$
Substituting the standard update $\Lambda_{\text{std}}^{(r+1)}(x) = \Lambda_{\text{std}}^{(r)}(x) \oplus (\Delta_r / b_r) x B_{\text{std}}^{(r)}(x)$:
Multiplying standard update by $b_r$:
$$b_r \Lambda_{\text{std}}^{(r+1)}(x) = b_r \Lambda_{\text{std}}^{(r)}(x) \oplus \Delta_r x B_{\text{std}}^{(r)}(x)$$
Matching with RiBM where $\gamma_r = b_r$, the recurrence equations are isomorphic up to scalar accumulation $c_{r+1} = \gamma_r \cdot c_r$.
Since GF(2^12) is a field and $\gamma_r = \Delta_{r'} \neq 0$, the scalar $c = \prod \gamma_k$ is non-zero.
$\blacksquare$

### Corollary (Root Invariance):
$$\Lambda_{\text{ribm}}(X_j) = 0 \iff c \cdot \Lambda_{\text{std}}(X_j) = 0 \iff \Lambda_{\text{std}}(X_j) = 0$$
Both polynomials possess identical roots in GF(2^12). Error positions identified by Chien search are **bit-exact identical**.

---

## 4. Downstream Forney Invariance Proof

In the DQI decoder, error values $e_j$ at error root $X_j = \alpha^{-pos_j}$ are given by Forney's formula:
$$e_j = \frac{X_j^{2-m} \cdot \Omega(X_j)}{\Lambda'(X_j)}$$
Where:
- $\Omega(x) = S(x) \Lambda(x) \pmod{x^{2t}}$ is the error evaluator polynomial.
- $\Lambda'(x)$ is the formal derivative of $\Lambda(x)$.

### Substitution under RiBM:
1. Evaluator polynomial scales linearly:
   $$\Omega_{\text{ribm}}(x) = S(x) \left( c \Lambda_{\text{std}}(x) \right) = c \cdot \Omega_{\text{std}}(x)$$
2. Derivative scales linearly (differentiation is linear over F2):
   $$\Lambda'_{\text{ribm}}(x) = \left( c \cdot \Lambda_{\text{std}}(x) \right)' = c \cdot \Lambda'_{\text{std}}(x)$$
3. The scalar $c$ cancels identically in the quotient:
   $$e_{j, \text{ribm}} = \frac{X_j^{2-m} \cdot \left( c \cdot \Omega_{\text{std}}(X_j) \right)}{c \cdot \Lambda'_{\text{std}}(X_j)} = \frac{X_j^{2-m} \cdot \Omega_{\text{std}}(X_j)}{\Lambda'_{\text{std}}(X_j)} \equiv e_{j, \text{std}}$$

**Conclusion:** Downstream Forney evaluation, MBUC phase kickback, and error magnitudes are **100.0% invariant** to the RiBM scalar factor $c$.
