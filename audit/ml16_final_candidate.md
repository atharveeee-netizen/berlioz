# MASTERLOOP 16 FINAL CANDIDATE SELECTION & VERDICT

**Selected Portfolio:** `submission.zip` (`SHA-256: f2d95c2ff0a53e26d76f7f904aa934a4298c83184fb3db94ab940aa10252c234`)  
**Verified Composite Score:** $23.06062$  
**Kaggle Graded Public Score:** $23.00043$  
**Submission Action:** NO SUBMISSION (LOCK ACTIVE)  

---

## 1. COMPONENT-WISE CANDIDATE RATIONALE

### 1. Invsqrt Selection: 62Q Champion
- **Alternative Evaluated:** 78Q Coalesced Rotations.
- **Verdict:** Rejected. Expanding register width to coalesce rotations incurs a $+25.8\%$ width penalty, dropping the ratio from $20.64\times$ to $18.75\times$. The 62Q candidate with MBUC `HMR` intermediate ancilla reset is strictly Pareto-optimal.

### 2. DQI Selection: 889Q Narrow-240 Streamed Decoder
- **Alternative Evaluated 1:** 740Q Syndrome Overwrite.
- **Verdict:** Falsified. Destroys the coherent quantum syndrome state; fails official verifier input preservation.
- **Alternative Evaluated 2:** 878Q Serialized Workspace.
- **Verdict:** Rejected. Adds $+39.4\%$ Toffolis, worsening DQI cost by $+36\%$.
- **Alternative Evaluated 3:** Tower-42 Arithmetic Integration.
- **Verdict:** Validated and officially verified. Achieves identical score ($59.84\times$) while reducing linear CNOT fanout by $-85\%$. Preserved as verified drop-in backend.

### 3. Chemistry Selection: $R = 8, J = 5$ Banked ANF
- **Alternative Evaluated 1:** $J = 7$ Linear QROM.
- **Verdict:** Rejected. Explodes angle Toffolis from 8,336 to 15,400 (+84.7%), dropping ratio from $9.93\times$ to $6.92\times$.
- **Alternative Evaluated 2:** $R = 10$ Expanded Precision.
- **Verdict:** Rejected. Wider registers and deeper tables drop ratio to $4.94\times$.

---

## 2. PORTFOLIO COMPOSITE METRICS

$$S = (20.64210 \times 59.84086 \times 9.92799)^{1/3} = \mathbf{23.06062}$$

The current verified champion portfolio remains strictly superior to all tested architectural mutations. No candidate achieves a higher official verified score.
