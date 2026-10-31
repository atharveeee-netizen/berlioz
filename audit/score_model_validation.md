# Mathematical Score Model Validation & Target Product Analysis

## 1. Exact Competition Composite Formula
The composite score on Kaggle is evaluated as the geometric mean across all three benchmarks:
$$\text{Score} = (R_{\text{invsqrt}} \cdot R_{\text{DQI}} \cdot R_{\text{chem}})^{1/3}$$
where each ratio is:
$$R_i = \frac{C_i^{\text{ref}}}{C_i^{\text{candidate}}}$$

## 2. Reconstructing the 22.80575 vs 22.99562 Grading Evidence
The target product equation from Masterloop 15 §11 states:
$$\text{Product} = \text{Score}^3 = R_{\text{invsqrt}} \cdot R_{\text{DQI}} \cdot R_{\text{chem}}$$

For the graded submission `57811741` which achieved **`22.80575`**:
$$\text{Product} = 22.80575^3 = 11,861.341$$
With verified $R_{\text{invsqrt}} = 20.64210$ and $R_{\text{chem}} = 9.92799$:
$$R_{\text{invsqrt}} \cdot R_{\text{chem}} = 20.64210 \times 9.92799 = 204.9346$$
Solving for the DQI ratio:
$$R_{\text{DQI}}^{\text{actual}} = \frac{11,861.341}{204.9346} = \mathbf{57.8787}$$

### Why was $R_{\text{DQI}} = 57.88$ instead of the theoretical $71.29$?
1. **The Clopper-Pearson Penalty ($R(0) = 1.19126$):**
   The un-penalized ratio at $T_{\text{mean}} = 433,783.5$ is:
   $$R_{\text{ideal}} = \frac{24,439,463,583,672.93}{889^2 \times 433,783.5} = 71.28638$$
   Under the mandatory Clopper-Pearson confidence bound at $\delta = 2^{-128}$ with zero errors ($k=0$):
   $$R_{\text{DQI}}^{(0)} = \frac{71.28638}{1.19126046} = \mathbf{59.84107}$$
2. **Kaggle Private Salt Sampling Noise:**
   On the private test salt with $N = 102,400$ shots, if 1 or 2 shots experience an error ($k=1$ or $k=2$):
   - For $k=1$: $\epsilon^+ = 9.1042 \times 10^{-4} \implies R(1) = 1.19673 \implies R_{\text{DQI}} = 59.57$
   - For $k=2$: $\epsilon^+ = 9.4882 \times 10^{-4} \implies R(2) = 1.20139 \implies R_{\text{DQI}} = 59.34$
   - Additionally, Monte Carlo sampling of error weight $w_k$ on private salt produces slight variance in mean Toffoli count ($T_{\text{mean}} \approx 448,000$), shifting $R_{\text{DQI}}$ to $57.88$.

## 3. Disproving Unverified Ratios
- Claims of $R_{\text{DQI}} \approx 195\times - 210\times$ assume an unverified 225,804 Toffoli reduction without the Clopper-Pearson confidence penalty.
- Composite projections of $35.6 - 36.7$ are mathematically impossible under the competition scoring contract unless $T_{\text{mean}}$ drops to $\sim 130,000$ Toffolis while retaining $Q \le 889$ and $\epsilon^+ < 1/16$.
- Our verified candidate achieves **`23.06081`** under genuine host simulation and **`22.99562`** on the live public leaderboard.
