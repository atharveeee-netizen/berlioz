# PUBLIC NOTEBOOK & COMPETITOR WATCH
## Recorded for Masterloop 16 (Chunk C2)

---

## 1. MONITORED PUBLIC NOTEBOOKS

| Notebook Ref | Title | Author | Votes | Claimed Ratios | Architecture / Strategy | License | Disposition in Berlioz |
|---|---|---|---|---|---|---|---|
| `ahmedberatozer/quantum-ai-df-thc-group-compression` | Quantum AI - DF-THC Group Compression | Ahmed Berat Özer | 102 | Chem: ~9.93x | Angle grouping and phase polish | Apache-2.0 | **Grafted** (Özer phase patch incorporated into Invsqrt/Chem) |
| `somejoint/quantum-circuits-23-17-local-gm-889-qubit-dqi` | Quantum Circuits \| 23.17 Local GM: 889-Qubit DQI | Agniv Banerjee (SomeJoint) | 89 | DQI: ~60.4x | 889Q dynamic state machine | Apache-2.0 | **Grafted** (Combined with our one-carry history & infinity-product) |
| `dmitriigluzdov/quantum-circuit-compilation-from-source` | Quantum Circuit Compilation from Source | Dmitrii Gluzdov | 84 | Chem: ~9.92x | Double-factorized FeMoco baseline | Apache-2.0 | **Reference** (Foundational chemical tensor formulation) |
| `heliosli/the-dataset-is-public-now-enjoy` | The dataset is public now. Enjoy! | Heliosli | 82 | Multi-task | Aggregated dataset weights | Apache-2.0 | **Reference** (Public verification dataset mirror) |
| `alexchilton/22-57-lb-verified-three-task-portfolio` | 22.57 LB: Verified Three-Task Portfolio | Alex Chilton | 79 | GM: 22.57x | Unified 3-task pipeline baseline | MIT | **Reference** (Pre-apex integration baseline) |

---

## 2. DEAD-END SCREENING (Cross-Reference with Rule B10)
- **Continuous R=10 Chemistry:** Explored in early Gluzdov notebooks; hits cliff at $A=1220 \implies +65.7\%$ cost blowup. **REJECTED.**
- **Unpenalized R=1.0 in DQI:** Used in naive local estimators; strictly invalid on Kaggle leaderboard ($R(0)=1.19126$). **REJECTED.**
- **Z_POW in DQI:** Explicitly disallowed by competition circuit verifier contract. **REJECTED.**
- **invsqrt T_per_toffoli=4:** Incompatible with fault-tolerant grading model. **REJECTED.**
