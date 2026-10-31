"""Unit tests and adversarial security tests for the hardened submission validator.
SPDX-License-Identifier: Apache-2.0
"""
import unittest
import sys, os, tempfile, zipfile
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'src')]

import validate_submission as VS

class TestSubmissionValidator(unittest.TestCase):
    def test_live_submission_zip(self):
        """Verify that the official live submission archive passes all 5 competition rules."""
        zip_path = ROOT / 'audit/baseline_vault/submission_2299.zip'
        if not zip_path.exists():
            zip_path = ROOT / 'submission.zip'
        self.assertTrue(zip_path.exists(), f"Missing test archive: {zip_path}")
        self.assertTrue(VS.validate_submission(str(zip_path)))

    def test_all_four_generated_slots(self):
        """Verify that all 4 generated submission slot archives pass all 5 competition rules."""
        sub_dir = ROOT / 'build/submissions'
        for slot in range(1, 5):
            zips = list(sub_dir.glob(f'submission_slot{slot}_*.zip'))
            self.assertTrue(len(zips) >= 1, f"Missing slot {slot} archive in {sub_dir}")
            zip_path = zips[0]
            self.assertTrue(VS.validate_submission(str(zip_path)), f"Slot {slot} archive failed validation: {zip_path}")

    def test_missing_path(self):
        """Verify that a nonexistent path fails gracefully without unhandled exceptions."""
        self.assertFalse(VS.validate_submission('nonexistent_path_xyz.zip', verbose=False))

    def test_malformed_archive_rejection(self):
        """Verify that an archive with missing or incorrect components is rejected."""
        with tempfile.TemporaryDirectory() as td:
            bad_zip = Path(td) / "bad_sub.zip"
            with zipfile.ZipFile(bad_zip, 'w') as z:
                z.writestr("dummy.txt", "corrupt content")
            self.assertFalse(VS.validate_submission(str(bad_zip), verbose=False))

    def test_adversarial_path_traversal(self):
        """Adversarial Test: Validator must reject archives containing path traversal ('..')."""
        with tempfile.TemporaryDirectory() as td:
            bad_zip = Path(td) / "traversal.zip"
            with zipfile.ZipFile(bad_zip, 'w') as z:
                z.writestr("../evil.txt", "payload")
            self.assertFalse(VS.validate_submission(str(bad_zip), verbose=False))

    def test_adversarial_absolute_path(self):
        """Adversarial Test: Validator must reject archives containing absolute paths."""
        with tempfile.TemporaryDirectory() as td:
            bad_zip = Path(td) / "absolute.zip"
            with zipfile.ZipFile(bad_zip, 'w') as z:
                z.writestr("/etc/passwd", "root:x:0:0")
            self.assertFalse(VS.validate_submission(str(bad_zip), verbose=False))

    def test_adversarial_corrupt_zip(self):
        """Adversarial Test: Corrupt or truncated zip files must fail gracefully."""
        with tempfile.TemporaryDirectory() as td:
            corrupt = Path(td) / "corrupt.zip"
            corrupt.write_bytes(b"PK\x03\x04not_a_real_zip_file_payload")
            self.assertFalse(VS.validate_submission(str(corrupt), verbose=False))

    def test_adversarial_bad_npz_shape(self):
        """Adversarial Test: Reject submission.npz with invalid orbital dimension (not 76)."""
        import kickmix as km
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            (p / 'dfthcsos').mkdir()
            # Valid dummy kmb circuit
            b = km.CircuitBuilder()
            b.alloc_qubits(10)
            c = b.finish_circuit()
            c.to_file(str(p / 'invsqrt.kmb'), format='kmb')
            c.to_file(str(p / 'dqi.kmb'), format='kmb')
            c.to_file(str(p / 'dfthcsos/angle_k_0.kmb'), format='kmb')

            # Invalid U shape (orbitals=50 instead of 76)
            np.savez(p / 'dfthcsos/submission.npz',
                     U=np.zeros((10, 10, 50), dtype=np.float64),
                     W=np.zeros((10, 10, 10), dtype=np.float64),
                     tree_edges=np.zeros((10, 2), dtype=np.int64))

            bad_zip = p / "bad_npz.zip"
            with zipfile.ZipFile(bad_zip, 'w') as z:
                z.write(p / 'invsqrt.kmb', 'invsqrt.kmb')
                z.write(p / 'dqi.kmb', 'dqi.kmb')
                z.write(p / 'dfthcsos/angle_k_0.kmb', 'dfthcsos/angle_k_0.kmb')
                z.write(p / 'dfthcsos/submission.npz', 'dfthcsos/submission.npz')

            self.assertFalse(VS.validate_submission(str(bad_zip), verbose=False))

if __name__ == '__main__':
    unittest.main()
