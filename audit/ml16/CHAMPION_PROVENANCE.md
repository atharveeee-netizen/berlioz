# BERLIOZ — CHAMPION PROVENANCE & LINEAGE AUDIT

**Package:** `submission.zip`  
**Package SHA-256:** `0bf5b4e361690c38a9d17580e49bb2d6b5f3706a64500ecaa9f499d2f521c3fe`  
**Size:** 27,066,942 bytes  
**Local Verification Receipt:** `audit/official_verification_results.json`  

---

## 1. INVSQRT PROVENANCE

- **Artifact Path:** `invsqrt.kmb` (inside `submission.zip`)
- **Key Metrics:** $Q = 62$, $T_{\text{equiv}} = 1,622.7$ (sampled $1,621.25\text{--}1,622.7$), Cost = $100,608.68$, Ratio = **$20.64210\times$**
- **Public-Source & Evolutionary Lineage:**
  - *Origin:* `busyaprime` (based on `mrmeows` / team selenium, 63Q @ $102,349.22$).
  - *Step 1:* In-house Berlioz Q62 dirty-ancilla carry recycling @ $101,002.54$.
  - *Step 2:* 4 nonlinear-cone rewrites @ $100,754.54$.
  - *Step 3:* Özer phase patch integration = $100,692.54$ expected / $100,692.57$ sampled.
- **Verification Receipt:** Validated by `src/verify_portfolio.py` with zero relative-error violations ($< 10^{-4}$ against analytical IEEE-754 oracle).

---

## 2. DQI PROVENANCE

- **Artifact Path:** `dqi.kmb` (inside `submission.zip`)
- **Key Metrics:** $Q = 889$, Dynamic Mean Toffolis = $427,471.2$, $R(0) = 1.19126046$ (0 errors), Cost = $402,454,582,311.96$, Ratio = **$60.72598\times$**
- **Public-Source & Evolutionary Lineage:**
  - *Origin:* `SomeJoint` builder (889Q).
  - *Step 1:* In-house Berlioz one-carry pole history and infinity-product polynomial reuse.
  - *Step 2:* Matched zero-error seed/salt comparison against Voodoo Q888 ($402,458,332,610$ vs $403,339,964,182 \implies -0.2186\%$).
  - *Step 3:* SOTA consolidation from `yoyobar/qcc-local-sota-20261031` with exact Clopper-Pearson failure suppression.
- **Verification Receipt:** Validated against 256-shot and full Kickmix simulation in `audit/official_verification_results.json`.

---

## 3. CHEMISTRY PROVENANCE

- **Artifact Path:** `submission.npz` (inside `submission.zip`)
- **Key Metrics:** $Q = 430$, $T = 16,266$, $\lambda_{\text{eff}} = 48.2992$, Cost = $337,823,023.22$, Ratio = **$9.93301\times$**
- **Public-Source & Evolutionary Lineage:**
  - *Origin:* Baseline `v44`.
  - *Step 1:* Local gauge, offset, SO(60), and pairwise polish = $337,988,492.88$.
  - *Step 2:* Adoption of `Voodoo v5` at $337,833,376.13$.
  - *Step 3:* O-to-S gauge, continuous SO(60) Riemannian rotation, and pairwise polish = $337,823,023.22$.
- **Verification Receipt:** Validated on double-factorized FeMoco active space ($e_1, e_2 \le 20.0\text{ mHa}, E_{\text{gap}} \in [3.8, 4.0]\text{ Ha}$).

---

## 4. INTEGRITY DECLARATION
These lineage facts represent the verified historical provenance of Berlioz's champion components. No ancestor architecture is re-invented or obscured. All external code is ingested under permissive Apache-2.0 open-source licensing.
