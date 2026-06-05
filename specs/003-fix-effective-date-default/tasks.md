---
description: "Task list for Fix Effective Date — Always Non-Null"
---

# Tasks: Fix Effective Date — Always Non-Null

**TDD Note**: Tests mandatory per Constitution Principle III.

## Phase 1: Setup

- [X] T001 Create `migrations/0003_effective_date_not_null.sql` — UPDATE nulls to posted_date then ALTER COLUMN SET NOT NULL

## Phase 2: Foundational Tests (Red)

- [X] T002 [P] Write failing unit tests for `effective_date` always being a `date` (not None) in `tests/unit/test_transaction.py`
- [X] T003 [P] Write failing unit tests asserting fallback to `posted_date` in `tests/unit/test_transform.py`

## Phase 3: Implementation

- [X] T004 Update `Transaction.effective_date` type from `date | None` to `date` in `src/models/transaction.py` (depends T002)
- [X] T005 Update `_transform_row()` in `src/etl/transform.py`: when MEMO pattern absent/invalid set `effective_date = posted_date`; wrap `_parse_effective_date()` in try/except for invalid dates (depends T003, T004)

## Phase 4: Polish

- [X] T006 Run full unit test suite and confirm all 25+ tests pass: `pytest tests/unit/`
- [X] T007 Validate all functions ≤25 lines in `src/etl/transform.py`
- [X] T008 Update `specs/001-load-ofx-transactions/contracts/database-schema.md` to mark `effective_date` as NOT NULL
