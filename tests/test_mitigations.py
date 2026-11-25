from datetime import date
import json
from pathlib import Path
import unittest
from tools.validate_mitigations import validate


class MitigationTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads(Path("guidance/mitigations-v1.json").read_text())

    def check(self):
        return validate(json.dumps(self.catalog), date(2026, 11, 25))

    def test_dataset(self):
        self.assertEqual(self.check()["records"], 5)

    def test_duplicate_rejected(self):
        self.catalog["records"].append(self.catalog["records"][0])
        with self.assertRaises(ValueError):
            self.check()

    def test_nonofficial_reference_rejected(self):
        self.catalog["records"][0]["source"] = "https://example.invalid/"
        with self.assertRaises(ValueError):
            self.check()

    def test_unexpected_assessment_rejected(self):
        self.catalog["records"][0]["assessment"] = "other"
        with self.assertRaises(ValueError):
            self.check()
