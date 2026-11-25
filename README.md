# SystemSentinel Database

Versioned snapshots of vendor security maintenance information, for local read-only scans.

The only included data is fictional and **not suitable for operational scanning**. The scanner refuses synthetic snapshots unless explicitly enabled.

## Format

See [snapshot-v1.json](schema/snapshot-v1.json). Each record identifies an exact distribution, release, binary package name, vendor fixed version, advisory reference and official reference URL. Versions must be taken from the named distribution; generic upstream versions are not interchangeable.

A SHA-256 digest can accompany the snapshot for corruption detection; the digest must come from a separately trusted source to authenticate a release. The scanner validates the supplied digest and reports snapshot age. No live feed importer or signed publishing pipeline is included yet.

A snapshot only covers records it contains; no matches do not establish that the host is secure.

License: MIT (schema and tooling; vendor feed licensing must be reviewed before redistribution).

For governing sources and submission requirements, see [SOURCES.md](SOURCES.md). The validation workflow checks snapshot structure, duplicate keys, versions, and vendor reference domains before review.
