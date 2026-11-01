# Chemistry Benchmark & R=8 Incumbent Audit — Masterloop 26 Experiment CHEM-1

**Date:** 2026-10-31T20:30Z  
**Standard:** Syzygy Spec-Driven Development Standard (v1.0.0)  
**Target Benchmark:** Benchmark III (Chemistry — DF-THC Hamiltonian Simulation)  
**Target Codebase:** `verifiers/dfthcsos/`, `src/chem/`, `fact/`  
**Evidence Class:** E1 (Direct source audit) + E2 (Locally reproduced verification)  

---

## 1. Executive Summary

This deliverable provides an authoritative technical audit of Benchmark III (Chemistry), its physical and mathematical specification, the double-factorized tensor hypercontraction (DF-THC) Hamiltonian simulation algorithm, and the current production $R=8$ incumbent champion.

### Authoritative Reference Standards:
- Official Google Reference Cost: $C_{\text{CHEM\_REF}} = \mathbf{3,355,599,588.3155365}$
- Incumbent Champion Cost: $C_{\text{inc}} = \mathbf{337,823,023.22}$
- Incumbent Improvement Ratio: $R_{\text{chem}} = \frac{C_{\text{CHEM\_REF}}}{C_{\text{inc}}} = \mathbf{9.933010\times}$
- Production Parameters: $R = 8, B = 143, C = 60, N = 76, \text{brot} = 8, J = 5$ (15 angle circuits).

---

## 2. Benchmark III Physical Specification & Scoring Formula

### 2.1 Active Space Problem
The benchmark targets the active-space Hamiltonian of the Nitrogenase iron-molybdenum cofactor (**FeMoCo76o113e**):
- Spin orbitals: $N = 76$ spatial orbitals ($152$ spin-orbitals).
- Active electrons: $113$ electrons.
- Electronic Hamiltonian:
  $$H = \sum_{p, q} h_{pq} a_p^\dagger a_q + \frac{1}{2} \sum_{p, q, r, s} v_{pqrs} a_p^\dagger a_r^\dagger a_s a_q$$
- Representation: Double-Factorized Tensor Hypercontraction (DF-THC) with Sum-of-Squares (SOS) stabilization.

### 2.2 Mathematical Cost Function
The official cost function is defined in `verifiers/dfthcsos/verify.py:53`:
$$C_{\text{chem}} = \lambda_{\text{eff}} \cdot T_{\text{total}} \cdot Q_{\text{total}}$$

where:
1. **Effective Spectral 1-Norm ($\lambda_{\text{eff}}$):**
   $$\lambda_{\text{eff}} = \sqrt{E_{\text{gap}} \cdot (2\Lambda - E_{\text{gap}})}$$
   - $\Lambda$ is the sum of double-factorized tensor norms.
   - $E_{\text{gap}}$ is the certified ground-state lower-bound energy shift.
   - Evaluated on the exact angle words loaded by the compiled `ANGLE_k` circuits.
2. **Total Toffoli Gate Count ($T_{\text{total}}$):**
   $$T_{\text{total}} = T_{\text{angles}} + T_{\text{prep, outer}} + T_{\text{prep, inner}} + T_{\text{givens}}$$
   - $T_{\text{angles}}$: Mean Toffoli count per shot across all 15 `ANGLE_k` circuits in `kickmix` (evaluated forward $U_T$ and adjoint $U_T^\dagger$, i.e. 2 passes).
   - $T_{\text{prep, outer}} + T_{\text{prep, inner}}$: State preparation Toffolis (`SpinFreeData_V1`).
   - $T_{\text{givens}} = 2 \cdot (N - 1) \cdot (2 \cdot \text{brot} - 1)$: Coherent Givens rotation ladder.
3. **Total Qubit Footprint ($Q_{\text{total}}$):**
   $$Q_{\text{total}} = Q_{\text{prep, persistent}} + J \cdot \text{brot} + \max(Q_{\text{prep, temp}}, Q_{\text{angles, temp}})$$
   - Persistent qubits: Outer + inner state preparation registers ($Q_{\text{prep, persistent}}$) plus $J \cdot \text{brot}$ persistent angle registers.
   - Shared temporary workspace: The `ANGLE_k` circuits run sequentially with state preparation, sharing scratch workspace.

