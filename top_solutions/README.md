# Top Competitor Solutions & Reverse-Engineered Public Codebases

This directory contains the original and de-duplicated Jupyter notebooks from the leading competitors and top public research teams in the **Google Quantum AI — Verifiable Quantum Circuit Compilation** challenge.

---

## Solutions Index & Methodology Breakdown

### 1. Avazaku (Sargis Khachatryan)
* **Notebooks**:
  * `avazaku_dqi-exact-42-and-arithmetic-full-verification.ipynb`
  * `avazaku_c60-gauge-descent-full-xor-qrom.ipynb`
  * `avazaku_epigraph-rank-scales-889-qubit-dqi.ipynb`
  * `avazaku_gauge-prox-sign-copy-qrom.ipynb`
* **Core Contribution**:
  * **Exact 42-AND Bilinear Tensor Multiplication**: Derives an algebraic isomorphism $\text{GF}(2^{12}) \cong \text{GF}(8)[v]/(v^4+v+1)$ over $\text{GF}(8) = \text{GF}(2)[u]/(u^3+u+1)$ that evaluates 12-bit multiplication using only 42 binary products (cutting Toffolis by 21.18% over the 63-AND reference).
  * **Free-Gap SQP & C60 Gauge Descent**: Orthogonal rotation updates to Hamiltonian factorizations.

### 2. Michael Rustad
* **Notebook**:
  * `michaelrustad_vqcc-r10-merged-group-chemistry-12-87-lb.ipynb`
* **Core Contribution**:
  * **$R=10, B=129, C=60$ DF-THC Factorization**: Merges Ahmed Berat Ozer's $(26, 60, 30)$ groups into $(13, 129, 60)$ and prunes down to 10 groups via continuous L-BFGS optimization, reaching $\lambda_{\text{eff}} = 48.0311$ (19.65 mHa error).
  * **Signed Half-Open Givens Gauge**: Omits sign-bit loading using `bit(7) == bit(6)`.
  * **4-Address Banked QROM (`angles_qrom.py`)**: Uses pebble initialization (`pebbled_init`) and ANF eraser (`del_lookup_anf`) to achieve 277 Toffolis per angle circuit.

### 3. SomeJoint (Agniv Banerjee / GPT-6 Astra Pro Team)
* **Notebook**:
  * `somejoint_quantum-circuits-22-77-local-gm-889-qubit-dqi.ipynb`
* **Core Contribution**:
  * **889-Qubit Streamed DQI Decoder**: Seven-stage RS(4095, 4025) decoder with in-place $J$-fraction Bézout-Hankel phase solving, paired high-component extraction chains, and inverse19 reverse, reducing peak qubits to 889.
  * **$(R=8, B=143, C=60)$ Chemistry Factorization**: Public baseline for 15-circuit angle packing.

### 4. Yoyobar
* **Notebook**:
  * `yoyobar_lb-22-99-invsqrt-101-62-qubits.ipynb`
* **Core Contribution**:
  * **62-Qubit / 101-Toffoli `invsqrt`**: Reversible Newton-Raphson inverse square root with optimized seed table and zero-phase drift, achieving an improvement ratio of **$20.465\times$** (Score component: 101,479 cost).

### 5. Atakan Aldemir & Dmitriy Abulkhanov (dmitriyab)
* **Notebooks**:
  * `atakanaldemir_qcc-888q-repair-and-native-chemistry-co-design.ipynb`
  * `dmitriyab_vqcc-cand-0045-bit-identical-submission-rebuild.ipynb`
* **Core Contribution**:
  * Co-design of native chemistry rotation circuits with 888Q/889Q DQI repairs, establishing the exact bit-identical package that yields score 22.99.

### 6. Ahmed Berat Özer
* **Notebook**:
  * `ahmedberatozer_quantum-ai-df-thc-group-compression.ipynb`
* **Core Contribution**:
  * DF-THC group compression $(26, 60, 30)$ and origin of `gauge_qrom` and mask projection.

### 7. Artem1410 / anazemcev
* **Notebook**:
  * `anazemcev_quantum-circuits-signed-digit-memory.ipynb`
* **Core Contribution**:
  * Signed-digit memory allocation, paired-v6 decoder, and THC joint norm refits.

### 8. Busyaprime (Akmal Xodarev)
* **Notebook**:
  * `busyaprime_lb-22-86841-22x-cheaper-than-google-s-circuits.ipynb`
* **Core Contribution**:
  * 63-qubit `invsqrt` with 172 AND gates (re-synthesized from mrmeows' 186-gate version).

### 9. Sigmaborov
* **Notebook**:
  * `sigmaborov_22-85569-lb-exact-gauge-search.ipynb`
* **Core Contribution**:
  * Exact pairwise orthogonal gauge descent search for chemistry factorization.
