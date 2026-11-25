"""Validate a maintenance snapshot before a repository review."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit

FIELDS = {"distribution", "release", "package", "fixed_version", "advisory", "reference"}
ROOT_KEYS = {"schema_version", "generated_at", "synthetic", "records"}
VENDOR_HOSTS = {"debian": {"security-tracker.debian.org", "www.debian.org"},
                "ubuntu": {"ubuntu.com", "documentation.ubuntu.com"}}


def validate(data, now=None):
    snapshot = json.loads(data)
    if not isinstance(snapshot, dict) or set(snapshot) != ROOT_KEYS:
        raise ValueError("Unexpected snapshot fields")
    if type(snapshot["schema_version"]) is not int or snapshot["schema_version"] != 1:
        raise ValueError("Unsupported schema")
    if type(snapshot["synthetic"]) is not bool or not isinstance(snapshot["records"], list):
        raise ValueError("Invalid snapshot metadata")
    if not isinstance(snapshot["generated_at"], str):
        raise ValueError("Invalid timestamp")
    generated = datetime.fromisoformat(snapshot["generated_at"].replace("Z", "+00:00"))
    if generated.tzinfo is None or generated > (now or datetime.now(timezone.utc)):
        raise ValueError("Timestamp must be timezone-aware and not in the future")
    seen = set()
    for record in snapshot["records"]:
        if not isinstance(record, dict) or set(record) != FIELDS:
            raise ValueError("Unexpected record fields")
        if not all(isinstance(value, str) and value.strip() for value in record.values()):
            raise ValueError("Invalid record value")
        distro = record["distribution"]
        if distro not in VENDOR_HOSTS:
            raise ValueError("Unsupported distribution")
        if not re.fullmatch(r"[a-z0-9][a-z0-9+.-]+", record["package"]):
            raise ValueError("Invalid binary package name")
        reference = urlsplit(record["reference"])
        if reference.scheme != "https" or not reference.hostname or reference.username or reference.password:
            raise ValueError("Reference must be an HTTPS URL without credentials")
        if not snapshot["synthetic"] and reference.hostname not in VENDOR_HOSTS[distro]:
            raise ValueError("Real records require an official vendor reference")
        result = subprocess.run(["dpkg", "--validate-version", record["fixed_version"]],
                                capture_output=True, timeout=5)
        if result.returncode:
            raise ValueError("Invalid vendor package version")
        identity = (distro, record["release"], record["package"], record["advisory"])
        if identity in seen:
            raise ValueError("Duplicate advisory/package record")
        seen.add(identity)
    return {"records": len(seen), "synthetic": snapshot["synthetic"],
            "sha256": hashlib.sha256(data).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.snapshot.read_bytes()), indent=2))
    except (OSError, ValueError, TypeError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"Snapshot invalid: {exc}\n")


if __name__ == "__main__":
    main()
