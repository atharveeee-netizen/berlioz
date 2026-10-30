# BLOCK 8 & 9: CHEMISTRY CO-DESIGN, GAUGE FIXING & QROM BATCHING NOVELTY CARD

```yaml
BLOCK: 8 & 9 - Chemistry Table Co-Design, Gauge Fixing & J=7 QROM Batching
STATUS: KEEP
NOVELTY: NOVEL (Half-Open Givens Gauge bit(7)==bit(6) with J=7 Batching under Q <= 126)
BEST_KNOWN: J=5 batching (15 circuits) with full 8-bit sign loading (QROM Toffolis = 4,152)
OUR_LEVER: Signed half-open gauge eliminates sign bit; J=7 batching reduces circuits from 15 to 11
BACK_OF_ENVELOPE_GAIN: Cuts angle circuit count by 26.7% (from 15 to 11 circuits) while strictly staying within the 128 qubit limit
P_SUCCESS: 0.96 (Verified in tests/test_portfolio_coupling.py and official dfthcsos verifier)
VERDICT: KEEP (Implemented in src/chem/angles_qrom.py and fact/dfthc_r10_b129_c60_brot8.npz)
```

## 1. Hypothesis
Because Givens angle rotation senses are defined up to an orthogonal gauge freedom:
$$\theta \mapsto \theta' \in [-\pi/2, \pi/2)$$
enforcing the signed half-open gauge condition:
$$\text{bit}(7) == \text{bit}(6)$$
across all $1,366 \times 75$ angle words allows the sign bit to be completely omitted during QROM loading, reducing word size from 8 bits to 7 bits. Furthermore, analytically scaling batch size to $J=7$ ($Q(7) = 125 \le 126$ qubits) reduces the total angle circuit count from 15 to 11 without exceeding the competition's 128-qubit ceiling.

## 2. Mathematical Proof & Bounds
1. **Half-Open Gauge Invariant:**
   $$\text{canonical} = (\text{words} \oplus \text{edge\_signs})$$
   Enforces that the top two bits match: `((canonical >> 7) ^ (canonical >> 6)) & 1 == 0`.
   This was verified exhaustively across all $102,450$ values in `fact/dfthc_r10_b129_c60_brot8.npz`.
2. **Qubit Allocation Envelope:**
   For address size $A=2$ and $\beta_{\text{rot}} = 8$:
   $$Q(J) = 20 + 15J$$
   For $J=7$: $Q(7) = 20 + 105 = 125 \le 126 \le 128$ (QUBIT_CAP).
   For $J=8$: $Q(8) = 140 > 128$ (REJECTED by verifier).
   Therefore, $J=7$ is the global mathematical optimum for $A=2$.

## 3. Verification & Evidence
* **Unit tests:** `test_tensor_shapes`, `test_half_open_gauge`, `test_batching_qubit_bounds`, `test_single_circuit_synthesis` in `tests/test_portfolio_coupling.py`.
* **Verifier output:** All chemical accuracy bounds pass ($e_1 = 19.0\text{ mHa} \le 20\text{ mHa}$, $e_2 = 19.7\text{ mHa} \le 20\text{ mHa}$, $\lambda_{\text{eff}} = 48.0311$).
