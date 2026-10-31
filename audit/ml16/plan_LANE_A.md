# LANE A PLAN: DQI MULTIPLIER SWAP
**Hypothesis:** Replacing standard multiplication with rank-42 bilinear tensor over GF(8)[v]/(v^4+v+1) reduces linear CNOT overhead and gate congestion without increasing Q or Toffolis.
**Price:** 1% DQI cost reduction = 4,275 Toffolis = +0.077 composite points.
**Approaches Evaluated:** (1) Naive column reconstruction (420 CNOTs); (2) Tree-based XOR accumulation (210 CNOTs); (3) Gray-code delta scheduling (63 CNOTs).
**Test:** Verify bilinear identity over all 4,096^2 operand pairs; compile `temp_dqi_tower42.kmb`; run 256-shot official verifier.
**Kill Rule:** Demote lane if multiplier Toffolis exceed 42 or net score saving is under 0.1%.
**Outcome:** PASSED. Slashed linear CNOTs by 85% (63 CNOTs); verified 0 value/phase errors in live DQI binary.
