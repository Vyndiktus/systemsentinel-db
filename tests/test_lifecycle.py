import json
from datetime import date
from pathlib import Path
import unittest
from tools.validate_lifecycle import validate


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.dataset = json.loads(Path("maintenance/lifecycle-v1.json").read_text())

    def check(self):
        return validate(json.dumps(self.dataset), date(2026, 11, 25))

    def test_reviewed_dataset(self):
        self.assertEqual(self.check()["records"], 7)

    def test_duplicate(self):
        self.dataset["records"].append(self.dataset["records"][0])
        with self.assertRaises(ValueError):
            self.check()

    def test_invalid_date(self):
        self.dataset["records"][0]["extended_until"] = "2026-02-31"
        with self.assertRaises(ValueError):
            self.check()

    def test_unofficial_source(self):
        self.dataset["records"][0]["source"] = "https://example.invalid"
        with self.assertRaises(ValueError):
            self.check()

    def test_future_review(self):
        self.dataset["reviewed_on"] = "2026-11-26"
        with self.assertRaises(ValueError):
            self.check()
