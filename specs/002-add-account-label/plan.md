# Implementation Plan: Add Account Label to Transactions

**Branch**: `002-add-account-label` | **Date**: 2026-06-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-add-account-label/spec.md`

## Summary

Extends the OFX ETL pipeline to tag every transaction with a user-supplied account label
provided as a CLI argument. The label is stored on each row, included in the SHA-256
idempotency hash, and managed through a new yoyo-migrations schema layer. A new
`ALTER TABLE` migration adds the `account_label` column to the existing `transactions`
table. The initial `CREATE TABLE` DDL is also migrated into the yoyo system, replacing
the previous `create_table_if_not_exists()` helper.

## Technical Context

**Language/Version**: Python 3.13 (system)

**Primary Dependencies**: `psycopg2-binary`, `python-dotenv`, `yoyo-migrations>=9.0`
(replaces ad-hoc DDL in `load.py`), `pytest`, `pytest-mock`

**Storage**: PostgreSQL — `transactions` table extended with `account_label` column

**Testing**: `pytest`, `pytest-mock`

**Target Platform**: Linux/macOS workstation or CI server

**Project Type**: ETL pipeline with CLI entry point

**Performance Goals**: Unchanged from feature 001 (≤10 s per 1,000-transaction file)

**Constraints**:
- `DATABASE_URL` and `DATA_ROOT` from env / `config/.env`
- Account label supplied as second positional CLI argument
- Label must be non-empty after trimming (validated at CLI entry)

**Scale/Scope**: Single account label per pipeline invocation; schema versioned via
yoyo-migrations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Data Decoupling | ✅ PASS | `DATABASE_URL`, `DATA_ROOT` from env; label from CLI arg; no hardcoded values |
| II. ETL Discipline | ✅ PASS | `account_label` is a transform-time parameter injected into `transform_transactions()`; schema management is separate (`src/db/migrations.py`) |
| III. Test-First | ✅ PASS | New/updated tests for label injection, hash change, empty-label rejection written before implementation |
| IV. Clean Code | ✅ PASS | `account_label` added to `Transaction` dataclass; hash helper updated; functions stay ≤25 lines |
| V. Simplicity First | ✅ PASS | yoyo replaces one ad-hoc DDL function — net reduction in custom schema code; no ORM added |

*Post-design re-check*: All gates hold after Phase 1.

## Project Structure

### Documentation (this feature)

```text
specs/002-add-account-label/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── cli-interface.md
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code Changes

```text
migrations/                          # NEW — yoyo-managed SQL migrations
├── 0001_create_transactions.sql     # Baseline schema (transactions table)
└── 0002_add_account_label.sql       # ADD COLUMN account_label

src/
├── db/                              # NEW package
│   ├── __init__.py
│   └── migrations.py                # apply_migrations(database_url) helper
├── etl/
│   ├── load.py                      # UPDATED: remove create_table_if_not_exists();
│   │                                #   include account_label in INSERT
│   └── transform.py                 # UPDATED: accept account_label param;
│                                    #   include in hash
├── models/
│   └── transaction.py               # UPDATED: add account_label: str field
└── cli.py                           # UPDATED: accept 2nd positional arg <label>;
                                     #   validate non-empty; call apply_migrations()

tests/
├── unit/
│   ├── test_transaction.py          # UPDATED: account_label field
│   ├── test_transform.py            # UPDATED: label injection + hash tests
│   └── test_load.py                 # UPDATED: account_label in INSERT
└── integration/
    └── test_pipeline.py             # UPDATED: label argument; two-account scenario

requirements.txt                     # UPDATED: add yoyo-migrations>=9.0
```

**Structure Decision**: New `src/db/` package isolates database-infrastructure concerns
(migrations) from ETL data-processing concerns (`src/etl/`), consistent with
Constitution Principle II. The `migrations/` directory at project root is the yoyo
standard layout.

## Complexity Tracking

> **No violations — no entries required.**
