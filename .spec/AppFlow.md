# APPLICATION FLOW (AppFlow)
## Berlioz — Verifiable Quantum Circuit Compilation Engine

**Framework:** Syzygy Spec-Driven Development Standard (v1.0.0)  

---

### 1. Evaluator-Guided Optimization State Machine

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> ProposeHypothesis: New Algorithmic Mutation
    ProposeHypothesis --> SynthesizeDAG: Apply Rewrite Operator
    SynthesizeDAG --> CompileBinary: Generate .kmb / .npz
    CompileBinary --> OfficialSimulation: Execute Kickmix Verifier
    OfficialSimulation --> SemanticCheck: Check Value/Phase Errors
    
    SemanticCheck --> Rollback: Errors > 0 or Coherence Lost
    Rollback --> LogFailure: Record in Negative Results
    LogFailure --> Idle
    
    SemanticCheck --> ScoreContract: All Verifiers PASS
    ScoreContract --> ParetoCheck: Calculate Ratio & Composite S
    
    ParetoCheck --> RejectDominated: S <= Current Champion
    RejectDominated --> Idle
    
    ParetoCheck --> UpdateChampion: S > Current Champion
    UpdateChampion --> CleanPurge: Purge Temp Binaries
    CleanPurge --> CommitLedger: Record SHA-256 & Provenance
    CommitLedger --> [*]
```

---

### 2. Failure Rollback & Negative Results Policy
* Any candidate that produces non-zero value errors, non-zero phase drift, or fails ancilla cleanup is immediately aborted.
* Intermediate scratch binaries are purged from disk to prevent working tree contamination.
* All negative results are permanently recorded in `research/ml16_experiment_registry.json`.
