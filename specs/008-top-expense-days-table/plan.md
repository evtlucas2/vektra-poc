# Implementation Plan: Top Expense Days Table

**Branch**: `008-top-expense-days-table` | **Date**: 2026-06-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/008-top-expense-days-table/spec.md`

## Summary

Add a read-only "highest expense days" table to the existing Streamlit main page, rendered
**directly below the daily balance decomposition chart** (after the chart and its download
button, within the same `main()` flow). The table reads the `daily_balance` table, treats a
negative `difference`
as a day's expense, selects the days whose `difference` is at or below the 5th percentile of
all daily changes (and is negative), and lists them sorted by expense descending. A new pure
function `top_expense_days()` does the selection/sort; a new `extract` function fetches the
`daily_balance` rows as a DataFrame; `app.py` renders the result. No schema change, no new
dependency (pandas already present).

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: Unchanged — `pandas` (selection), `streamlit` (table render),
`psycopg2-binary`. No new dependencies.

**Storage**: PostgreSQL — reads the existing `daily_balance` table (read-only)

**Testing**: `pytest`, `pytest-mock`

**Project Type**: Time-series analysis + Streamlit UI

**Performance Goals**: Table renders in under 2 seconds for typical data

**Constraints**:
- `DATABASE_URL` from env / `config/.env`
- Expense = negative `difference`; selection threshold = 5th percentile of `difference`
- Non-empty when ≥ 1 expense day exists; clear message otherwise

**Scale/Scope**: One added table section on the main page; selection over the full
`daily_balance` series

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Data Decoupling | ✅ PASS | `DATABASE_URL` from env; no hardcoded paths |
| II. ETL Discipline | ✅ PASS | `fetch_daily_balance_frame` (extract/I-O) is separate from pure `top_expense_days` (compute); `app.py` is presentation only |
| III. Test-First | ✅ PASS | Pure selection logic and the frame extract are unit-tested before implementation |
| IV. Clean Code | ✅ PASS | `EXPENSE_PERCENTILE = 5` named constant; functions ≤25 lines |
| V. Simplicity First | ✅ PASS | `pandas.quantile` for the percentile; reuses existing DB/UI; no new dependency, no schema change |

*Post-design re-check*: All gates hold after Phase 1.

## Project Structure

### Documentation (this feature)

```text
specs/008-top-expense-days-table/
├── plan.md          # This file
├── research.md      # Phase 0 output
├── data-model.md    # Phase 1 output
├── quickstart.md    # Phase 1 output
├── contracts/       # Phase 1 output
│   └── ui-table.md
└── tasks.md         # Phase 2 output (/speckit-tasks)
```

### Source Code Changes

```text
src/timeseries/
├── extract.py                      # UPDATED: + fetch_daily_balance_frame(conn) -> pandas DataFrame
├── expenses.py                     # NEW pure: top_expense_days(df, percentile=EXPENSE_PERCENTILE) -> DataFrame
└── app.py                          # UPDATED: render the expense table directly below the
                                    #   decomposition chart (new _render_expense_table called
                                    #   in main() after the chart render)

tests/
├── unit/
│   ├── test_expenses.py            # NEW — selection, threshold, ordering, empty/no-expense, non-empty guard
│   └── test_timeseries_extract.py  # UPDATED — fetch_daily_balance_frame returns expected columns (mocked)
└── integration/
    └── test_expenses_pipeline.py   # NEW — seed daily_balance, fetch frame, top_expense_days (skips without DATABASE_URL)
```

**Structure Decision**: A new pure module `src/timeseries/expenses.py` holds the
selection/sort logic so it is unit-testable without a database (Principle II/III). The
extract function for the full `daily_balance` frame lives alongside the existing
`fetch_balance_series` in `extract.py`. `app.py` gains one render section
placed **immediately below the daily balance decomposition chart**: `main()` first renders the
chart (and its download button), then calls a new `_render_expense_table(...)` so the table
always appears beneath the chart. The table is independent of the decomposition's minimum-data
requirement — when the chart cannot be drawn (insufficient data) the warning shows and the
expense table still renders below it whenever `daily_balance` has expense days.

## Complexity Tracking

> **No violations — no entries required.**
