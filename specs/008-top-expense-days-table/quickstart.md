# Quickstart: Top Expense Days Table

**Branch**: `008-top-expense-days-table` | **Date**: 2026-06-11

## Prerequisites

- Daily balance computed (`python -m src.balance <initial-balance>`), so `daily_balance` has
  rows with a spread of `difference` values.
- `DATABASE_URL` set in `config/.env`.
- Dependencies installed (`pip install -r requirements.txt`) — no new ones for this feature.

## Launching

```bash
streamlit run src/timeseries/app.py
```

Below the decomposition chart you will see a **"Highest expense days"** table: the days whose
daily change is in the most-extreme 5% (largest expenses), ordered with the biggest expense at
the top.

## Automated Validation (no browser)

```bash
pytest tests/unit/test_expenses.py tests/unit/test_timeseries_extract.py -v
```

Checks:
- `top_expense_days` selects rows at/below the 5th-percentile threshold and `difference < 0`.
- Result is sorted by expense descending; an `expense` column (positive) is present.
- Empty input → empty result; all-positive `difference` → empty result.
- Non-empty guard: with ≥ 1 expense day, ≥ 1 row is returned.
- `fetch_daily_balance_frame` returns the expected columns.

## Integration Check (requires database)

```bash
DATABASE_URL="postgresql://..." pytest tests/integration/test_expenses_pipeline.py
```

Seeds `daily_balance` with known `difference` values, then asserts the selected days and order.

## Manual Verification (SQL cross-check)

```sql
-- 5th-percentile threshold of daily change
SELECT percentile_cont(0.05) WITHIN GROUP (ORDER BY difference) FROM daily_balance;

-- The days the table should show (largest expense first)
SELECT balance_date, -difference AS expense, day_of_week, balance
FROM daily_balance
WHERE difference <= (SELECT percentile_cont(0.05) WITHIN GROUP (ORDER BY difference) FROM daily_balance)
  AND difference < 0
ORDER BY difference ASC;
```

## Reference

- UI contract: [contracts/ui-table.md](contracts/ui-table.md)
- Data model: [data-model.md](data-model.md)
- Research/decisions: [research.md](research.md)
