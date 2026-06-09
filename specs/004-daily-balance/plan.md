# Implementation Plan: Calculate Daily Balance

**Branch**: `004-daily-balance` | **Date**: 2026-06-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/004-daily-balance/spec.md`

## Summary

A new CLI command computes a running daily balance from the `transactions` table and
persists it to a new `daily_balance` table. The command takes an initial balance as its
only argument. It aggregates transaction amounts by `effective_date` across all accounts,
gap-fills every calendar day between the first and last transaction date, and records for
each day: the running balance, the day-of-week (Python `weekday()` — 0=Mon…6=Sun), a
weekend flag (1 for Sat/Sun), and the difference from the previous day's balance (0 on the
first day). Implemented as a separate ETL pipeline (`src/balance/`) invoked via
`python -m src.balance <initial-balance>`, reusing yoyo-migrations for the new table.

## Technical Context

**Language/Version**: Python 3.13 (system)

**Primary Dependencies**: Unchanged — `psycopg2-binary`, `python-dotenv`,
`yoyo-migrations>=9.0`, `pytest`, `pytest-mock`. No new dependencies.

**Storage**: PostgreSQL — new `daily_balance` table (separate from `transactions`)

**Testing**: `pytest`, `pytest-mock`

**Project Type**: ETL pipeline with a second CLI entry point

**Performance Goals**: Process a multi-year date range (single-digit thousands of days) in
well under 5 seconds

**Constraints**:
- `DATABASE_URL` and `DATA_ROOT` from env / `config/.env`
- Initial balance supplied as the single positional CLI argument; must be a valid decimal
- Reads `transactions` read-only; never modifies it

**Scale/Scope**: One global series per run; one row per calendar day in the transaction
date range

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Data Decoupling | ✅ PASS | `DATABASE_URL` from env; initial balance from CLI; no hardcoded paths |
| II. ETL Discipline | ✅ PASS | New `src/balance/` package with separate extract / compute / load; `compute_daily_balances()` is a pure function (no I/O) |
| III. Test-First | ✅ PASS | Pure compute function and CLI validation are unit-tested first; extract/load mocked; integration test for full series |
| IV. Clean Code | ✅ PASS | Functions ≤25 lines; `WEEKEND_DAYS = frozenset({5, 6})` as named constant; `DailyBalance` dataclass |
| V. Simplicity First | ✅ PASS | No new dependencies; reuses yoyo + psycopg2; flat module layout; DELETE+INSERT for idempotency rather than an upsert-diff scheme |

*Post-design re-check*: All gates hold after Phase 1.

## Project Structure

### Documentation (this feature)

```text
specs/004-daily-balance/
├── plan.md          # This file
├── research.md      # Phase 0 output
├── data-model.md    # Phase 1 output
├── quickstart.md    # Phase 1 output
├── contracts/       # Phase 1 output
│   ├── cli-interface.md
│   └── database-schema.md
└── tasks.md         # Phase 2 output (/speckit-tasks)
```

### Source Code Changes

```text
migrations/
└── 0004_create_daily_balance.sql   # NEW — CREATE TABLE daily_balance

src/
├── balance/                        # NEW package — daily-balance ETL pipeline
│   ├── __init__.py
│   ├── extract.py                  # fetch_daily_net(conn) -> dict[date, Decimal]
│   ├── compute.py                  # compute_daily_balances(daily_net, initial) -> list[DailyBalance] (PURE)
│   ├── load.py                     # replace_daily_balances(conn, rows)  (DELETE + INSERT)
│   └── __main__.py                 # CLI entry: python -m src.balance <initial-balance>
└── models/
    └── daily_balance.py            # NEW — DailyBalance dataclass

tests/
├── unit/
│   ├── test_balance_compute.py     # NEW — pure series logic (gap-fill, difference, weekday, weekend)
│   ├── test_balance_extract.py     # NEW — aggregation query (mocked cursor)
│   ├── test_balance_load.py        # NEW — DELETE+INSERT behavior (mocked cursor)
│   └── test_daily_balance_model.py # NEW — dataclass fields
└── integration/
    └── test_balance_pipeline.py    # NEW — end-to-end against PostgreSQL (skips without DATABASE_URL)
```

**Structure Decision**: The daily-balance calculation is a distinct pipeline from the OFX
loader, so it gets its own `src/balance/` package with its own three ETL phases (extract →
compute → load) per Constitution Principle II. The new command is invoked as
`python -m src.balance <initial-balance>` via a package `__main__.py`, mirroring but
independent of the existing `python -m src.cli` loader. The existing loader is unchanged.

## Complexity Tracking

> **No violations — no entries required.**
