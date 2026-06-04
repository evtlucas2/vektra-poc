# Research: Load OFX Transactions

**Branch**: `001-load-ofx-transactions` | **Date**: 2026-06-04

## Decision 1: OFX File Parsing

**Decision**: Use Python stdlib `xml.etree.ElementTree` after manually stripping the
plain-text SGML header.

**Rationale**: OFX files from Brazilian banks (and many others) consist of a plain-text
key:value header followed by an XML document. The XML portion begins at the first `<OFX>`
tag. Locating that tag and feeding the rest to `ElementTree` requires no external
dependencies and handles the files described in the spec reliably.

`ofxparse` (third-party) supports SGML-only OFX 1.x but adds a dependency for no gain
here since the spec explicitly states the file contains "a header and xml". Stdlib is
sufficient and aligns with Principle V (Simplicity First).

**Alternatives considered**:
- `ofxparse` — supports SGML OFX 1.x; not needed here; extra dependency.
- `lxml` — faster XML parser; overkill for files of this size.

**Implementation note**: Strip everything before the first occurrence of `<OFX` (or
`<ofx`), then parse with `ElementTree`. Wrap in a try/except to catch malformed XML
and log the error without crashing (FR-008).

---

## Decision 2: PostgreSQL Driver

**Decision**: `psycopg2-binary`

**Rationale**: The most widely used, well-documented PostgreSQL adapter for Python.
The `-binary` variant includes native C extensions pre-compiled, avoiding build toolchain
requirements on the deployment machine.

**Alternatives considered**:
- `psycopg3` (psycopg) — newer async-capable driver; async adds unnecessary complexity
  for a synchronous ETL pipeline (Principle V).
- SQLAlchemy — full ORM/core layer; adds abstractions not needed for a single-table
  insert pipeline (Principle V).

---

## Decision 3: Idempotency Strategy

**Decision**: Compute a SHA-256 hash of `(posted_date, amount, raw_memo, name)` and
store it as `transaction_hash TEXT UNIQUE`. Use `INSERT ... ON CONFLICT (transaction_hash)
DO NOTHING`.

**Rationale**: OFX files from the same bank account may be re-downloaded with overlapping
date ranges. A natural unique key does not exist in the OFX spec (no guaranteed unique
transaction ID in all OFX implementations). Hashing the deterministic fields produces
a stable idempotency key.

Hash input is constructed before MEMO transformation so that the same source row always
produces the same hash, regardless of how the MEMO splits.

**Alternatives considered**:
- Use `FITID` (financial institution transaction ID) as unique key — `FITID` is present
  in the OFX spec but not guaranteed to be unique across re-exports from all banks.
  Using it as a secondary check alongside the hash is a future enhancement.
- Upsert with update — unnecessary; re-loading the same row with identical values is
  a no-op; `DO NOTHING` is sufficient.

---

## Decision 4: MEMO Pattern Matching

**Decision**: Match MEMO against the regex `^(\d{1,2}/\d{1,2})\s+\d{1,2}:\d{2}\s+(.+)$`.

- Group 1 (`DD/MM`) combined with year from `DTPOSTED[:4]` → `effective_date` as
  `datetime.date(year, month, day)`.
- Group 2 → `description`.

**Rationale**: The pattern `DD/MM HH:MM description` is unambiguous. Using a compiled
regex as a named module constant is clean and testable in isolation.

If MEMO does not match: store full MEMO as `description`, set `effective_date = None`.

**DTPOSTED parsing**: OFX date format is `YYYYMMDD` or `YYYYMMDDHHMMSS[.nnn][+offset]`.
Extract year from the first 4 characters. Raise `ValueError` on malformed DTPOSTED and
skip the row (FR-008).

---

## Decision 5: Configuration Management

**Decision**: `python-dotenv` loads a `.env` file at startup; env vars override `.env`
values. Required variables: `DATABASE_URL` (PostgreSQL DSN), `DATA_ROOT` (base path
for data files).

**Rationale**: Consistent with Constitution Principle I. `.env.example` documents
required variables without exposing secrets. CI sets env vars directly without a `.env`
file.

**Alternatives considered**:
- `dynaconf` — feature-rich config library; too heavy for two config values.
- Argparse only — would require repeating the connection string on every CLI call;
  environment variables are the idiomatic approach for secrets.

---

## Decision 7: Directory Scanning

**Decision**: Use `pathlib.Path.glob("*.ofx")` (case-sensitive) combined with a
lowercase check to enumerate OFX files. Return a sorted list of `Path` objects so
processing order is deterministic across runs and operating systems.

**Rationale**: `pathlib` is stdlib, expressive, and returns `Path` objects that compose
cleanly with the rest of the pipeline. Sorting by filename gives predictable, reproducible
test output. An empty result from `glob` naturally maps to the empty-directory no-op
(FR-002).

For case-insensitive matching on Linux (where `glob` is case-sensitive), apply
`.lower().endswith(".ofx")` on each candidate returned by `Path.iterdir()`.

**Alternatives considered**:
- `os.scandir` — lower-level; works but less ergonomic than `pathlib`.
- `os.listdir` — older API; no `Path` integration; not used.

**Empty directory handling**: If the list is empty, `cli.py` logs
`[INFO] No OFX files found in <directory>. Nothing to do.` and exits with code 0.

---

## Decision 6: Transaction Filtering

**Decision**: Filter out transactions where `NAME` (case-sensitive) equals
`"Saldo do dia"` or `"Saldo Anterior"`. Store the excluded names as a `frozenset`
module-level constant in `transform.py`.

**Rationale**: Exact string match is deterministic and testable. Using a `frozenset`
makes membership checks O(1) and communicates that the set is immutable by design.
