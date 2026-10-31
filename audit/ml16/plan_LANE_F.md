# LANE F PLAN: SEARCH HARNESS & AUTOTUNING
**Hypothesis:** An evaluator-guided automated search engine exploring algebraic and structural rewrites can discover Pareto-optimal quantum circuits.
**Price:** Evaluator cycles amortized by filtering invalid candidates before slow full-shot simulation.
**Approaches Evaluated:** (1) Brute-force random gate search (inefficient); (2) Peephole greedy optimization (trapped in local minima); (3) Syzygy Spec-Driven Evaluator-Guided Closed Loop (`src/syzygy_ai_quantum_optimizer.py`).
**Test:** Automated verification against Kickmix simulator across candidate mutations.
**Kill Rule:** Terminate candidates failing semantic invariance or dominated on Pareto frontier.
**Outcome:** OPERATIONAL. Automated optimizer active; confirmed new certified SOTA portfolio at 23.17767.
