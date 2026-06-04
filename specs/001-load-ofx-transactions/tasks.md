---

description: "Task list for Load OFX Transactions feature"
---

# Tasks: Load OFX Transactions

**Input**: Design documents from `specs/001-load-ofx-transactions/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/ ✅

**TDD Note**: Tests are **mandatory** (Constitution Principle III). Every task group follows
Red → Green → Refactor. Test tasks MUST be completed and confirmed failing before the
corresponding implementation tasks begin.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Project initialization and directory structure

- [X] T001 Create project directory structure: `src/etl/`, `src/models/`, `tests/unit/`, `tests/integration/`, `config/`, `tests/fixtures/empty_dir/`, `tests/fixtures/single/`, `tests/fixtures/multi/`
- [X] T002 Create `requirements.txt` with `psycopg2-binary`, `python-dotenv`, `pytest`, `pytest-mock`
- [X] T003 [P] Create `config/.env.example` documenting `DATABASE_URL` and `DATA_ROOT` variables
- [X] T004 [P] Create OFX test fixture files: `tests/fixtures/single/sample.ofx` (2 valid transactions, 1 filtered "Saldo do dia"), `tests/fixtures/multi/january.ofx` (3 transactions), `tests/fixtures/multi/february.ofx` (2 transactions)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared infrastructure — Transaction model and database layer — that ALL user
stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 [P] Create empty package markers: `src/etl/__init__.py` and `src/models/__init__.py`
- [X] T006 [P] Write failing test for `Transaction` dataclass (fields, types, nullability) in `tests/unit/test_transaction.py` ⚠️ Confirm test FAILS before T007
- [X] T007 Create `Transaction` dataclass with fields `posted_date`, `effective_date`, `description`, `amount`, `transaction_hash` in `src/models/transaction.py` (depends T006)
- [X] T008 Write failing tests for `db_connect()` and `create_table_if_not_exists()` in `tests/unit/test_load.py` ⚠️ Confirm tests FAIL before T009
- [X] T009 Implement `db_connect()` (from `DATABASE_URL` env) and `create_table_if_not_exists()` (CREATE TABLE IF NOT EXISTS with unique constraint on `transaction_hash`) in `src/etl/load.py` (depends T008)

**Checkpoint**: Foundation ready — `Transaction` model and database layer verified. User story phases can now begin.

---

## Phase 3: User Story 1 — Load OFX Directory into Database (Priority: P1) 🎯 MVP

**Goal**: Pipeline scans a directory, processes each OFX file sequentially, and loads all
valid transactions into the database.

**Independent Test**: Run `pytest tests/unit/ tests/integration/test_pipeline.py::test_load_directory`
and confirm row count matches non-filtered transactions across all fixture files.

### Tests for User Story 1 ⚠️ Write FIRST — confirm all FAIL before any implementation

- [X] T010 [P] [US1] Write failing unit test for `scan()`: returns sorted list of `.ofx` Paths, handles case-insensitive extension in `tests/unit/test_scan.py`
- [X] T011 [P] [US1] Write failing unit test for `extract_transactions()`: parses OFX XML body from `tests/fixtures/single/sample.ofx`, returns list of raw dicts in `tests/unit/test_extract.py`
- [X] T012 [P] [US1] Write failing unit tests for `transform_transactions()`: filter by `FILTERED_NAMES`, MEMO pattern split (matched + unmatched), `effective_date` derivation in `tests/unit/test_transform.py`
- [X] T013 [P] [US1] Write failing unit tests for `insert_transactions()`: inserts rows, returns count in `tests/unit/test_load.py`
- [X] T014 [P] [US1] Write failing integration test `test_load_directory`: directory with 2 fixture files → correct total row count in database in `tests/integration/test_pipeline.py`

### Implementation for User Story 1 (after all T010–T014 confirmed failing)

- [X] T015 [P] [US1] Implement `scan(directory: Path) -> list[Path]` returning sorted `.ofx` files (case-insensitive, uses `pathlib`) in `src/etl/scan.py` (depends T010)
- [X] T016 [P] [US1] Implement `extract_transactions(path: Path) -> list[dict]` stripping plain-text header before `<OFX` tag, parsing XML with `xml.etree.ElementTree`, extracting `DTPOSTED`, `NAME`, `MEMO`, `TRNAMT` per `<STMTTRN>` in `src/etl/extract.py` (depends T011)
- [X] T017 [US1] Implement `transform_transactions(raw: list[dict]) -> list[Transaction]` with `FILTERED_NAMES = frozenset({"Saldo do dia", "Saldo Anterior"})` and `MEMO_PATTERN = re.compile(...)` as module constants; compute `transaction_hash` via SHA-256 in `src/etl/transform.py` (depends T012, T007)
- [X] T018 [US1] Implement `insert_transactions(conn, transactions: list[Transaction]) -> int` using `INSERT ... ON CONFLICT (transaction_hash) DO NOTHING`; return inserted count in `src/etl/load.py` (depends T013, T009)
- [X] T019 [US1] Implement `src/cli.py` entry point: load `.env` with `python-dotenv`, resolve directory from `DATA_ROOT` + argument, call `scan → extract → transform → load` per file, print per-file and total summary to stdout in `src/cli.py` (depends T015, T016, T017, T018)
- [X] T020 [US1] Run integration test `test_load_directory` and confirm it passes; verify per-file stdout summary format matches contract in `contracts/cli-interface.md` (depends T014, T019)

**Checkpoint**: User Story 1 complete — pipeline loads multi-file OFX directory into PostgreSQL.

---

## Phase 4: User Story 2 — Empty Directory (Priority: P2)

**Goal**: Pipeline exits cleanly with code 0 and an informational message when the input
directory contains no `.ofx` files.

**Independent Test**: Run `pytest tests/integration/test_pipeline.py::test_empty_directory`
and confirm exit code is 0, zero rows inserted.

### Tests for User Story 2 ⚠️ Write FIRST — confirm FAIL before implementation

- [X] T021 [P] [US2] Write failing unit test for `scan()` with an empty directory: returns `[]` in `tests/unit/test_scan.py`
- [X] T022 [P] [US2] Write failing integration test `test_empty_directory`: `tests/fixtures/empty_dir/` → exit code 0, 0 rows inserted, stdout contains "No OFX files found" in `tests/integration/test_pipeline.py`

### Implementation for User Story 2

- [X] T023 [US2] Update `src/cli.py` to handle empty scan result: log `[INFO] No OFX files found in <directory>. Nothing to do.` to stdout and exit with code 0 (depends T021, T019)
- [X] T024 [US2] Run integration test `test_empty_directory` and confirm it passes (depends T022, T023)

**Checkpoint**: User Story 2 complete — empty directory is a graceful no-op.

---

## Phase 5: User Story 3 — Idempotent Reload (Priority: P3)

**Goal**: Running the pipeline twice against the same directory produces no duplicate rows.

**Independent Test**: Run `pytest tests/integration/test_pipeline.py::test_idempotent_reload`
and confirm row count is identical after both runs.

### Tests for User Story 3 ⚠️ Write FIRST — confirm FAILS before implementation

- [X] T025 [P] [US3] Write failing integration test `test_idempotent_reload`: load same fixture directory twice, assert row count after second run equals row count after first run in `tests/integration/test_pipeline.py`

### Implementation for User Story 3

- [X] T026 [US3] Run integration test `test_idempotent_reload` — `ON CONFLICT (transaction_hash) DO NOTHING` in T018 should already cover this; if test fails, review `insert_transactions()` in `src/etl/load.py` (depends T025, T018)

**Checkpoint**: All user stories complete — pipeline handles all scenarios from spec.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Clean code compliance and full validation.

- [X] T027 [P] Add type hints to all public functions in `src/etl/scan.py`, `src/etl/extract.py`, `src/etl/transform.py`, `src/etl/load.py`, `src/models/transaction.py`
- [X] T028 [P] Verify all functions are ≤25 lines (Constitution Principle IV); refactor any violators — extract helpers if needed
- [X] T029 Run full test suite and confirm all tests pass: `pytest`
- [X] T030 Run quickstart.md validation scenarios end-to-end against a local PostgreSQL instance

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup (**blocks all user stories**)
- **US1 (Phase 3)**: Depends on Foundational — **MVP; must complete before US2/US3**
- **US2 (Phase 4)**: Depends on Foundational + US1 cli.py (T019)
- **US3 (Phase 5)**: Depends on Foundational + US1 load.py (T018)
- **Polish (Phase 6)**: Depends on all user story phases

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational — no dependency on US2/US3
- **US2 (P2)**: Depends on US1 `cli.py` (T019) for the no-op exit path
- **US3 (P3)**: Depends on US1 `load.py` (T018) for the ON CONFLICT logic

### Within Each User Story

- Test tasks (T010–T014, T021–T022, T025) MUST be written and confirmed failing before implementation
- Models before services: T007 before T017
- DB layer before insert: T009 before T018
- All ETL modules (T015, T016, T017, T018) before cli.py (T019)

### Parallel Opportunities

- All Phase 1 tasks marked [P]: T003, T004 (with T001 as prerequisite)
- All Phase 2 test tasks marked [P]: T006, T008 can run simultaneously
- All US1 test tasks T010–T014: fully parallel (different files)
- All US1 implementation tasks T015, T016: parallel (different files); T017, T018 follow after models/db
- T021 and T022 (US2 tests): parallel

---

## Parallel Example: User Story 1 Tests

```bash
# Launch all US1 test tasks together (all RED — must fail):
Task: T010 — tests/unit/test_scan.py
Task: T011 — tests/unit/test_extract.py
Task: T012 — tests/unit/test_transform.py
Task: T013 — tests/unit/test_load.py
Task: T014 — tests/integration/test_pipeline.py::test_load_directory

# After confirming all fail, launch parallel implementations:
Task: T015 — src/etl/scan.py
Task: T016 — src/etl/extract.py
# Then sequentially:
Task: T017 — src/etl/transform.py  (after T007)
Task: T018 — src/etl/load.py       (after T009)
Task: T019 — src/cli.py            (after T015-T018)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (tests first, then implementation)
4. **STOP and VALIDATE**: Run `pytest` + quickstart.md scenarios
5. Merge or demo if ready

### Incremental Delivery

1. Setup + Foundational → base infrastructure
2. US1 → working directory-to-database pipeline (MVP)
3. US2 → graceful empty-directory handling
4. US3 → confirmed idempotency
5. Polish → clean code compliance

---

## Notes

- [P] tasks = different files, no shared state dependencies
- [Story] label maps task to a user story for traceability
- TDD is mandatory per Constitution Principle III — never skip the Red step
- Commit after each phase checkpoint
- `tests/fixtures/` live under the project root; production data lives under `DATA_ROOT` (outside project)
