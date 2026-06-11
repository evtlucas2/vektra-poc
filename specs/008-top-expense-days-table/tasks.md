---
description: "Task list for Top Expense Days Table"
---

# Tasks: Top Expense Days Table

**Input**: Design documents from `specs/008-top-expense-days-table/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/ ✅

**TDD Note**: Tests are **mandatory** (Constitution Principle III). The pure selection logic
(`top_expense_days`) and the frame extract are written test-first. The Streamlit table render
is verified manually.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no shared state dependencies)
- **[Story]**: Maps to user story from spec.md (US1)

---

## Phase 1: Setup

- [X] T001 Confirm baseline tests are green (`pytest tests/unit/ -q`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: None — reuses existing DB layer and `pandas`; no schema, migration, or dependency
changes. Proceed to US1.

*(No foundational tasks.)*

---

## Phase 3: User Story 1 — See My Worst Spending Days (Priority: P1) 🎯 MVP

**Goal**: A read-only table of the highest-expense days (5th-percentile tail of `difference`,
expenses only), sorted expense-descending, rendered directly below the decomposition chart.

**Independent Test**: `pytest tests/unit/test_expenses.py tests/unit/test_timeseries_extract.py`
plus integration `test_expenses_pipeline.py`; then `streamlit run src/timeseries/app.py` shows
the "Highest expense days" table beneath the chart.

### Tests for User Story 1 ⚠️ Write FIRST — confirm all FAIL before implementation

- [X] T002 [P] [US1] Write failing unit tests for `top_expense_days(df, percentile=5)` in `tests/unit/test_expenses.py`: selects rows with `difference <= quantile(0.05)` AND `difference < 0`; adds positive `expense = -difference`; sorted expense-descending (largest first); empty DataFrame → empty; all-non-negative `difference` → empty; non-empty guard (≥ 1 expense day ⇒ ≥ 1 row, the global minimum); `EXPENSE_PERCENTILE == 5`
- [X] T003 [P] [US1] Write failing unit tests for `fetch_daily_balance_frame(conn)` in `tests/unit/test_timeseries_extract.py`: returns a pandas DataFrame with columns `balance_date, day_of_week, weekend, balance, difference` from a mocked grouped query; empty result → empty DataFrame
- [X] T004 [P] [US1] Write failing integration test `test_top_expense_days` in `tests/integration/test_expenses_pipeline.py`: seed `daily_balance` with known `difference` spread, fetch frame + `top_expense_days`, assert the selected dates and descending order (skips without `DATABASE_URL`)

### Implementation for User Story 1 (after T002–T004 confirmed failing)

- [X] T005 [P] [US1] Implement pure `top_expense_days(df, percentile=EXPENSE_PERCENTILE)` with `EXPENSE_PERCENTILE = 5` in `src/timeseries/expenses.py`: empty-guard; `threshold = df["difference"].quantile(percentile/100)`; select `difference <= threshold` and `difference < 0`; add `expense = -difference`; sort by `difference` ascending (depends T002)
- [X] T006 [P] [US1] Implement `fetch_daily_balance_frame(conn) -> pandas.DataFrame` in `src/timeseries/extract.py` using `SELECT balance_date, day_of_week, weekend, balance, difference FROM daily_balance ORDER BY balance_date` (depends T003)
- [X] T007 [US1] Update `src/timeseries/app.py`: add `_render_expense_table(conn_or_frame)` that fetches the frame, computes `top_expense_days`, renders the columns date/expense/day_of_week/balance with `st.dataframe` (or `st.table`), and shows `st.info("No expense days to display.")` when empty; call it in `main()` **after** the chart render so the table appears directly below the decomposition chart (depends T005, T006)
- [X] T008 [US1] Run unit tests T002–T003 (Green) and the integration test T004; confirm column/order match `contracts/ui-table.md` (depends T005, T006, T007)

**Checkpoint**: US1 complete — top expense days table renders below the chart.

---

## Phase 4: Polish & Cross-Cutting Concerns

- [X] T009 [P] Validate all functions ≤25 lines across `src/timeseries/expenses.py`, `src/timeseries/extract.py`, and the new `app.py` render function (Constitution Principle IV)
- [X] T010 Run the full unit suite and confirm all tests pass: `pytest tests/unit/`
- [ ] T011 Manual check: `streamlit run src/timeseries/app.py` shows the "Highest expense days" table directly below the decomposition chart, largest expense first; and shows the empty-state message when there are no expense days

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 baseline
- **Foundational (Phase 2)**: none
- **US1 (Phase 3)**: T002–T004 (tests, Red) → T005 + T006 (parallel impl) → T007 (app) → T008 (verify)
- **Polish (Phase 4)**: after US1

### Within US1

- Tests T002, T003, T004 all parallel (different files) — all Red before implementation
- T005 (`expenses.py`) and T006 (`extract.py`) parallel — different files
- T007 (`app.py`) depends on T005 + T006; T008 verifies

### Parallel Opportunities

```bash
# US1 tests — all parallel (Red):
Task: T002 — tests/unit/test_expenses.py
Task: T003 — tests/unit/test_timeseries_extract.py
Task: T004 — tests/integration/test_expenses_pipeline.py

# US1 implementation — pure module + extract parallel:
Task: T005 — src/timeseries/expenses.py
Task: T006 — src/timeseries/extract.py
# then:
Task: T007 — src/timeseries/app.py
```

---

## Implementation Strategy

### MVP (US1)

1. Phase 1 → Phase 3 (tests first, then implementation)
2. `pytest tests/unit/` all pass
3. Launch `streamlit run src/timeseries/app.py` and confirm the table renders below the chart

### Notes

- `top_expense_days` is pure (no I/O) — primary unit-test target; the non-empty guard falls out
  because the global-minimum `difference` is always ≤ the 5th percentile
- Integration tests auto-skip without `DATABASE_URL`
- No schema, migration, or dependency changes; `pandas` already present
- Existing commands (`python -m src.cli`, `python -m src.balance`) and the decomposition chart
  are unchanged; the table is added below the chart in `main()`
