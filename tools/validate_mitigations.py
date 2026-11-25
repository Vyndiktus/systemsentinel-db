"""Validate the catalog of defensive threat categories and mitigations."""
import argparse
from datetime import date
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

FIELDS = {"id", "category", "assessment", "mitigation", "source"}
HOSTS = {"csrc.nist.gov", "www.cisa.gov", "documentation.ubuntu.com", "www.debian.org"}
ASSESSMENTS = {"local_update_review", "local_index_review", "local_lifecycle_review", "manual_review"}


def validate(data, today=None):
    catalog = json.loads(data)
    if not isinstance(catalog, dict) or set(catalog) != {"schema_version", "kind", "reviewed_on", "records"}:
        raise ValueError("Unexpected catalog fields")
    if type(catalog["schema_version"]) is not int or catalog["schema_version"] != 1 or catalog["kind"] != "defensive-threat-mitigations":
        raise ValueError("Unsupported mitigation catalog")
    reviewed = catalog["reviewed_on"]
    if not isinstance(reviewed, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", reviewed) or date.fromisoformat(reviewed) > (today or date.today()):
        raise ValueError("Invalid review date")
    records = catalog["records"]
    if not isinstance(records, list) or not records:
        raise ValueError("No mitigation records")
    ids = set()
    for record in records:
        if not isinstance(record, dict) or set(record) != FIELDS:
            raise ValueError("Unexpected mitigation fields")
        if not all(isinstance(value, str) and value.strip() for value in record.values()):
            raise ValueError("Invalid mitigation value")
        key = record["id"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", key) or key in ids:
            raise ValueError("Invalid or duplicate mitigation ID")
        ids.add(key)
        if record["assessment"] not in ASSESSMENTS:
            raise ValueError("Unsupported assessment type")
        url = urlsplit(record["source"])
        if (url.scheme != "https" or url.hostname not in HOSTS or url.username or url.password
                or url.port not in (None, 443) or url.query or url.fragment):
            raise ValueError("Source must be an official HTTPS reference")
    return {"records": len(ids), "reviewed_on": reviewed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.file.read_bytes()), indent=2))
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(1, f"Invalid catalog: {exc}\n")


if __name__ == "__main__":
    main()
