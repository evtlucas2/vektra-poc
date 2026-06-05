---

description: "Task list for Add Account Label to Transactions feature"
---

# Tasks: Add Account Label to Transactions

**Input**: Design documents from `specs/002-add-account-label/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/ ✅

**TDD Note**: Tests are **mandatory** (Constitution Principle III). Every implementation
task has a corresponding test written and confirmed failing (Red) before implementation.

**Scope**: This feature modifies existing modules from feature 001. Tasks marked
**UPDATED** touch files already in the codebase.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no shared state dependencies)
- **[Story]**: Maps to user story from spec.md (US1, US2)

---

## Phase 1: Setup

**Purpose**: Add yoyo-migrations dependency and scaffold new directories.

- [X] T001 Add `yoyo-migrations>=9.0` to `requirements.txt` and run `pip install -r requirements.txt`
- [X] T002 Create `migrations/` directory at project root
- [X] T003 [P] Create empty package marker `src/db/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Migration files, migration runner, and updated `Transaction` model + `load.py`
— all user story phases depend on these.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 [P] Create `migrations/0001_create_transactions.sql` — baseline `CREATE TABLE IF NOT EXISTS transactions (...)` DDL matching the existing schema (id, posted_date, effective_date, description, amount, transaction_hash with UNIQUE constraint)
- [X] T005 [P] Create `migrations/0002_add_account_label.sql` — `ALTER TABLE transactions ADD COLUMN IF NOT EXISTS account_label TEXT NOT NULL DEFAULT 'unknown'`
- [X] T006 [P] Write failing unit tests asserting migration files exist and contain expected SQL keywords in `tests/unit/test_migrations.py` ⚠️ Confirm tests FAIL before T007
- [X] T007 Implement `apply_migrations(database_url: str) -> None` using `yoyo.get_backend` and `yoyo.read_migrations` in `src/db/migrations.py`; resolve `migrations/` path relative to project root (depends T004, T005, T006)
- [X] T008 [P] Write failing unit tests for updated `Transaction` dataclass with new `account_label: str` field in `tests/unit/test_transaction.py` ⚠️ Confirm tests FAIL before T009
- [X] T009 Add `account_label: str` field to `Transaction` dataclass in `src/models/transaction.py` (depends T008)
- [X] T010 [P] Write failing unit tests for updated `insert_transactions()` that includes `account_label` in the INSERT statement in `tests/unit/test_load.py` ⚠️ Confirm tests FAIL before T011
- [X] T011 Remove `create_table_if_not_exists()` from `src/etl/load.py`; update `_INSERT_SQL` and `insert_transactions()` to include `account_label` column and value (depends T009, T010)

**Checkpoint**: Foundation complete — migrations defined, `Transaction` model updated,
`load.py` updated. User story phases can begin.

---

## Phase 3: User Story 1 — Load Transactions Tagged with Account Label (Priority: P1) 🎯 MVP

**Goal**: Pipeline accepts `<account-label>` as second positional CLI argument, injects it
into every transaction, and includes it in the idempotency hash.

**Independent Test**: Run pipeline twice with same directory but different labels; confirm
both sets of rows exist in the database with correct `account_label` values.

### Tests for User Story 1 ⚠️ Write FIRST — confirm all FAIL before implementation

- [X] T012 [P] [US1] Write failing unit tests for `transform_transactions(raw, account_label)` updated signature: label stored on `Transaction`, label included in hash in `tests/unit/test_transform.py`
- [X] T013 [P] [US1] Write failing integration test `test_two_account_labels`: same directory loaded under two labels → both label rows present, counts match in `tests/integration/test_pipeline.py`

### Implementation for User Story 1

- [X] T014 [US1] Update `transform_transactions(raw: list[dict], account_label: str)` in `src/etl/transform.py`: add `account_label` param; set `transaction.account_label = account_label`; append `|{account_label}` to hash input string `_compute_hash()` (depends T012, T009)
- [X] T015 [US1] Update `src/cli.py`: accept second positional arg `<account-label>`; strip whitespace; exit 1 with `[ERROR] Account label must not be empty.` if blank; call `apply_migrations(DATABASE_URL)` at startup; pass `account_label` to `transform_transactions()` in `_process_files()` (depends T007, T014)
- [X] T016 [US1] Run integration test `test_two_account_labels` and confirm it passes (depends T013, T015)

