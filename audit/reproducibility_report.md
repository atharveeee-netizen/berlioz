# Clean Environment Reproducibility Report

## 1. Zero External Dependency Verification
The Berlioz repository is completely self-contained. A fresh clone requires no sibling folders (`../quantum-competition`) and no machine-specific absolute paths.

### Documented Build Flow:
```bash
# 1. Environment Setup
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. Build All Submissions Atomically
python src/build_all_submissions.py

# 3. Certify Best Candidate Portfolio
python src/verify_portfolio.py submission.zip --mode quick --dqi-shots 2048

# 4. Full Unit & Security Regression
python -m unittest discover tests/
```

## 2. Component Digest Manifest
All components utilized in candidate generation have fixed cryptographic digests:

| Component | Target Location | File Size | SHA-256 Digest |
|---|---|---:|---|
| Invsqrt 62Q Champion | `fact/components/invsqrt_62q.kmb` | 468,143 B | `a568bc79348165bad5be2349960d200300c5639ffd2142aca6d548e764a399d9` |
| Invsqrt 63Q Alternate | `fact/components/invsqrt_63q.kmb` | 459,891 B | `0766a111a76f241aa57fbbed466436d743be13436943ddb0628c291ca07d67d6` |
| DQI 889Q Champion | `build/dqi.kmb` | 544,419,428 B | `7a378f4755605e0c5fa6117f808891bf8dcf0797d047155e6d4c9e75e3c99421` |
| DQI 877Q Alternate | `build/dqi_877q.kmb` | 557,750,701 B | `3c09b8374a4cfcf05bb239f603c4cf7e7261d76ea242fc4bf5cf61b6016df36a` |
| Chemistry R=8 npz | `fact/r8_champion/submission.npz` | 27,872 B | `bce0e4d0b16259ae65977a28e8316e6d117c4b4fe5ef2594a896cf8964d4c82b` |
| Slot 1 Final Archive | `build/submissions/submission_slot1_chem_champion.zip` | 78,665,545 B | `f2d95c2ff0a53e26d76f7f904aa934a4298c83184fb3db94ab940aa10252c234` |
| Certified Submission | `submission.zip` | 78,665,545 B | `f2d95c2ff0a53e26d76f7f904aa934a4298c83184fb3db94ab940aa10252c234` |

All archives build with 100% deterministic contents and validate without exceptions.
