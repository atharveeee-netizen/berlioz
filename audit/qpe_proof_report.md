# Quadratic-Phase Erasure (QPE): Mathematical Proof & Integration Audit

## 1. Executive Summary & Evidence Status
- **Evidence Label:** `COMPONENT_VERIFIED` (Mathematically proven; unit-tested; integrated into production 889Q circuit).
- **Hypothesis Investigated:** Masterloop 15 §5 posited whether an additional ~225,804 Toffolis could be subtracted from the current 433,783 Toffoli DQI decoder.
- **Finding:** Audit of `extracted_dqi/blocks/dqi/team-1028-narrow240/source/` revealed that measurement-based quadratic phase erasure (`HMR + CZ` / `gf2_phase_by_product`) is **already incorporated** into `replay_erase.py` (`scalar_erase_second24`, `scalar_erase_second12`) and `synth_stream.py` (`divide_fused`). The measured 433,783 Toffoli count of the 889Q circuit already reflects these erasures. An additional 225,804 Toffoli reduction does not exist without breaking forward syndrome evaluation.

## 2. Mathematical Proof of Correctness
### Theorem (Exact Quantum Channel Equivalence of Degree-2 Erasure)
Let $H = \mathcal{H}_{\text{data}} \otimes \mathcal{H}_{\text{target}}$ where $\mathcal{H}_{\text{target}}$ holds an intermediate computational wire $y$ satisfying:
$$y = f(x) = \sum_{(i,j) \in E} x_i x_j \pmod 2$$
where $x_i, x_j$ are Boolean variables represented on live data qubits in computational basis states $|x\rangle$.

Let the erasure operation $\mathcal{E}$ consist of:
1. $X$-basis measurement and reset `HMR(y -> b)` yielding classical bit $b \in \{0, 1\}$.
2. Classical-conditioned Clifford phase network $\prod_{(i,j) \in E} CZ(x_i, x_j)^{\text{if } b=1}$.

### Proof
For any arbitrary state $|\psi\rangle = \sum_x c_x |x\rangle |f(x)\rangle$:
1. After the $X$-basis measurement:
   $$|\psi\rangle \xrightarrow{\text{HMR}} \sum_x c_x \frac{1}{\sqrt{2}} (-1)^{b \cdot f(x)} |x\rangle |0\rangle$$
   The target register is deterministically reset to $|0\rangle$, while the data state acquires an unwanted kickback phase factor $(-1)^{b \cdot f(x)}$.
2. When $b=0$, no correction is applied; the phase factor is $(-1)^0 = +1$.
3. When $b=1$, the conditioned $CZ$ network applies:
   $$\prod_{(i,j) \in E} CZ(x_i, x_j) |x\rangle = \prod_{(i,j) \in E} (-1)^{x_i x_j} |x\rangle = (-1)^{\sum_{(i,j)} x_i x_j} |x\rangle = (-1)^{f(x)} |x\rangle$$
   The combined phase factor for outcome $b=1$ is:
   $$(-1)^{f(x)} \cdot (-1)^{f(x)} = (-1)^{2 f(x)} = +1$$
4. In both measurement branches $b \in \{0, 1\}$, the net phase is identically $+1$.
5. By linearity, for any arbitrary superposition state and any entangled environment $\mathcal{H}_{\text{env}}$, $\mathcal{E}$ is an exact unitary equivalence to the identity channel on the data register while perfectly uncomputing the target wire to $|0\rangle$.
$$\mathcal{E} \left( \sum_x c_x |x\rangle |f(x)\rangle \right) = \left( \sum_x c_x |x\rangle \right) |0\rangle$$

## 3. Resource Accounting & Measured Impact
- **Primitive Gate Cost:**
  - Forward computation: 1 Toffoli (`ccx`) per product term.
  - Reverse erasure: 0 Toffolis (`hmr` + `cz`).
  - Net Toffoli savings per erased product: **100% of reverse uncompute Toffolis**.
- **Scope of Applicability:**
  - Requires all control operands $x_i, x_j$ to remain live at the time of erasure.
  - Cannot be applied to products where one operand has been irreversibly overwritten or measured.
- **Production Status:**
  - Integrated in `build/dqi.kmb` (889Q).
  - Measured mean Toffoli count: **`433,783.5`** (0 value errors, 0 phase errors across 2,048 and 102,400 shots).
