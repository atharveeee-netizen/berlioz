# DQI PROFILING & MULTIPLIER ATTRIBUTION (CHUNK C4)
**Artifact:** `dqi.kmb` | **Qubits:** 889 | **Mean Dynamic Toffolis:** 427,471.2 | **Ratio:** 60.72598×

---

### 1. Dynamic Toffoli Attribution & Multiplier Share
- **Total Dynamic Toffolis:** 427,471.2
- **Variable × Variable Multiplication Share:**
  - Dynamic multiplication calls per shot: $1,364.0$ calls
  - Toffoli cost per multiplier: $144.0$ Toffolis
  - Total multiplication Toffolis: $196,416.0$
  - **Share of total Toffolis:** **`45.95%`** (Target: $\ge 40.0\%$ — **PASS**)
- **Constant Multiplications & Squarings:**
  - Total calls: $2,840$ constant products, $1,420$ squarings
  - **Toffoli cost:** **0 Toffolis** (Rigorous proof: Constant multiplication is an $\mathbb{F}_2$-linear map $y = Mx$ synthesized exclusively with CNOTs. Squaring in characteristic 2 is the Frobenius endomorphism $(a+b)^2 = a^2+b^2$, which is strictly linear over $\mathbb{F}_2$).
- **Syndrome Extraction:** 64,120.0 Toffolis (15.0%)
- **Chien Search & Forney Evaluation:** 101,220.0 Toffolis (23.7%)
- **State Uncomputation:** 65,721.2 Toffolis (15.4%)

---

### 2. Reserve Inventory & Sizing Method
- `syndrome_register`: 840 qubits (70 symbols × 12 bits) — fixed contract specification.
- `pole_history`: 1 qubit — compressed from 3 qubits via single-carry uncomputation (measured quantile).
- `multiplier_scratch`: 12 qubits — ephemeral shared scratch.
- `normalizer_workspace`: 24 qubits — ephemeral register for polynomial monic reduction.
- `chien_scratch`: 12 qubits — single symbol accumulator.
- **Total active width:** Exactly 889 qubits (0 slack against the 889 ceiling).

---

### 3. Discrete Cliff Map & Physical Bounds
- **The $Q = 840$ Physical Floor:** Dropping width below 840 requires streaming syndrome symbols sequentially, which incurs a minimum serialization penalty of $+189,475$ Toffolis, far exceeding the break-even threshold ($\Delta T_{\text{max}} = 51,326$).
- **The $k \ge 1$ Failure Penalty:** A single value error re-weights $R(\epsilon^+)$ by $+0.46\%$ ($\approx +1,960$ Toffolis equivalent).
