# GOOGLE QUANTUM AI VQCC — COMPETITION RULES & EVALUATION POLICY
## Recorded for Masterloop 16 (Chunk C2)

---

### 1. Key Deadlines and Submission Constraints
- **Final Submission Deadline:** 20 January 2027, 23:59 UTC.
- **Milestone Deadlines:**
  - Mid-Competition Milestone ($10,000): 20 November 2026.
  - Longest Leader Milestone ($10,000): 4 January 2027.
- **Daily Submission Limit:** 5 submissions per 24-hour UTC window.
- **Final Selection:** Exactly 2 submissions selected for final private evaluation.

---

### 2. External Code & Open-Source Policy
- Publicly available code and pre-trained weights/tensors are permitted if posted to the competition forum or public notebooks with permissible open-source licenses (Apache-2.0, MIT, BSD-3-Clause).
- All third-party artifacts (e.g. `yoyobar/qcc-local-sota-20261031`, `SomeJoint`, `busyaprime`, `Gluzdov`) must maintain strict provenance and attribution records.

---

### 3. Metric Feedback & Per-Task Visibility
- **Are per-task scores visible per Kaggle submission?**
  **NO.** Kaggle only reports a single scalar composite geometric-mean score $S$:
  $$S = (R_{\text{invsqrt}} \times R_{\text{dqi}} \times R_{\text{chem}})^{1/3}$$
  To isolate individual task performance, the compiler team must evaluate exact bit-exact local verifiers and use the algebraic residual inversion:
  $$d_{\text{kaggle}} = \frac{S^3}{R_{\text{invsqrt}} \times R_{\text{chem}}}$$

---

### 4. Approximation & Rare-Input Policy
- **Invsqrt:** Zero rare-input error trades allowed. Every test input drawn by the salted verifier must strictly fall within the IEEE floating-point tolerance bound. A single failure causes instant disqualification (`Score = 0.0`).
- **Chemistry:** Zero rare-input approximations allowed. The active space ground state energy, gap bounds ($E_{\text{gap}} \in [3.8, 4.0]\text{ Ha}$), and $e_1, e_2 \le 20.0\text{ mHa}$ must hold strictly.
- **DQI:** Approximation is explicitly allowed and priced via the Clopper-Pearson repetition factor $R(\epsilon^+)$ at confidence $\delta = 2^{-128}$. Rare failures ($k > 0$) multiply the cost by $R(\epsilon^+(k)) / R(\epsilon^+(0))$.
