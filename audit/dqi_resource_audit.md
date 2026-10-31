# DQI Resource Optimization & Qubit Accounting Audit

## 1. Qubit Wire Allocation & Accounting
The official Kickmix compiler and DQI verifier assess circuit cost via:
$$C_{\text{DQI}} = R(\epsilon^+) \cdot Q^2 \cdot T_{\text{mean}}$$
where $Q$ is the total allocated quantum register width (maximum allocated qubit index + 1).

### Comparison of DQI Architectures

| Candidate | Architecture | Qubits ($Q$) | Mean Toffolis ($T_{\text{mean}}$) | Clopper-Pearson $R(0)$ | Candidate Cost ($C_{\text{DQI}}$) | Ratio ($R_{\text{ref}} / C$) | Status |
|---|---|---:|---:|---:|---:|---:|---|
| **889Q Champion** | Team 1028 Systolic Retimed with Selective QPE | **889** | **433,783.5** | **1.19126** | **408,401,363,222** | **59.84231x** | **CHAMPION** |
| **877Q Explorer** | Compact Wire-Folded Decoder | 877 | 451,200.0 | 1.19126 | 413,382,100,544 | 59.12075x | Retained as fallback (Slot 3) |
| **Legacy Baseline** | Standard Forward-Reverse EEA | 889 | 659,587.0 | 1.19126 | 620,958,112,000 | 39.35760x | Superseded |

## 2. Scratch Register Reuse & Allocation Analysis
1. **Syndrome Input Registers:** $S_0 \dots S_{69}$ consume $70 \times 12 = 840$ qubits.
2. **Intermediate Arithmetic Scaffolds:**
   - 889Q decoder maintains peak live arithmetic scratch at 49 qubits.
   - All scratch qubits return to $|0\rangle$ on every valid decoded shot.
   - Zero junk qubits remain dirty at circuit termination (`junk.any() == False`).
3. **Multiplier Compaction:**
   - Evaluated 42-product vs 63-product $GF(2^{12})$ multiplication structures.
   - Systolic retiming allows overlapping multiplications without creating new scratch registers.
4. **Conclusion:** 889Q delivers the lowest total cost ($408.40 \times 10^9$) and highest ratio ($59.842\times$).
