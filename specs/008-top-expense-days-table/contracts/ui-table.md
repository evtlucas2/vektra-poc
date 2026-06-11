# Contract: Top Expense Days Table (UI)

**Feature**: Top Expense Days Table | **Date**: 2026-06-11

## Placement

On the existing Streamlit main page (`streamlit run src/timeseries/app.py`), a section titled
"Highest expense days" appears **directly below the daily balance decomposition chart**.
Render order in `main()`: decomposition chart (and its download button) first, then this table.
If the chart cannot be drawn (insufficient data), its warning shows and this table still
renders immediately below it.

## Content

A table with one row per selected high-expense day, ordered largest expense first:

| Column | Description |
|--------|-------------|
| Date | The day (`balance_date`) |
| Expense | Positive expense amount (`-difference`) |
| Day of week | 0 = Monday … 6 = Sunday |
| Balance | End-of-day balance |

## Selection Rule (matches data-model)

- Threshold = 5th percentile of `difference` across all `daily_balance` rows.
- Included rows: `difference <= threshold` AND `difference < 0`.
- Sorted by expense descending (most negative `difference` first).

## States

| Condition | UI |
|-----------|----|
| Expense days exist | Table with ≥ 1 row, largest expense at top |
| No `daily_balance` data, or no expense days | `st.info` message ("No expense days to display."), no table |

## Underlying Function Contracts (unit-testable, no Streamlit)

```python
# extract.py
fetch_daily_balance_frame(conn) -> pandas.DataFrame
#   columns: balance_date, day_of_week, weekend, balance, difference; ordered by date

# expenses.py
EXPENSE_PERCENTILE = 5
top_expense_days(df, percentile=EXPENSE_PERCENTILE) -> pandas.DataFrame
#   selected rows + 'expense' column, sorted expense-descending; empty df -> empty result
```
