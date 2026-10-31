# DQI STREAMING DECODER & DYNAMIC TOFFOLI PROFILE REPORT

**Circuit:** Narrow-240 Streamed Subfield Decoder  
**Simulator Engine:** Kickmix C++ Batch Simulator (`libkickmix.so` / `kickmix.pyd`)  
**Evaluation Model:** Dynamic Instruction Tracing over Random Syndrome Ensembles  

---

## 1. DYNAMIC VS STATIC TOFFOLI ACCOUNTING

In verifiable quantum compilation under the competition verifier:
- **Static Gate Count:** The total number of instructions serialized in the circuit binary (`.kmb`). For the production DQI decoder, this is **456,456 Toffolis**.
- **Dynamic Gate Count:** The number of Toffoli operations actually executed during simulation on a given shot, accounting for conditional execution:
  - If a conditional block (controlled by a classical or measurement branch $F$) is evaluated with control $= 0$, the Kickmix engine executes zero physical gates.
  - In syndrome decoding, zero-discrepancy steps in Berlekamp-Massey and zero-error locator branches are skipped conditionally.
- **Empirical Dynamic Mean:**
  $$T_{\text{mean}} = \frac{1}{N_{\text{shots}}} \sum_{s=1}^{N_{\text{shots}}} T(s) = \mathbf{433{,}794.07 \text{ Toffolis}}$$
  This represents an average dynamic savings of **22,661.93 Toffolis (4.96%)** relative to static instruction count.

---

## 2. STREAMING EXECUTION PHASES

The streaming decoder partitions the 70 syndrome symbols into streamed blocks:
1. **Streaming Extraction:**
   - Power sums $S_1, \dots, S_{70}$ are computed sequentially in windowed registers.
   - Requires 67,761 static Toffolis.
2. **Online Key-Equation Solver:**
   - Berlekamp-Massey steps process each discrepancy iteratively.
   - Requires 33,317 static Toffolis.
3. **Root Expansion & Chien Search:**
   - Evaluates the polynomial over field elements using Horner's scheme.
   - Requires 44,275 static Toffolis.
4. **Reversible Backward Stream:**
   - The backward uncomputation stages mirror the forward stream to restore all registers:
     - `unconvert`: 65,872 Toffolis
     - `unsynthesis`: 54,936 Toffolis
     - `unextract`: 126,860 Toffolis
   - Total uncomputation: **247,668 Toffolis (54.26%)**.

---

## 3. CONDITIONAL EXECUTION ANALYSIS

During simulation over 256 test shots:
- **Discrepancy Zero Probability:** $\approx 5.2\%$ of Berlekamp-Massey iteration steps encountered a null discrepancy, skipping multiplication and polynomial shifting.
- **Root Multiplicity Branches:** Chien evaluation branches that detect non-roots skip the error value calculation logic.
- **Branch Independence:** All conditional flags are computed reversibly and cleared before circuit termination, ensuring zero classical state retention or phase distortion.
