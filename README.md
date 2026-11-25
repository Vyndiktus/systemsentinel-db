# SystemSentinel Database

Versioned snapshots of vendor security maintenance information, for local read-only scans.

The only included data is fictional and **not suitable for operational scanning**. The scanner refuses synthetic snapshots unless explicitly enabled.

## Format

See [snapshot-v1.json](schema/snapshot-v1.json). Each record identifies an exact distribution, release, binary package name, vendor fixed version, advisory reference and official reference URL. Versions must be taken from the named distribution; generic upstream versions are not interchangeable.

A SHA-256 digest can accompany the snapshot for corruption detection; the digest must come from a separately trusted source to authenticate a release. The scanner validates the supplied digest and reports snapshot age. No live feed importer or signed publishing pipeline is included yet.

A snapshot only covers records it contains; no matches do not establish that the host is secure.

License: MIT (schema and tooling; vendor feed licensing must be reviewed before redistribution).

For governing sources and submission requirements, see [SOURCES.md](SOURCES.md). The validation workflow checks snapshot structure, duplicate keys, versions, and vendor reference domains before review.

## Distribution preview

The development-preview release contains `snapshot.json` (fictional test data) and a separate SHA-256 checksum. The application accepts a named GitHub release and a trusted digest for explicit local import. It does not download or run scripts from the database.

## Real maintenance lifecycle data

The [vendor maintenance lifecycle dataset](maintenance/lifecycle-v1.json) is a separate, real-data catalog of seven Debian and Ubuntu releases, with standard and extended maintenance boundaries and official references. Its purpose is to guide upgrade planning, not determine whether individual packages are vulnerable. Date precision follows the source (month or day); coverage may vary with architecture, package and subscription. The catalog is manually reviewed and dated, not an exhaustive real-time feed.

Validate it with:

```sh
python3 tools/validate_lifecycle.py maintenance/lifecycle-v1.json
```

The existing advisory snapshot remains fictional. Lifecycle data must not be imported as an advisory snapshot.

## Defensive threat and mitigation references

The [defensive reference catalog](guidance/sources-v1.json) is a reviewed directory of official vendor advisories, general threat context and mitigation resources. It stores source-level links and intended defensive uses; it does not mirror exploit inventories or assert exploitation status for individual packages. The `official-reference` verification state means an official publisher document confirms the URL, but direct access could not be verified during this review.

```sh
python3 tools/validate_guidance.py guidance/sources-v1.json
```
