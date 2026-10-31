# Submission Validator Security & Adversarial Defense Audit

## 1. Executive Summary
- **Target File:** `src/validate_submission.py`
- **Test Suite:** `tests/test_submission_validator.py`
- **Result:** **8 / 8 tests passed in 17.44s**.
- **Security Posture:** Hardened against ZIP path traversal (`../`), absolute paths (`C:/`, `/etc`), symlinks, corrupt archives, memory exhaustion, decompression bombs, missing required NPZ matrices, and invalid orbital dimensions ($N \ne 76$).

## 2. Implemented Defense Mitigations

| Vulnerability Vector | Threat Description | Defense Mechanism in `validate_submission.py` | Status |
|---|---|---|---|
| **Path Traversal** | Malicious ZIP entry with `../` attempting to escape extract directory | Rejects any archive member with `..` in path or starting with `/` or `\\`. | **HARDENED** |
| **Absolute Paths** | Archive members targeting drive root (e.g. `C:\Windows`) | Rejects members matching `[a-zA-Z]:` or starting with root slash. | **HARDENED** |
| **Duplicate Entries** | Archive with multiple entries for the same filename to confuse parser | Validates that `len(set(namelist)) == len(namelist)`. | **HARDENED** |
| **Zip Bomb / Size Exhaustion** | Compressed file expanding into hundreds of gigabytes | Enforces `MAX_FILE_BYTES = 100 * 1024 * 1024` for individual files, `MAX_TOTAL_EXTRACTED_BYTES = 750 * 1024 * 1024` overall. | **HARDENED** |
| **Corrupt / Truncated Archive** | Corrupt ZIP headers crashing unhandled with tracebacks | Wrapped in robust `try...except zipfile.BadZipFile` returning clean `False`. | **HARDENED** |
| **Chemistry NPZ Structure** | Malformed or zero-dimension NPZ array | Checks for exact presence of `U`, `W`, and `tree_edges` keys; verifies orbital dimension is strictly 76 ($N=76$). | **HARDENED** |
| **Temporary File Leaks** | Abandoned extraction folders on disk upon error | Exception-safe extraction using `tempfile.TemporaryDirectory` within context manager. | **HARDENED** |

## 3. Adversarial Test Evidence
All 4 adversarial attack vectors were actively simulated against the validator:
1. `test_adversarial_path_traversal`: Attempted write outside sandbox $\to$ **REJECTED (PASS)**.
2. `test_adversarial_absolute_path`: Injected Windows drive letters $\to$ **REJECTED (PASS)**.
3. `test_adversarial_corrupt_zip`: Injected truncated binary stream $\to$ **REJECTED (PASS)**.
4. `test_adversarial_bad_npz_shape`: Injected $50 \times 50$ array instead of $76 \times 76 \to$ **REJECTED (PASS)**.
