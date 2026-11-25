import json
from pathlib import Path
import unittest
from datetime import datetime, timezone
from tools.validate_snapshot import validate


class ValidateTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = json.loads(Path("examples/synthetic.json").read_text())
        self.now = datetime(2026, 11, 26, tzinfo=timezone.utc)

    def check(self):
        return validate(json.dumps(self.snapshot).encode(), now=self.now)

    def test_example(self):
        self.assertEqual(self.check()["records"], 1)

    def test_duplicate(self):
        self.snapshot["records"].append(self.snapshot["records"][0])
        with self.assertRaises(ValueError):
            self.check()

    def test_nonvendor_reference_rejected(self):
        self.snapshot["synthetic"] = False
        with self.assertRaises(ValueError):
            self.check()

    def test_invalid_version_rejected(self):
        self.snapshot["records"][0]["fixed_version"] = "--bad"
        with self.assertRaises(ValueError):
            self.check()
