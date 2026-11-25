from datetime import date
import json
from pathlib import Path
import unittest
from tools.validate_guidance import validate


class GuidanceTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads(Path("guidance/sources-v1.json").read_text())

    def check(self):
        return validate(json.dumps(self.catalog), date(2026, 11, 25))

    def test_published_catalog(self):
        self.assertEqual(self.check()["references"], 6)

    def test_duplicate(self):
        self.catalog["sources"].append(self.catalog["sources"][0])
        with self.assertRaises(ValueError):
            self.check()

    def test_domain_mismatch(self):
        self.catalog["sources"][0]["url"] = "https://example.invalid/"
        with self.assertRaises(ValueError):
            self.check()

    def test_unexpected_fields(self):
        self.catalog["sources"][0]["extra"] = "unexpected"
        with self.assertRaises(ValueError):
            self.check()

    def test_future_review(self):
        self.catalog["reviewed_on"] = "2026-11-26"
        with self.assertRaises(ValueError):
            self.check()
