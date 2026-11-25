"""Validate the defensive reference catalog before publication."""
import argparse
from datetime import date
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

PUBLISHERS = {
    "Debian": {"www.debian.org", "security-tracker.debian.org"},
    "Canonical": {"ubuntu.com", "documentation.ubuntu.com"},
    "CISA": {"www.cisa.gov"},
    "CERT-EU": {"www.cert.europa.eu", "cert.europa.eu"}
}
FIELDS = {"id", "publisher", "category", "scope", "url", "intended_use", "verification"}


def validate(data, today=None):
    catalog = json.loads(data)
    if not isinstance(catalog, dict) or set(catalog) != {"schema_version", "kind", "reviewed_on", "sources"}:
        raise ValueError("Invalid catalog root")
    if type(catalog["schema_version"]) is not int or catalog["schema_version"] != 1 or catalog["kind"] != "defensive-reference-catalog":
        raise ValueError("Unsupported reference catalog")
    reviewed = catalog["reviewed_on"]
    if not isinstance(reviewed, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", reviewed) or date.fromisoformat(reviewed) > (today or date.today()):
        raise ValueError("Invalid review date")
    sources = catalog["sources"]
    if not isinstance(sources, list) or not sources:
        raise ValueError("No reference sources")
    ids, urls = set(), set()
    for source in sources:
        if not isinstance(source, dict) or set(source) != FIELDS:
            raise ValueError("Unexpected reference fields")
        if not all(isinstance(value, str) and value.strip() for value in source.values()):
            raise ValueError("Invalid reference values")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", source["id"]):
            raise ValueError("Invalid reference identifier")
        parts = urlsplit(source["url"])
        if (parts.scheme != "https" or parts.hostname not in PUBLISHERS.get(source["publisher"], set())
                or parts.username or parts.password or parts.port not in (None, 443)
                or parts.query or parts.fragment):
            raise ValueError("Reference must be a stable official publisher URL")
        if source["category"] not in {"vendor-advisories", "mitigation-guidance", "threat-context"} or source["scope"] not in {"debian", "ubuntu", "general"}:
            raise ValueError("Unsupported reference category or scope")
        if source["verification"] not in {"direct", "official-reference"}:
            raise ValueError("Unsupported verification status")
        if source["id"] in ids or source["url"] in urls:
            raise ValueError("Duplicate catalog reference")
        ids.add(source["id"])
        urls.add(source["url"])
    return {"references": len(ids), "reviewed_on": reviewed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.file.read_bytes()), indent=2))
    except (OSError, TypeError, ValueError) as exc:
        parser.exit(1, f"Reference catalog invalid: {exc}\n")


if __name__ == "__main__":
    main()
