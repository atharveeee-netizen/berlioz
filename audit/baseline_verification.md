# Baseline Verification Report — Masterloop 15

## 1. Environment & Commit Freeze
- **Repository Commit:** `2508ca1143d7aaa5eb443dd3120d2fc982a66e73`
- **Branch:** `master`
- **Compiler:** `kickmix` 0.1.0 on Python 3.11.9 (Windows AMD64)
- **Baseline Vault:** Preserved in `audit/baseline_vault/`
  - `submission_2299.zip` (`891e55a6710587f0517b3d462966b1af23f05eccf95ea3fe408e8813b37e6fa2`)
  - `submission.zip` (`f2d95c2ff0a53e26d76f7f904aa934a4298c83184fb3db94ab940aa10252c234`)
  - `invsqrt.kmb` (`a568bc79348165bad5be2349960d200300c5639ffd2142aca6d548e764a399d9`)
  - `dqi.kmb` (`7a378f4755605e0c5fa6117f808891bf8dcf0797d047155e6d4c9e75e3c99421`)

## 2. Benchmark I: Invsqrt (62Q Champion)
- **Problem Instance:** $n_p = 10$, width = 22, $x \in [1, 3133452]$
- **Restoration:** Perfect ($x$ register restored across all shots; scratch returns cleanly to $|0\rangle$).
- **Rotation Budget:** Min margin verified $> 0$; $\epsilon = 5.57 \times 10^{-9}$ turns.
- **Resource Counts:**
  - $Q = 62$
  - Per-shot Toffoli count: $1332.3$
  - Rotation gates: $41.0$ (T-equivalent: $1622.7$)
  - Candidate Cost: $100,608.7$
  - Reference Cost: $2,076,774.23$
  - **Ratio:** **`20.64210x`**

## 3. Benchmark II: DQI (889Q Reed-Solomon MBUC Decoder)
- **Parameters:** $m = 4095, n = 70, b = 12, r = 2016, \delta = 2^{-128}$
- **Shots Evaluated:** 2,048 shots (0 value errors, 0 phase errors).
- **Clopper-Pearson Confidence Overhead:**
  - At $k=0$ errors in $N=102,400$ shots: $\epsilon^+ = 8.660587 \times 10^{-4}$
  - $R(0) = 1.19126046$
- **Resource Counts:**
  - $Q = 889$
  - Mean Toffolis: $433,783.5$
  - Candidate Cost: $1.19126046 \times 889^2 \times 433,783.5 = 408,401,363,222$
  - Reference Cost: $24,439,463,583,672.93$
  - **Official Ratio:** **`59.84231x`**

## 4. Benchmark III: Chemistry (FeMoCo76o113e)
- **Parameters:** $N_{\text{orbitals}} = 76, N_{\text{electrons}} = 113, \text{brot} = 16, R = 8$
- **Resource Counts:**
  - $Q = 430$
  - Total Toffolis: $16,266$
  - $\lambda_{\text{eff}} = 48.323602$
  - Candidate Cost: $337,993,822.4$
  - Reference Cost: $3,355,599,588.32$
  - **Ratio:** **`9.92799x`**

## 5. Composite Metric
$$GM = (20.64210 \times 59.84231 \times 9.92799)^{1/3} = \mathbf{23.06081}$$
(Kaggle graded equivalent with private salt sampling noise: **22.99562**).