**Checkpoint**: US1 complete — every transaction row is tagged with the user-supplied
account label; two-account scenario works correctly.

---

## Phase 4: User Story 2 — Idempotent Reload with Account Label (Priority: P2)

**Goal**: Re-running the pipeline with the same directory and same account label inserts
zero duplicate rows. The updated hash (which includes `account_label`) ensures
idempotency is preserved per-label.

**Independent Test**: Run pipeline twice with same directory and same label; confirm row
count is identical after both runs.

### Tests for User Story 2 ⚠️ Write FIRST — confirm FAIL before implementation

- [X] T017 [P] [US2] Write failing integration test `test_idempotent_reload_with_label`: load same directory + label twice; assert second run inserts 0 rows in `tests/integration/test_pipeline.py`

### Implementation for User Story 2

- [X] T018 [US2] Verify `test_idempotent_reload_with_label` passes — `ON CONFLICT (transaction_hash) DO NOTHING` in `load.py` handles this once hash includes `account_label`; if it fails, review `_compute_hash()` in `src/etl/transform.py` (depends T017, T014)

**Checkpoint**: US2 complete — idempotency preserved with labelled transactions.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [X] T019 [P] Validate all functions are ≤25 lines in `src/etl/transform.py`, `src/cli.py`, `src/db/migrations.py` (Constitution Principle IV); refactor if needed
- [X] T020 [P] Update `specs/001-load-ofx-transactions/contracts/database-schema.md` to document the new `account_label` column added by migration `0002`
- [X] T021 Run full unit test suite and confirm all tests pass: `pytest tests/unit/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — **blocks all user stories**
- **US1 (Phase 3)**: Depends on Foundational (T009, T011)
- **US2 (Phase 4)**: Depends on US1 transform update (T014)
- **Polish (Phase 5)**: Depends on all user story phases

### Within Phase 2

- T004, T005, T006, T008, T010: all parallel (different files)
- T007 depends on T004, T005, T006
- T009 depends on T008
- T011 depends on T009, T010

### Within US1

- T012, T013: parallel (different test files) — both Red before any implementation
- T014 depends on T012, T009
- T015 depends on T007, T014
- T016 depends on T013, T015

### Parallel Opportunities

```bash
# Phase 2 — launch all test-writing tasks together (Red):
Task: T006 — tests/unit/test_migrations.py
Task: T008 — tests/unit/test_transaction.py
Task: T010 — tests/unit/test_load.py

# Phase 2 — after confirming Red, implement in dependency order:
Task: T007 — src/db/migrations.py      (after T004, T005, T006)
Task: T009 — src/models/transaction.py (after T008)
Task: T011 — src/etl/load.py           (after T009, T010)

# US1 — test tasks parallel:
Task: T012 — tests/unit/test_transform.py
Task: T013 — tests/integration/test_pipeline.py
```

---

## Implementation Strategy

### MVP (US1 Only)

1. Complete Phase 1 + Phase 2
2. Complete Phase 3 (US1)
3. Run `pytest tests/unit/` — all pass
4. Validate with `python -m src.cli <directory> <label>`

### Incremental Delivery

1. Setup + Foundational → migrations in place, model updated
2. US1 → labelled loading + two-account scenario
3. US2 → idempotency confirmed
4. Polish → line-length check, schema doc update, full test run

---

## Notes

- `create_table_if_not_exists()` is **deleted** from `load.py` — yoyo is the sole schema
  owner from this feature forward
- All existing unit tests in `test_transaction.py`, `test_transform.py`, `test_load.py`
  need updating to pass `account_label` where required; failing tests count as Red
- Integration tests auto-skip without `DATABASE_URL`
- Existing rows in the database (from feature 001) receive `account_label = 'unknown'`
  via migration 0002 DEFAULT; their stored hashes are legacy and remain valid
