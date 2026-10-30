"""Unit tests for the submission format and constraint validator.
SPDX-License-Identifier: Apache-2.0
"""
import unittest
import sys, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'src')]

import validate_submission as VS

class TestSubmissionValidator(unittest.TestCase):
    def test_live_submission_zip(self):
        """Verify that the official live submission archive passes all 5 competition rules."""
        zip_path = Path('C:/Users/noobg/.gemini/antigravity-ide/scratch/quantum-competition/submission_2299.zip')
        if not zip_path.exists():
            raise unittest.SkipTest("submission_2299.zip not found")
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
        self.assertFalse(VS.validate_submission('nonexistent_path_xyz.zip'))

    def test_malformed_archive_rejection(self):
        """Verify that an archive with missing or incorrect components is rejected."""
        import tempfile, zipfile
        with tempfile.TemporaryDirectory() as td:
            bad_zip = Path(td) / "bad_sub.zip"
            with zipfile.ZipFile(bad_zip, 'w') as z:
                # Add only a dummy file, missing required circuits
                z.writestr("dummy.txt", "corrupt content")
            self.assertFalse(VS.validate_submission(str(bad_zip)))

if __name__ == '__main__':
    unittest.main()
