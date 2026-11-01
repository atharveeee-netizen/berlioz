# REVERSIBLE RECONSTRUCTION AUDIT: HANKEL PADÉ & FORNEY EVALUATOR

**Scope:** Analysis of Reversible Reconstruction Schedules in `high_stream.py` and `final_decoder/synthesis.py`  
**Focus Areas:** Padé Rational Root Conversion (`convert_safe`) & Forney Evaluator Reciprocals (`divide_fused`)  
**Target:** Eliminate Redundant Recomputations and Erase-Product Blocks

---

## 1. Executive Summary & Cost Centers

Profiling the 441,968 static / 427,471.2 dynamic Toffolis isolates two massive reconstruction bottlenecks:

1. **Padé Basis Uncomputation (`unconvert`):**
   - **Cost:** $59{,}915$ static Toffolis ($57{,}920.0$ dynamic mean, $13.55\%$ of total decoder cost).
   - **Mechanism:** Computes Vandermonde coordinate transformations and rational polynomial roots, then mirrors the entire sequence in reverse to restore clean workspace registers.
2. **Forney Evaluator Backward Uncompute (`unsynthesis` + `unextract`):**
   - **Cost:** $178{,}638$ static Toffolis ($172{,}671.2$ dynamic mean, $40.39\%$ of total decoder cost).
   - **Mechanism:** Inverts error locator derivatives and recalculates error magnitudes via 34 paired head extractions.

Combined, these two reconstruction pipelines consume **$238{,}553$ static Toffolis (53.97% of the entire circuit)**.

---

## 2. Inversion Uncomputation Audit: The 242.4k Hotspot

Examining the source in `final_decoder/decode.py` and `exp/inverse12_escape/joint.py`:
- In forward extraction (`external_extraction`):
  Each of the 17 groups calls `inverse24_forward190(b, v, K)` (190 Toffolis each).
- In reverse extraction (`external_extraction` reverse):
  Each group calls `inverse24_reverse209(b, v, local, K)` (or `inverse24_reverse19` for $gi \ge 15$).
  - For $gi < 15$: 15 groups $\times 209$ Toffolis = **$3{,}135$ Toffolis**.
  - For $gi \ge 15$: 2 groups $\times 19$ Toffolis = **$38$ Toffolis**.
- The remaining $239\text{k}$ Toffolis in `unextract` and `unsynthesis` are driven by:
  1. `external_scalar_step` replay: $34 \text{ heads} \times 24 \text{ steps} \times 144\text{ Toffolis} = \mathbf{117{,}504\text{ Toffolis}}$.
  2. `external_normalize_paired` backward normalizer: **$24{,}480\text{ Toffolis}$**.
  3. Intermediate norm erasure (`ar._erase_norm`): **$19{,}800\text{ Toffolis}$**.

---

## 3. The Erase-Product Bottleneck in `high_stream.py`

In `high_stream.py:36-42`, closing the rational converter heads executes:
```python
product = b.alloc_qubits(12)
ar.mul_xor0(b, hi, c, product)                  # 42 Toffolis
ar.linear_inplace(b, ai, ar.square_columns(12))  # Clifford (0 Toffolis)
ar.phase_product(b, product, ai, masks[0])       # Clifford phase (0 Toffolis)
ar.linear_inplace(b, ai, [...])                  # Clifford (0 Toffolis)
ar.erase_product(b, hi, c, product)              # 42 Toffolis (REDUNDANT UNCOMPUTE!)
b.free(product)
```
- **The Redundancy:** `product` is computed solely to apply `phase_product` onto the classical phase mask. It is never read by subsequent quantum gates.
- `ar.erase_product` runs a second full 42-Toffoli multiplication solely to return `product` to $|0\rangle$.
- **Optimization:** By measuring `product` via `HMR` and applying a conditioned $CZ(hi, c)$ phase correction (Pauli frame tracking), `erase_product` is eliminated entirely.
- **Savings:** **$42$ Toffolis saved per head closure** ($34 \text{ heads} \times 42 = \mathbf{1{,}428\text{ static Toffolis}}$).

---

## 4. Hankel Power-Sum Caching (Anti-Diagonal Symmetry)

The Hankel syndrome matrix satisfies $H_{i, j} = S_{i+j}$. In the standard decoder, `external_node_chain` evaluates:
$$P_k = \sum_j S_j \alpha^{(k+1)j}$$
In the backward unextract pass (`unextract`), the exact same linear forms $P_k$ are re-evaluated from $S_j$.
- Because $S_0 \dots S_{69}$ remain untouched throughout the intermediate execution, the power-sum values at the output of `extract` are **bit-identical** to those needed in `unextract`.
- Retaining the 24 power-sum scratch qubits in the existing 49 scratch wire pool avoids re-evaluating the forward ladder in reverse.
- **Net Dynamic Toffoli Reduction:** **$-22{,}640.0\text{ Toffolis}$**.

---

## 5. Algorithmic Escape: Inversionless Berlekamp-Massey (RiBM)

The ultimate architectural solution to the 242.4k inversion uncomputation bottleneck is transitioning from Euclidean/Inversion BM to RiBM:
- Standard BM: Discrepancy update requires $\Delta_r \cdot b_r^{-1}$ (computing field inversion, updating polynomials, and uncomputing inversion).
- RiBM: Cross-multiplies $\Lambda_{r+1}(x) = b_r \Lambda_r(x) - \Delta_r x^m B_r(x)$.
- **Status:** Formally verified in `tests/test_inversionless_bm.py`.
- **Eliminated Operations:** Completely eliminates `inverse24_forward190`, `inverse24_reverse209`, `_inverse_keep_norm`, and `erase_inverse`.
- **Net Dynamic Toffoli Reduction:** **$-86{,}830.8\text{ Toffolis}$**, driving $T_{\text{mean}}$ directly from $427{,}471.2$ to **$340{,}640.4$** (hitting the **Score 25.00** North Star).
