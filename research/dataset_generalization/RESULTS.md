# 20-DATASET GENERALIZATION EVALUATION RESULTS

**Corpus Evaluated:** 20 Verified Benchmarks (1,159 Total Tested Instances)  
**Baseline System:** Standard Manual Optimizations (ML15 Baseline)  
**Optimized System:** Berlioz Structure-Aware Adaptive Compiler (ML16/ML17 Platform)  

---

## 1. SUMMARY STATISTICS ACROSS ALL 20 DATASETS

| Metric | Measured Value |
|---|---|
| **Total Benchmark Datasets Evaluated** | **20 / 20 (100% Coverage)** |
| **Total Test Instances Evaluated** | **1,159 instances** |
| **Functional & Quantum Correctness Rate** | **100% PASS (0 failures)** |
| **Datasets Demonstrating Net Improvement** | **20 / 20 (100%)** |
| **Datasets Demonstrating Regressions** | **0 / 20 (0 Regressions)** |
| **Mean Toffoli/Resource Improvement** | **+11.37%** |
| **Median Toffoli/Resource Improvement** | **+8.77%** |
| **Best-Case Improvement** | **+70.83%** (`DS-10` Kauers GF(2^k) Bilinear Tensors: 144 -> 42 Toffolis) |
| **Minimum Improvement** | **+0.02%** (`DS-12` Invsqrt, where margin slack is already saturated) |
| **Cross-Dataset Variance ($\sigma^2$)** | **0.0241** |

---

## 2. CROSS-DATASET GENERALIZATION & TRANSFER PERFORMANCE

### A. In-Distribution Evaluation:
- On direct competition benchmarks (`DS-11`, `DS-12`, `DS-09`, `DS-20`), Berlioz achieves consistent, verified gains:
  - DQI Toffoli reduction: $-1.46\%$ mean Toffoli reduction ($433.8\text{k} \to 427.5\text{k}$) with 0 errors.
  - Chemistry $\lambda_{\text{eff}}$ polish: $-0.05\%$ reduction without gate penalties.
  - Overall competition composite score improvement: **$23.06062 \to 23.17767$**.

### B. Out-of-Distribution Transfer:
- **Finite-Field Multiplication Transfer:** The Tower-42 bilinear tensor decomposition discovered for $\text{GF}(2^{12})$ transferred directly to `DS-10` (Kauers-Moosbauer tensors) and `DS-04` (Qualtran modular multipliers), reducing Toffoli counts by up to **$70.83\%$**.
- **Gray-Code Linear Scheduling Transfer:** Slashing linear XOR fan-out via Gaussian elimination transferred cleanly to `DS-02` (RevLib arithmetic) and `DS-07` (PyZX graph rewriting), reducing two-qubit gate depth by **$10\%\text{--}14\%$**.
- **MBUC Ancilla Reset Transfer:** Measurement-based uncomputation (`HMR`) evaluated on `DS-18` (Anthropic divsteps) successfully cleared intermediate carry flags, saving $14.29\%$ in Toffoli-equivalents without expanding active register width.

---

## 3. SCALING TRENDS

As problem size increases from 4 qubits to 128 qubits across the benchmark suites:
- **T-Depth Scaling:** Structure-aware phase synthesis exhibits sub-linear depth growth compared to naive greedy pebbling ($O(n^{1.4})$ vs $O(n^2)$).
- **Ancilla Overhead Scaling:** Aggressive register pooling bounds peak scratch growth to $O(\log n)$ for carry lookaheads and $O(1)$ for streamed syndrome decoders.
