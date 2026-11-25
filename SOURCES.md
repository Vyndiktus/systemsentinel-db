# Vendor maintenance sources

Use official vendor package update channels as the source of truth.

- Debian: [Debian Security Tracker](https://security-tracker.debian.org/tracker/) and [Debian security advisories](https://www.debian.org/security/).
- Ubuntu: [Ubuntu Security Notices](https://ubuntu.com/security/notices) and [Ubuntu security metadata documentation](https://documentation.ubuntu.com/security/security-updates/osv/).

The tracker may identify source packages rather than installed binary packages; these must not be treated as interchangeable. Record exact distro releases, binary package names, and vendor-confirmed fixed versions; exclude uncertain records, unsupported suites, and unsupported package sources. Do not infer affected status from a generic upstream version. If entitlement is required to receive a fix, point users to the vendor's instructions and do not imply the update is available to everyone.

## Review and validation

Any proposed snapshot must be reviewed against the vendor notice by a maintainer. Run:

```sh
python3 -m unittest discover -s tests -v
python3 tools/validate_snapshot.py path/to/snapshot.json
```

Validation checks structure and official reference domains; it does not certify advisory accuracy, completeness, licensing, or availability of any fix. Preserve the fictional fixture for offline tests. Publish only reviewed snapshots, with versioned releases and independently trusted checksums. Keep exploit code, proof-of-concept procedures, credentials and host inventories out of the database.
