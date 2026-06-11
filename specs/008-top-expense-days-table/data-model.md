# Data Model: Top Expense Days Table

**Branch**: `008-top-expense-days-table` | **Date**: 2026-06-11

**No database schema changes.** This feature reads the existing `daily_balance` table and
produces an in-memory, display-only result.

## Input: Daily Balance Frame (in-memory)

Built by `extract.fetch_daily_balance_frame(conn)`:

| Column | Type | Source |
|--------|------|--------|
| `balance_date` | date | `daily_balance.balance_date` |
| `day_of_week` | int | `daily_balance.day_of_week` (0=Mon … 6=Sun) |
| `weekend` | int | `daily_balance.weekend` |
| `balance` | float | `daily_balance.balance` |
| `difference` | float | `daily_balance.difference` (day-over-day change) |

Ordered by `balance_date` ascending. Empty table → empty DataFrame.

## Computation: Top Expense Days

Produced by `expenses.top_expense_days(df, percentile=5)`:

1. If `df` is empty → return empty result.
2. `threshold = df["difference"].quantile(percentile / 100)` (linear interpolation).
3. Select rows where `difference <= threshold` **and** `difference < 0`.
4. Add `expense = -difference` (positive magnitude).
5. Sort by `difference` ascending (= `expense` descending).

Validation / guarantees:
- No row with `difference >= 0` appears (SC-003).
- If any expense day exists, ≥ 1 row is returned (the global minimum is always ≤ the 5th
  percentile) — SC-005.
- If no expense day exists, the result is empty (FR-006).

## Output: Top Expense Row (display-only)

| Field | Meaning |
|-------|---------|
| `balance_date` | The day |
| `expense` | Expense amount (positive; `= -difference`) |
| `day_of_week` | 0=Mon … 6=Sun (context) |
| `balance` | End-of-day balance (context) |

Rendered as a table on the main page, largest expense first.

## Entities Summary

- **Daily Balance** (existing table, read-only) — source rows.
- **Daily Balance Frame** (in-memory DataFrame) — all rows for selection.
- **Top Expense Days** (in-memory DataFrame) — selected, sorted, display-only result.
