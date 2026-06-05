# Implementation Plan: Fix Effective Date — Always Non-Null

**Branch**: `003-fix-effective-date-default` | **Date**: 2026-06-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/003-fix-effective-date-default/spec.md`

## Summary

Small focused fix: when the MEMO tag does not match the `DD/MM HH:MM` pattern (or is
blank/absent), `effective_date` now defaults to `posted_date` instead of `None`. The
`Transaction` dataclass changes `effective_date` from `date | None` to `date`. A new
yoyo migration (`0003`) backfills existing null rows with `posted_date` then enforces
the `NOT NULL` constraint on the column.

## Technical Context

**Language/Version**: Python 3.13 (system)

**Primary Dependencies**: Unchanged — `psycopg2-binary`, `python-dotenv`,
`yoyo-migrations>=9.0`, `pytest`, `pytest-mock`

**Storage**: PostgreSQL — `effective_date` column: `DATE NULL` → `DATE NOT NULL`

**Testing**: `pytest`, `pytest-mock`

**Target Platform**: Linux/macOS workstation or CI server

**Project Type**: ETL pipeline fix (no CLI interface change)

**Performance Goals**: Unchanged

**Constraints**: Migration must backfill before adding NOT NULL — two-statement migration
needed to be safe on tables with existing null rows

**Scale/Scope**: Single-column nullability change; transform logic tweak; no new fields

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Data Decoupling | ✅ PASS | No path or connection-string changes; migration applied via existing `apply_migrations()` |
| II. ETL Discipline | ✅ PASS | Change isolated to `_transform_row()` in `transform.py`; pure function; no I/O introduced |
| III. Test-First | ✅ PASS | Tests for fallback behavior and type change written before implementation |
| IV. Clean Code | ✅ PASS | One-line change in `_transform_row()`; `effective_date` type simplified to `date` |
| V. Simplicity First | ✅ PASS | Minimal change — no new abstractions; migration does exactly two SQL statements |

*Post-design re-check*: All gates hold.

## Project Structure

### Documentation (this feature)

```text
specs/003-fix-effective-date-default/
├── plan.md          # This file
├── research.md      # Phase 0 output
├── data-model.md    # Phase 1 output
├── quickstart.md    # Phase 1 output
└── tasks.md         # Phase 2 output (/speckit-tasks)
```

No new contracts — CLI interface is unchanged.

### Source Code Changes

```text
migrations/
└── 0003_effective_date_not_null.sql   # NEW — backfill + NOT NULL constraint

src/
├── models/
│   └── transaction.py                 # UPDATED: effective_date: date (not date | None)
└── etl/
    └── transform.py                   # UPDATED: _transform_row() returns posted_date
                                       #   when MEMO pattern absent/invalid

tests/
└── unit/
    ├── test_transaction.py            # UPDATED: effective_date is always date
    └── test_transform.py              # UPDATED: fallback tests; remove None assertions
```