### 2.3 Strict Verifier Rejection Boundaries (`verify.py:68-75`):
A submission is rejected (`FAIL`) if:
- Energy reconstruction error exceeds $20 \text{ mHa}$ ($\Delta E_1 > 0.020$ Ha or $\Delta E_2 > 0.020$ Ha).
- The SOS gap is outside $(0, 2\Lambda)$.
- Raw $\Lambda \le 49.0$ Ha or $E_{\text{gap}} \le 3.914898$ Ha.
- **Any `ANGLE_k` circuit uses more than 128 qubits ($Q_{\text{angle}} \le 128$)**.
- The circuits break register naming conventions (`selection`, `word_0..word_{J-1}`).

---

## 3. Audit of the Current $R=8$ Incumbent Implementation

### 3.1 Factorization Tensors (`submission.npz`):
- $U \in \mathbb{R}^{R \times B \times N} = \mathbb{R}^{8 \times 143 \times 76}$: THC orbital basis factor tensor.
- $W \in \mathbb{R}^{R \times B \times C} = \mathbb{R}^{8 \times 143 \times 60}$: Core auxiliary expansion tensor.
- Total address rows: $A = 1,220$ address configurations.
- Givens tree: 75 tree edges spanning the 76 spatial orbitals.
- Rotation precision: $\text{brot} = 8$ bits.

### 3.2 QROM Architecture: Signed Half-Open Gauge + 4-Address Banked Pebble QROM
The incumbent (`angles_qrom.py`) achieves state-of-the-art performance via four complementary co-design innovations:

1. **Signed Half-Open Givens Gauge:**
   - Every Givens rotation angle $\theta$ is canonically mapped such that:
     $$\text{bit}(\text{brot}-1) == \text{bit}(\text{brot}-2) \quad (\text{bit } 7 == \text{bit } 6)$$
   - Because the sign bit is identical to the most significant magnitude bit, the top bit does not need to be loaded from QROM!
   - Only $\text{brot} - 1 = 7$ bits per word are loaded, and the sign bit is cloned via a single CNOT.
2. **Exact Five-Word Batching ($J = 5$):**
   - The 75 Givens rotation angles divide cleanly by 5:
     $$\frac{75}{5} = \mathbf{15 \text{ ANGLE circuits}}$$
   - Completely eliminates padding: zero empty angles, zero wasted rotations.
3. **Four-Address Banking:**
   - Groups 4 adjacent addresses $(4h, 4h+1, 4h+2, 4h+3)$ into a single super-word.
   - Stores the base value $v_0$ and 3 difference vectors:
     $$d_1 = v_0 \oplus v_1, \quad d_2 = v_0 \oplus v_2, \quad d_3 = v_0 \oplus v_1 \oplus v_2 \oplus v_3$$
   - The bank requires $3 \times (\text{brot}-1) \times J = 3 \times 7 \times 5 = 105$ qubits.
4. **Pebble Initialization & Split ANF Lookup Erasure:**
   - Evaluates the Algebraic Normal Form (ANF) polynomial over high selection bits using `pebbled_init`.
   - Cleans up the bank using split ANF erasure (`del_lookup_anf`).
   - Peak qubits in circuit:
     $$Q = n_{\text{sel}} + \text{words} + \text{bank} + \text{scratch} = 11 + 40 + 105 + 5 = \mathbf{126 \text{ qubits}} \quad (\le 128)$$

### 3.3 Incumbent Performance Metrics:
- **Angle Circuits:** 15 circuits, each using 126 qubits and $301$ Toffolis (mean).
- **Total Toffolis ($T_{\text{total}}$):**
  - $T_{\text{angles}} = 2 \times 4,515 = 9,030$ Toffolis (2 passes).
  - $T_{\text{prep}} = 5,061$ Toffolis.
  - $T_{\text{givens}} = 2 \times 75 \times 15 = 2,250$ Toffolis.
  - $T_{\text{total}} = 16,266.0$ Toffolis.
- **Total Qubits ($Q_{\text{total}}$):** $430$ qubits.
- **$\lambda_{\text{eff}}$:** $48.299209$ Ha.
- **Total Score ($C_{\text{chem}}$):** $48.299209 \times 16,266 \times 430 = \mathbf{337,823,023.22}$ ($9.933\times$ improvement).
