# Research: Top Expense Days Table

**Branch**: `008-top-expense-days-table` | **Date**: 2026-06-11

## Decision 1: Expense Definition from `difference`

**Decision**: A day's expense is the magnitude of a negative `difference` (the day-over-day
balance change). Days with `difference >= 0` are not expenses and are excluded. Display the
expense as a positive number (`expense = -difference`).

**Rationale**: `daily_balance` has no dedicated expense column; `difference` is the only
per-day signed change. The request restricts the source to `daily_balance`, so expense must be
derived from `difference`. A drop in balance (negative change) is exactly a net expense day.

---

## Decision 2: 5th-Percentile Selection (low tail of `difference`)

**Decision**: Compute `threshold = quantile(difference, 0.05)` over all rows (pandas default
linear interpolation). Select rows where `difference <= threshold` **and** `difference < 0`.

**Rationale**: The highest-expense days are the most-negative `difference` values — the low
tail. The 5th percentile of `difference` is that tail's boundary, so `difference <= P5` picks
the most-extreme ~5% (the largest expenses). The extra `difference < 0` guard ensures only true
expenses are shown if the data is unusual (mostly non-negative changes), satisfying FR-002.

**Non-empty guarantee**: The global minimum `difference` is always `<= quantile(., 0.05)`, so
if at least one expense day exists (min `difference < 0`), at least one row is selected —
satisfying FR-007 without special-casing small N. If the minimum is `>= 0`, there are no
expense days and the result is empty (FR-006).

**Alternatives considered**:
- Percentile over expense-only days — narrows the base; the spec says "across the available
  daily balance data" (all rows), so the full-series base is used.
- `nlargest(5%)` by expense — equivalent in spirit but the percentile threshold is the literal
  reading and is trivially recomputable for the SC-001 check.

---

## Decision 3: Ordering — Descending by Expense

**Decision**: Sort the selected rows by `difference` ascending (most negative first), which is
expense descending (largest expense at the top). Add an `expense` column for display.

**Rationale**: Matches FR-004 / SC-002: the largest expense is first, decreasing downward.

---

## Decision 4: Pure Selection Function + Separate Extract

**Decision**:
- `expenses.top_expense_days(df, percentile=EXPENSE_PERCENTILE=5) -> DataFrame` — pure; takes a
  DataFrame with `balance_date, day_of_week, weekend, balance, difference`; returns the selected,
  sorted rows with an added `expense` column. Empty input → empty output.
- `extract.fetch_daily_balance_frame(conn) -> DataFrame` — reads
  `SELECT balance_date, day_of_week, weekend, balance, difference FROM daily_balance ORDER BY
  balance_date`.

**Rationale**: Keeping selection pure (no I/O) makes the percentile/ordering logic unit-testable
without a database (Principle III) and keeps the ETL phases separated (Principle II). The
existing `fetch_balance_series` is unchanged; the new frame fetch serves this table.

---

## Decision 5: Rendering on the Main Page

**Decision**: In `app.py`, render the table **directly below the daily balance decomposition
chart**. `main()` calls the existing chart render first, then a new
`_render_expense_table(...)` that fetches the frame, computes `top_expense_days`, and renders
it with `st.dataframe` (or `st.table`). When the result is empty, show
`st.info("No expense days to display.")`.

**Rationale**: The user asked for the table to sit beneath the decomposition chart, so the
render order in `main()` is chart → expense table. The table is independent of the chart's
minimum-data requirement — it appears whenever expense days exist, even when the chart shows an
"insufficient data" warning instead of the figure (the table still renders below that warning).
A second small read query is acceptable for a POC (Principle V); it keeps the two concerns
(series for the chart, frame for the table) simple and separately tested.
