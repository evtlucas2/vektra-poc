# Implementation Plan: Load OFX Transactions

**Branch**: `001-load-ofx-transactions` | **Date**: 2026-06-04 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-load-ofx-transactions/spec.md`

## Summary

ETL pipeline that scans a directory for OFX files (zero or more), processes each file
sequentially, and loads clean Transaction records into a PostgreSQL table. Per file: the
plain-text header is skipped, the XML body is parsed, balance-summary rows ("Saldo do
dia", "Saldo Anterior") are filtered out, and the MEMO field is split when it matches the
`DD/MM HH:MM description` pattern. An empty directory is a valid no-op. Idempotency is
guaranteed via a SHA-256 content hash. Implemented in Python using stdlib XML parsing and
psycopg2.

## Technical Context

**Language/Version**: Python 3.13 (system); minimum requirement Python 3.11+

**Primary Dependencies**: `psycopg2-binary` (PostgreSQL driver), `python-dotenv`
(environment variable loading from `.env` files)

**Storage**: PostgreSQL — single table `transactions`

**Testing**: `pytest`, `pytest-mock`

**Target Platform**: Linux/macOS workstation or CI server

**Project Type**: ETL pipeline with a CLI entry point

**Performance Goals**: ≤10 seconds for 1,000 transactions (SC-005 in spec)

**Constraints**:
- OFX directory path supplied externally (env var `DATA_ROOT` + relative argument or full path)
- Database connection string from `DATABASE_URL` env var
- No hardcoded data paths in source code (Constitution Principle I)

**Scale/Scope**: One directory per invocation; ~hundreds to low thousands of transactions
per file; sequential per-file processing

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Data Decoupling | ✅ PASS | OFX directory path resolved from `DATA_ROOT`; `DATABASE_URL` from env. No hardcoded paths. |
| II. ETL Discipline | ✅ PASS | Three separate modules: `extract.py`, `transform.py`, `load.py`. Transform is pure. |
| III. Test-First | ✅ PASS | Unit tests for all three ETL phases written before implementation. Integration test covers full pipeline. |
| IV. Clean Code | ✅ PASS | Named constants for filtered names and regex; functions ≤25 lines enforced in design. |
| V. Simplicity First | ✅ PASS | No ORM — direct psycopg2. Stdlib XML. Flat module structure. No abstraction layers beyond what the spec requires. |

*Post-design re-check*: All gates hold after Phase 1 design — no new violations introduced.

## Project Structure

### Documentation (this feature)

```text
specs/001-load-ofx-transactions/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── cli-interface.md
│   └── database-schema.md
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
src/
├── etl/
│   ├── __init__.py
│   ├── scan.py           # Scan directory for .ofx files → list[Path]
│   ├── extract.py        # Parse OFX file header → skip; XML body → list[dict]
│   ├── transform.py      # Filter + normalize raw dicts → list[Transaction]
│   └── load.py           # Upsert Transaction records into PostgreSQL
├── models/
│   ├── __init__.py
│   └── transaction.py    # Transaction dataclass
└── cli.py                # CLI entry point (reads env vars, wires ETL phases)

tests/
├── unit/
│   ├── test_scan.py
│   ├── test_extract.py
│   ├── test_transform.py
│   └── test_load.py
└── integration/
    └── test_pipeline.py  # End-to-end: directory on disk → PostgreSQL assertions

config/
└── .env.example          # Documents DATA_ROOT, DATABASE_URL

tests/fixtures/
├── empty_dir/            # Fixture directory with no OFX files
├── single/
│   └── sample.ofx        # Minimal OFX fixture — one file
└── multi/
    ├── january.ofx       # Fixture — first file
    └── february.ofx      # Fixture — second file
```

**Structure Decision**: Single-project layout under `src/`. A new `scan.py` module handles
directory enumeration as a separate, independently testable ETL concern (Constitution
Principle II). ETL now has four phases: Scan → Extract → Transform → Load. No web layer,
no frontend. The `<data_root>` directory for production data lives outside the project
tree, accessed via `DATA_ROOT` env var.
