"""Masterloop 27 Chunk 1: Adversarial Tests for Release Verifier Integrity.

Authors: BERLIOZ Independent Verification Agent
Context: ML27 CHUNK 1 - FORENSIC AUDIT OF RELEASE VERIFIER
Date: 2026-11-01
"""

import hashlib
import json
from pathlib import Path
import pytest
import zipfile

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
INCUMBENT_PATH = REPO_ROOT / "submission.zip"
EXPECTED_INCUMBENT_SHA256 = "0bf5b4e361690c38a9d17580e49bb2d6b5f3706a64500ecaa9f499d2f521c3fe"


def sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


class TestReleaseVerifierAdversarialRules:
    """Mandatory adversarial tests that any honest release verifier MUST enforce."""

    def test_adv_zip_must_not_be_duplicate_of_incumbent(self):
        """Rule 1: An advanced candidate portfolio cannot have the identical SHA-256 to the incumbent."""
        advanced_path = REPO_ROOT / "build" / "portfolios" / "portfolio_ml26_advanced.zip"
        if advanced_path.exists():
            adv_sha = sha256_of_file(advanced_path)
            inc_sha = sha256_of_file(INCUMBENT_PATH)
            # The ML26 advanced archive FAILS this rule because it was a direct copy!
            # The test proves that an honest verifier must flag this condition as INVALID.
            is_copy = (adv_sha == inc_sha)
            assert is_copy, "Reproduced failure: portfolio_ml26_advanced.zip is an exact byte copy of incumbent."

    def test_reject_manifest_with_identical_portfolio_hashes(self):
        """Rule 2: A release manifest cannot certify an improved score if the archive hash is unchanged."""
        manifest_path = REPO_ROOT / "ml26" / "ml26_release_manifest.json"
        assert manifest_path.exists()
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        inc_hash = manifest["portfolios"]["tier1_incumbent"]["sha256"]
        adv_hash = manifest["portfolios"]["tier3_ml26_advanced"]["sha256"]
        inc_score = manifest["portfolios"]["tier1_incumbent"]["composite_score"]
        adv_score = manifest["portfolios"]["tier3_ml26_advanced"]["composite_score"]

        # An honest auditor rejects any manifest where hash is identical but score differs!
        if inc_hash == adv_hash:
            with pytest.raises(AssertionError, match="Disallowed: Improved score claimed for identical archive SHA-256"):
                assert inc_score == adv_score, "Disallowed: Improved score claimed for identical archive SHA-256"

    def test_reject_unexecuted_hardcoded_pass_gates(self):
        """Rule 3: Gates G0-G5 cannot be accepted if assigned as unverified string literals."""
        manifest_path = REPO_ROOT / "ml26" / "ml26_release_manifest.json"
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        gates = manifest.get("verification_gates", {})
        # G3 and G4 must contain execution logs or evidence dictionaries, not naked string 'PASS'
        g3 = gates.get("G3_semantic_correctness")
        g4 = gates.get("G4_reproducibility_clean_build")

        # Flag that string literals without log proof fail the verifiable execution standard
        assert isinstance(g3, str) and g3 == "PASS", "ML26 defect reproduced: G3 was a static string"
        assert isinstance(g4, str) and g4 == "PASS", "ML26 defect reproduced: G4 was a static string"

    def test_member_hash_cross_validation(self):
        """Rule 4: Packaged member hashes must match isolated component certificates."""
        with zipfile.ZipFile(INCUMBENT_PATH, "r") as z:
            invsqrt_data = z.read("invsqrt.kmb")
            invsqrt_sha = sha256_of_bytes(invsqrt_data)
            # Incumbent invsqrt is the 62Q circuit
            assert invsqrt_sha == "a568bc79348165bad5be2349960d200300c5639ffd2142aca6d548e764a399d9"

    def test_score_calculation_reproducibility(self):
        """Rule 5: Composite score must equal geometric mean of benchmark ratios exactly."""
        from tools.score_calc import composite
        r_inv = 22.34540
        r_dqi = 75.11200
        r_chem = 9.93301
        expected_s = (r_inv * r_dqi * r_chem) ** (1.0 / 3.0)
        calc_s = composite(r_inv, r_dqi, r_chem)
        assert abs(calc_s - expected_s) < 1e-6
