"""Validate the vendor maintenance lifecycle dataset."""
import argparse
from datetime import date
import json
from pathlib import Path
import re

SOURCES = {
    "debian": "https://www.debian.org/releases/",
    "ubuntu": "https://ubuntu.com/about/release-cycle",
}
FIELDS = {"distribution", "release", "standard_until", "extended_until",
          "extended_program", "source", "guidance"}


def parse_boundary(value):
    if not re.fullmatch(r"\d{4}-\d{2}(?:-\d{2})?", value):
        raise ValueError("Unrecognized date precision")
    # Use the first day for ordering only, not as an exact support end date.
    return date.fromisoformat(value if len(value) == 10 else value + "-01")


def validate(data, today=None):
    dataset = json.loads(data)
    if not isinstance(dataset, dict) or set(dataset) != {"schema_version", "kind", "reviewed_on", "records"}:
        raise ValueError("Invalid lifecycle root fields")
    if type(dataset["schema_version"]) is not int or dataset["schema_version"] != 1 or dataset["kind"] != "vendor-maintenance-lifecycle":
        raise ValueError("Unsupported lifecycle format")
    reviewed = dataset["reviewed_on"]
    if not isinstance(reviewed, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", reviewed) or date.fromisoformat(reviewed) > (today or date.today()):
        raise ValueError("Invalid review date")
    records = dataset["records"]
    if not isinstance(records, list) or not records:
        raise ValueError("Lifecycle dataset must contain records")
    keys = set()
    for record in records:
        if not isinstance(record, dict) or set(record) != FIELDS:
            raise ValueError("Invalid lifecycle record fields")
        if not all(isinstance(value, str) and value.strip() for value in record.values()):
            raise ValueError("Invalid lifecycle record value")
        distro = record["distribution"]
        release = record["release"]
        if distro not in SOURCES or record["source"] != SOURCES[distro]:
            raise ValueError("Unrecognized vendor lifecycle source")
        if not re.fullmatch(r"\d+(?:\.\d+)?", release):
            raise ValueError("Invalid release identifier")
        key = (distro, release)
        if key in keys:
            raise ValueError("Duplicate lifecycle record")
        keys.add(key)
        standard, extended = record["standard_until"], record["extended_until"]
        if len(standard) != len(extended) or parse_boundary(standard) >= parse_boundary(extended):
            raise ValueError("Invalid support date ordering or precision")
    return {"records": len(keys), "reviewed_on": reviewed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.file.read_bytes()), indent=2))
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(1, f"Lifecycle dataset invalid: {exc}\n")


if __name__ == "__main__":
    main()
