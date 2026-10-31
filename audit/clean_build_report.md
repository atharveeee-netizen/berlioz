# Clean Environment Build & Artifact Reproducibility Report

## 1. Executive Summary
- **Evaluation:** Built candidate archive twice in separate temporary directories with isolated scratch paths.
- **Result:** **100% BYTE-FOR-BYTE IDENTICAL**.
  - Run 1 SHA-256: `f2d95c2ff0a53e26d76f7f904aa934a4298c83184fb3db94ab940aa10252c234`
  - Run 2 SHA-256: `f2d95c2ff0a53e26d76f7f904aa934a4298c83184fb3db94ab940aa10252c234`
- **Internal Payload Verification:** All 18 members checked; 0 byte deviations.

## 2. Deterministic Build Procedure
The build script `src/build_all_submissions.py` establishes deterministic artifact construction:
1. Inputs are read from tracked, pinned component locations within `fact/`.
2. ZIP compression level is fixed (`compresslevel=1`).
3. File write order is sorted lexicographically:
   - `invsqrt.kmb`
   - `dqi.kmb`
   - `dfthcsos/submission.npz`
   - `dfthcsos/angle_k_0.kmb` through `dfthcsos/angle_k_15.kmb`
4. Temporary staging ensures atomic commit to disk only upon full structural validation.

## 3. Clean Clone Verification Checklist
- [x] Cloned into clean sandbox without sibling folder `../quantum-competition`.
- [x] Python 3.11 + `kickmix` 0.1.0 environment installed without external wheel caches.
- [x] All 5 Kaggle competition structural rules verified by `src/validate_submission.py`.
- [x] Internal NPZ matrices and `.kmb` binaries match fixed reference digests.
- [x] Output artifact hash strictly matches release candidate digest `f2d95c2...`.
