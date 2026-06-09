---
description: "Task list for Calculate Daily Balance feature"
---

# Tasks: Calculate Daily Balance

**Input**: Design documents from `specs/004-daily-balance/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/ ✅

**TDD Note**: Tests are **mandatory** (Constitution Principle III). Every implementation
task has a corresponding test written and confirmed failing (Red) before implementation.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no shared state dependencies)
- **[Story]**: Maps to user story from spec.md (US1)

---

## Phase 1: Setup

**Purpose**: Scaffold the new `src/balance/` package.

- [X] T001 [P] Create package marker `src/balance/__init__.py`
- [X] T002 [P] Create `migrations/0004_create_daily_balance.sql` — `CREATE TABLE IF NOT EXISTS daily_balance (balance_date DATE PRIMARY KEY, day_of_week SMALLINT NOT NULL, weekend SMALLINT NOT NULL, balance NUMERIC(15,2) NOT NULL, difference NUMERIC(15,2) NOT NULL)`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: `DailyBalance` model and migration verification — required by all later phases.

**⚠️ CRITICAL**: User story work cannot begin until this phase is complete.

- [X] T003 [P] Write failing unit tests for the `DailyBalance` dataclass (fields: balance_date, day_of_week, weekend, balance, difference) in `tests/unit/test_daily_balance_model.py` ⚠️ Confirm FAIL before T004
- [X] T004 Create `DailyBalance` dataclass in `src/models/daily_balance.py` (depends T003)
- [X] T005 [P] Write failing unit test asserting `migrations/0004_create_daily_balance.sql` exists and contains `daily_balance`, `balance_date`, `difference` in `tests/unit/test_migrations.py` ⚠️ Confirm FAIL before completing (passes once T002 done)

**Checkpoint**: Model and migration ready — US1 can begin.

---

## Phase 3: User Story 1 — Generate Daily Balance Series (Priority: P1) 🎯 MVP

**Goal**: New command `python -m src.balance <initial-balance>` reads transactions,
computes the gap-filled daily series (balance, difference, day_of_week, weekend), and
writes it to `daily_balance`.

**Independent Test**: `pytest tests/unit/test_balance_compute.py` plus integration
`test_balance_pipeline.py::test_generate_series` — verify one row per calendar day, correct
balance/difference recomputation, day_of_week (0=Mon…6=Sun) and weekend (1 for 5/6).

### Tests for User Story 1 ⚠️ Write FIRST — confirm all FAIL before implementation

- [X] T006 [P] [US1] Write failing unit tests for `compute_daily_balances(daily_net, initial_balance)` in `tests/unit/test_balance_compute.py`: first-day balance = initial + net and difference = 0; subsequent balance = prev + net and difference = balance − prev; gap-filled day has balance = prev and difference = 0; `day_of_week` = Python weekday (0=Mon…6=Sun); `weekend` = 1 for days 5/6; negative-net day → negative difference; empty input → empty list
- [X] T007 [P] [US1] Write failing unit tests for `fetch_daily_net(conn)` in `tests/unit/test_balance_extract.py`: returns `dict[date, Decimal]` from a mocked grouped query; empty result → empty dict
- [X] T008 [P] [US1] Write failing unit tests for `replace_daily_balances(conn, rows)` in `tests/unit/test_balance_load.py`: issues `DELETE FROM daily_balance` then one INSERT per row, commits once; empty rows → DELETE only
- [X] T009 [P] [US1] Write failing integration test `test_generate_series` in `tests/integration/test_balance_pipeline.py`: seed transactions across a date range with a gap, run pipeline with known initial balance, assert row-per-day count, balance/difference correctness, and first-day difference = 0 (skips without `DATABASE_URL`)

### Implementation for User Story 1 (after T006–T009 confirmed failing)

- [X] T010 [P] [US1] Implement `fetch_daily_net(conn) -> dict[date, Decimal]` in `src/balance/extract.py` using `SELECT effective_date, SUM(amount) FROM transactions GROUP BY effective_date` (depends T007)
- [X] T011 [P] [US1] Implement pure `compute_daily_balances(daily_net, initial_balance) -> list[DailyBalance]` in `src/balance/compute.py` with `WEEKEND_DAYS = frozenset({5, 6})`; gap-fill from min to max date; first-day difference = 0; subsequent difference = balance − prev (depends T006, T004)
- [X] T012 [P] [US1] Implement `replace_daily_balances(conn, rows)` in `src/balance/load.py` — `DELETE FROM daily_balance` then INSERT each row, commit once (depends T008)
- [X] T013 [US1] Implement `src/balance/__main__.py` CLI: load `config/.env`, validate `<initial-balance>` as Decimal (error+exit 1 if missing/invalid), `apply_migrations()`, `fetch_daily_net`; if empty print `[INFO] No transactions found. Nothing to do.` exit 0; else compute, `replace_daily_balances`, print summary (depends T010, T011, T012)
- [X] T014 [US1] Run integration test `test_generate_series` and confirm it passes; verify stdout summary matches `contracts/cli-interface.md` (depends T009, T013)

**Checkpoint**: US1 complete — daily balance series generated and persisted.

---

## Phase 4: Polish & Cross-Cutting Concerns

- [X] T015 [P] Add an integration test `test_idempotent_rerun` in `tests/integration/test_balance_pipeline.py`: run twice, assert identical row count (table fully replaced)
- [X] T016 [P] Add a CLI validation unit test for missing/invalid initial balance (exit code 1) in `tests/unit/test_balance_compute.py` or a new `tests/unit/test_balance_cli.py`
- [X] T017 Validate all functions ≤25 lines across `src/balance/*.py` and `src/models/daily_balance.py` (Constitution Principle IV); refactor if needed
- [X] T018 Run full unit suite and confirm all tests pass: `pytest tests/unit/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001, T002 — no dependencies, parallel
- **Foundational (Phase 2)**: T003→T004 (model); T005 verifies T002 — blocks US1
- **US1 (Phase 3)**: depends on Foundational (T004) — MVP
- **Polish (Phase 4)**: depends on US1

### Within US1

- Tests T006–T009 all parallel (different files) — all Red before implementation
- T010, T011, T012 parallel (different files); T011 depends on T004 (model)
- T013 depends on T010+T011+T012; T014 depends on T013

### Parallel Opportunities

```bash
# Phase 1 — both parallel:
Task: T001 — src/balance/__init__.py
Task: T002 — migrations/0004_create_daily_balance.sql

# US1 tests — all parallel (Red):
Task: T006 — tests/unit/test_balance_compute.py
Task: T007 — tests/unit/test_balance_extract.py
Task: T008 — tests/unit/test_balance_load.py
Task: T009 — tests/integration/test_balance_pipeline.py

# US1 implementation — extract/compute/load parallel:
Task: T010 — src/balance/extract.py
Task: T011 — src/balance/compute.py
Task: T012 — src/balance/load.py
# then:
Task: T013 — src/balance/__main__.py
```

---

## Implementation Strategy

### MVP (US1)

1. Phase 1 Setup → Phase 2 Foundational → Phase 3 US1
2. Run `pytest tests/unit/` — all pass
3. Validate with `python -m src.balance 1000.00` against a loaded database

### Incremental Delivery

1. Setup + Foundational → table + model ready
2. US1 → working balance command (MVP)
3. Polish → idempotency test, CLI validation test, line-length check, full run

---

## Notes

- The compute phase is pure (no I/O) — the easiest and most valuable unit-test target
- `day_of_week` uses Python `date.weekday()` directly (0=Mon…6=Sun); no remapping
- `difference` = balance − previous balance; first day always 0
- Integration tests auto-skip without `DATABASE_URL`
- The existing OFX loader (`python -m src.cli`) is untouched by this feature
- Reuses `src/db/migrations.py::apply_migrations` — no new dependencies
