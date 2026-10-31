# SYSTEM ARCHITECTURE
## Berlioz — Verifiable Quantum Circuit Compilation Engine

**Framework:** Syzygy Spec-Driven Development Standard (v1.0.0)  

---

### 1. Component Topology Mesh

```mermaid
graph TD
    subgraph Syzygy AI Co-Design Engine
        A[Problem Specification] --> B[Syzygy AI Optimizer]
        B --> C1[Tower-42 Linear Scheduler]
        B --> C2[MBUC Phase Peeling Engine]
        B --> C3[Banked ANF Synthesizer]
    end

    subgraph Circuit Synthesis & Packaging
        C1 --> D[Narrow-240 DQI Decoder]
        C2 --> E[62Q Invsqrt Circuit]
        C3 --> F[R=8 Chemistry Matrices]
        D --> G[submission.zip Packaging]
        E --> G
        F --> G
    end

    subgraph Official Verifier Gate
        G --> H1[verify_invsqrt_official]
        G --> H2[verify_dqi_official]
        G --> H3[verify_chemistry_official]
        H1 --> I[Integrated Verification Suite]
        H2 --> I
        H3 --> I
    end

    subgraph Pareto Audit & Release
        I --> J[Official Scoring Module]
        J --> K[Pareto Frontier Ledger]
        K --> L{Better Than Champion?}
        L -- Yes --> M[Update Champion Vault]
        L -- No --> N[Preserve Current Champion]
    end
```

---

### 2. Module Responsibilities
* **`src/syzygy_ai_quantum_optimizer.py`:** Autonomous evaluator-guided optimization passes.
* **`extracted_dqi/blocks/dqi/team-1028-narrow240/source/`:** 86 verified DQI algorithm units.
* **`audit/integrated_verification_suite.py`:** Standalone end-to-end official benchmark verifier harness.
* **`src/verify_portfolio.py`:** Canonical portfolio scoring and resource accounting module.
