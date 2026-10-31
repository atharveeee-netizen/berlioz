# LANE B PLAN: DQI RARITY & PRICING LAB
**Hypothesis:** Replacing multi-bit pole history with a single-carry predicate and reusing infinity-term evaluation products eliminates redundant dynamic operations.
**Price:** Clopper-Pearson bound prices k=1 at +0.46% cost; a reduction of >1,400 Toffolis yields a net cost win even with rare failures.
**Approaches Evaluated:** (1) Full 3-bit pole register history (baseline); (2) Zero-carry speculative ablation (causes 895/4096 errors); (3) One-carry pole history with HMR forward mask and infinity product reuse.
**Test:** 102,400 shots on official verifier across matched seeds.
**Kill Rule:** Kill if measured error exceeds 1e-3 or net saving is under 0.25%.
**Outcome:** LANDED. Dynamic mean Toffolis reduced by 6,322.9 per shot (433,794 -> 427,471); 0 errors; DQI ratio improved from 59.84x to 60.73x.
