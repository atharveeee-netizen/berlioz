# LANE D PLAN: INVSQRT PHASE & WORKSPACE
**Hypothesis:** Coalescing 41 rotations into fewer synthesized phase angles or pruning small angles reduces T_equiv.
**Price:** 1 qubit = 26.17 Toffoli-equivalents; 1% cost = 16.23 Toffoli-equivalents.
**Approaches Evaluated:** (1) Angle pruning (boundary margin slack = 3.17e-12 turns vs smallest angle 2.89e-11 turns; fails error tolerance); (2) Coalesced 4-rotation tree (expands width to 78Q, worsening cost by +10.1%); (3) 62Q MBUC architecture with HMR intermediate ancilla resets.
**Test:** 5,000 domain points on official Kickmix simulator.
**Kill Rule:** Kill if error exceeds 2^-64 or if width expansion cost exceeds rotation savings.
**Outcome:** BASELINE CHAMPION RETAINED. 62Q MBUC architecture verified strictly Pareto-optimal (ratio 20.64210x).
