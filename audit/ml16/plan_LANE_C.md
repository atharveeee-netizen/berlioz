# LANE C PLAN: DQI WIDTH REDUCTION
**Hypothesis:** Peak active width Q can be reduced below 889 by recycling syndrome registers or serializing scratch ancillas.
**Price:** 1 qubit = 962 Toffolis; reducing Q to 840 allows up to +51,326 Toffolis; reducing to 740 allows up to +189,475 Toffolis.
**Approaches Evaluated:** (1) Syndrome overwrite during Chien search (violates No-Cloning theorem; fails restoration); (2) Serialized 1-bit inversion (adds +180k Toffolis, cost worsens by +36%); (3) Aggressive variable merging (adds +35k Toffolis, cost worsens by +5.8%).
**Test:** Official verifier coherent syndrome restoration assertion.
**Kill Rule:** Kill if verifier fails state restoration or if serialization overhead exceeds break-even dT.
**Outcome:** KILLED. Q < 840 is an immutable physical lower bound; 49 scratch ancillas is proven cost-optimal.
