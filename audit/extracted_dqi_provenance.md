# Extracted 889Q DQI Implementation: Provenance & Cryptographic Audit

## 1. Upstream Origin & Repository Path
- **Audit Target:** `extracted_dqi/blocks/dqi/team-1028-narrow240/source/`
- **Origin:** Research Team 1028 ("narrow240" systolic retimed decoder architecture).
- **Core Builder:** `build.py` invoking `exp/r-main/narrow240/decode_retimed.py`.
- **Target Output Digest:** `6349d2bc82eb1ef3a4e8c52c71a312823d756532517463b5e18eb25cc81195a8`

## 2. Cryptographic Source Integrity Audit
- **Manifest:** `source_sha256.json` (86 tracked source files).
- **Audit Tool:** `audit/verify_extracted_dqi_hashes.py`.
- **Verification Results:**
  - Files Verified: **86 / 86** (**100.0%** match).
  - Missing Files: **0**.
  - Mismatches: **0**.
  - Windows CRLF Discovery: Files match bit-exact under standard Unix LF line normalization (Git on Windows translates `\n` to `\r\n` upon checkout unless `core.autocrlf` is unset).

## 3. Dynamic Source Rewriting & Execution Analysis
`decode_retimed.py` utilizes dynamic source inspection and runtime compilation:
```python
ext_source = inspect.getsource(ref.external_extraction)
old = 'inverse24_reverse209(b,v,local,K)'
assert ext_source.count(old) == 1
ext_source = ext_source.replace(old, '(inverse24_reverse19 if gi>=15 else inverse24_reverse209)(b,v,local,K)')
ext_env = dict(ref.external_extraction.__globals__, external_node_chain=external_node_chain, inverse24_reverse19=inverse24_reverse19)
exec(compile(ext_source, __file__, 'exec'), ext_env)
```
- **Risk Assessment:** While functional and deterministic when dependencies are pinned, runtime string substitution via `inspect.getsource` is brittle across Python minor versions.
- **Mitigation:** The compiled circuit is frozen into binary `.kmb` format (`build/dqi.kmb`), eliminating runtime `inspect` dependencies during submission verification and grading.

## 4. Verification Under Official Verifier
- Evaluated via `verifiers/dqi/verify_submission_dqi.py`:
  - Qubits: **889**
  - Mean Toffolis: **433,783.5**
  - Value Errors: **0 / 2,048** (0.0%)
  - Phase Errors: **0 / 2,048** (0.0%)
  - Repetition Overhead $R(0)$: **1.19126**
  - Official Score Ratio: **59.84231x**
- **Conclusion:** Accepted as the production Benchmark II champion.
