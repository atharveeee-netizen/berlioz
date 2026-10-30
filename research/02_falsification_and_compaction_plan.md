# STAGE 6: PRE-REGISTERED EXPERIMENT PLAN (DQI WIRE COMPACTION)

```yaml
EXPERIMENT: DQI-Wire-Compaction-01
TARGET_BENCHMARK: Benchmark II (DQI RS Syndrome Decoder)
HYPOTHESIS: Re-ordering intermediate register allocations and recycling GF(2^12) arithmetic scratch registers via a unified LIFO wire pool will reduce DQI peak active qubits Q from 889 to <= 720 without altering Toffoli counts or introducing phase/value errors.
SUCCESS_CRITERION: DQI Q <= 720 on full instance (or >= 15% reduction on mini-instances) with 100% bit-exact equivalence on verification shots.
FAILURE_CRITERION: Any register overlap collision, leaked scratch wire, or Q reduction < 5%.
ABANDON_CONDITION: If Kickmix's internal register naming rules enforce rigid wire index segregation that prevents global ancilla sharing.
```

## 1. Research Question
In Decoded Quantum Interferometry, the competition cost law is:
$$\text{Cost}_{\text{dqi}} = R(\epsilon^+) \times Q^2 \times T_{\text{mean}}$$
Because cost scales quadratically with $Q$, reducing peak live qubits $Q$ provides higher marginal return than gate reductions:
$$\left(\frac{889}{720}\right)^2 = \mathbf{1.524\times \text{ improvement (-34.4% cost)}}$$
$$\left(\frac{889}{520}\right)^2 = \mathbf{2.923\times \text{ improvement (-65.8% cost)}}$$

Can we construct a register compaction layer over `FullTowerBuilder` that actively tracks the lifespan of temporary Galois field workspace wires and prevents unneeded wire index growth?

## 2. Experimental Setup
* **Baseline:** Current `FullTowerBuilder` producing mini-DQI with $Q=240$ and full-scale DQI with $Q=889$.
* **Intervention:** Linear-scan register compaction tracking live intervals and mapping temporary allocations to a compact physical wire pool.
* **Control:** Exact mathematical equivalence tested on random syndrome instances.
