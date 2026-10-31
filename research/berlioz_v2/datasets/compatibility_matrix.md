# DATASET-TO-ARCHITECTURE COMPATIBILITY MATRIX (CHUNK C9)
## Systematic Mapping of 20 Benchmark Suites to Berlioz Subsystems

---

| Dataset ID | Dataset Name | Primary Berlioz Architecture | Adaptation / Lowering Path | Correctness Oracle Path | Compatible? | Incompatibility Notes |
|---|---|---|---|---|---|---|
| `DS-01` | **QASMBench** | General Optimizer | OpenQASM 2.0 parser & lowerer | Qiskit Aer statevector simulation | **YES** | None (direct gate-level) |
| `DS-02` | **RevLib** | Reversible Logic & GF(2^n) | Truth-table to Toffoli lowerer | Exhaustive boolean evaluation | **YES** | Classical logic only |
| `DS-03` | **MQT Bench** | General Optimizer | MQT QASM 3.0 transpiler | QCEC equivalence checker | **YES** | Multi-level circuits |
| `DS-04` | **Qualtran** | GF(2^n) & Modular Arithmetic | Qualtran Bloq to Math-IR adapter | Symbolic matrix equivalence check | **YES** | Fault-tolerant arithmetic |
| `DS-05` | **SupermarQ** | General Optimizer | Cirq circuit to Math-IR mapper | Unitary matrix statevector check | **YES** | Low-depth kernels |
| `DS-06` | **QFOTON** | Phase Optimizer (PhasePoly) | Phase form to parity polynomial | Matroid synthesis formal check | **YES** | Diagonal subcircuits |
| `DS-07` | **PyZX Corpus** | General Optimizer | ZX-diagram to Clifford+T lowerer | ZX graph equality verification | **YES** | Spider graph rewrites |
| `DS-08` | **OpenFermion** | Chemistry Engine | FCIDUMP integrals to double-fac | Configuration interaction (CI) energy | **YES** | Electronic structure |
| `DS-09` | **Gluzdov FeMoco** | Chemistry Engine | NPZ basis tensor converter | Analytical spectral norm verifier | **YES** | 65x60x30 factorizations |
| `DS-10` | **Kauers Tensors** | GF(2^n) Arithmetic (Tower42) | Bilinear matrix generator to Math-IR | Bilinear tensor rank validator | **YES** | Finite-field multipliers |
| `DS-11` | **DQI RS Decoders**| DQI State Machine | KMB state machine generator | Official Kickmix shot simulator | **YES** | QEC syndrome decoders |
| `DS-12` | **Gidney Fixed-Pt** | Invsqrt Engine | Precision normalization to fixed-pt | Analytical IEEE-754 error bound | **YES** | Elementary math |
| `DS-13` | **QASM Chemistry** | Chemistry Engine | Givens rotation transpiler | State fidelity active space check | **YES** | VQE rotation networks |
| `DS-14` | **Shor Modular** | GF(2^n) & Modular Arithmetic | Modular exponentiation track parser | Arithmetic modular cycle orbit | **YES** | Reversible number theory |
| `DS-15` | **IBM Quantum Vol**| General Optimizer | Qiskit circuit transpiler | Qiskit Aer unitary simulation | **YES** | Haar-random unitaries |
| `DS-16` | **Amy Matroid** | Phase Optimizer (PhasePoly) | T-par format to PhasePolynomialTerm | Phase polynomial semantic oracle | **YES** | Minimal T-count synthesis |
| `DS-17` | **Stim Surface** | DQI / Stabilizer Tracker | Stim circuit tableau lowerer | Stim stabilizer tableau simulator | **YES** | Stabilizer syndrome cycles |
| `DS-18` | **Anthropic Div** | GF(2^n) & Invsqrt (MBUC) | Divstep step state machine | Stepwise GCD invariant check | **YES** | Modular inversion |
| `DS-19` | **QLib Layout** | General Optimizer | Physical coupling graph mapper | SWAP routing fidelity verifier | **YES** | Grid mapping |
| `DS-20` | **QCC Local SOTA** | Full Berlioz Unified Portfolio| Native KMB / NPZ / Horner pipeline | Official competition verifiers | **YES** | Competition benchmarks |

---

### Incompatible Hardware & Pulse Datasets (Explicitly Excluded)
1. **IBM Qiskit Pulse Schedules:** Excluded because Berlioz operates strictly at the fault-tolerant logical Clifford+T / Toffoli level rather than microwave drive Hamiltonian calibration.
2. **Analog Neutral Atom Hamiltonian Ensembles:** Excluded due to continuous spatial coordinates incompatible with discrete topological stabilizer patches.
