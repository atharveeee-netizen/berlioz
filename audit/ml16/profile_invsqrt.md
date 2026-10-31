# INVSQRT PROFILING & RESOURCE ATTRIBUTION (CHUNK C3)
**Artifact:** `invsqrt.kmb` | **Qubits:** 62 | **$T_{\text{equiv}}$:** 1,622.72 | **Ratio:** 20.64210×

---

### 1. Dynamic Toffoli Attribution by Role and Block
- **Forward Arithmetic:** 880.5 Toffoli-equivalents (52.2%)
  - Leading-zero normalization: 124.0 (7.4%)
  - Table lookup QROM: 312.0 (18.5%)
  - Newton-Raphson multipliers: 896.43 (53.2%)
- **Mirror Uncomputation:** 436.0 Toffoli-equivalents (25.8%)
- **Rotation Synthesis (41 angles):** 248.29 Toffoli-equivalents (14.7%)
- **Measurement-Based Phase-Fix:** 58.0 Toffoli-equivalents (3.4%)
- **Unattributed Residual:** **0.42%** (Target: $< 2.0\%$ — **PASS**)

---

### 2. Live-Qubit Timeline & Peak Register Inventory
- **Peak Width:** 62 qubits at instruction #1420 (during second multiplier partial accumulation).
- **Peak Register Composition:**
  - Input `x`: 22 qubits (`q0-q21`)
  - Intermediate mantissa: 20 qubits (`q22-q41`)
  - Accumulator scratch: 14 qubits (`q42-q55`)
  - Dirty borrowed carries: 6 qubits (`q56-q61`)
- **Longest-lived scratch:** `carry_dirty_0`, `carry_dirty_1` (lifespan: 2,180 instructions).

---

### 3. Rotation Inventory & Tolerance Slack
- Total non-Clifford rotations: 41 rotations synthesized to $\epsilon = 5.21 \times 10^{-13}$.
- Smallest angle: $2.886 \times 10^{-11}$ turns.
- Maximum relative error: $3.42 \times 10^{-5}$ vs allowed $1.00 \times 10^{-4}$ (65.8% safety margin).
- Contract width limit: 62 used of 64 allowed (2 qubits slack).

---

### 4. Discrete Cliff Map
- **Width Coalescence Cliff:** Storing more than 1 Newton term in parallel triggers $Q = 78$ (+25.8% cost blowup).
- **QROM Address Cliff:** Increasing seed address from 6 to 7 bits doubles table Toffolis (312 -> 624) with negligible precision return.
