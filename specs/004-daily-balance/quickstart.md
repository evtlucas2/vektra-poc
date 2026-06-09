# Quickstart: Calculate Daily Balance

**Branch**: `004-daily-balance` | **Date**: 2026-06-08

## Prerequisites

- Transactions already loaded via `python -m src.cli <directory> <label>`
- `DATABASE_URL` set in `config/.env`
- Dependencies installed: `pip install -r requirements.txt`

## Applying the Migration

The new `daily_balance` table is created automatically when the command runs. To apply
manually:

```bash
yoyo apply --database "$DATABASE_URL" migrations/
# expect 0004_create_daily_balance in the applied list
```

## Running the Command

```bash
# Compute the daily balance series with a starting balance of 1000.00
python -m src.balance 1000.00
```

Expected output:

```
[INFO] Daily balance: 92 day(s) written from 2026-01-05 to 2026-04-06 (initial 1000.00)
```

No-transactions case:

```
[INFO] No transactions found. Nothing to do.
```

## Verifying the Result

```sql
-- One row per calendar day in range; zero gaps
SELECT COUNT(*) FROM daily_balance;

-- Inspect the series
SELECT balance_date, day_of_week, weekend, balance, difference
FROM daily_balance
ORDER BY balance_date
LIMIT 15;

-- First day's difference must be 0
SELECT difference FROM daily_balance ORDER BY balance_date LIMIT 1;
-- Expected: 0.00

-- Weekend flag sanity: weekend=1 exactly for Sat(5)/Sun(6)
SELECT DISTINCT day_of_week, weekend FROM daily_balance ORDER BY day_of_week;
-- Expected: weekend=1 only for day_of_week 5 and 6

-- Difference equals balance minus prior balance (window check)
SELECT balance_date,
       balance,
       difference,
       balance - LAG(balance) OVER (ORDER BY balance_date) AS expected_diff
FROM daily_balance
ORDER BY balance_date
LIMIT 15;
-- difference should match expected_diff for all rows except the first (0.00)
```

## Idempotency Check

```bash
python -m src.balance 1000.00
python -m src.balance 1000.00
# Row count identical after both runs (table is fully replaced each time)
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM daily_balance;"
```

## Running Tests

```bash
# Pure compute logic + model + mocked extract/load (no database)
pytest tests/unit/test_balance_compute.py tests/unit/test_balance_extract.py \
       tests/unit/test_balance_load.py tests/unit/test_daily_balance_model.py -v

# Full unit suite
pytest tests/unit/

# Integration (requires DATABASE_URL)
DATABASE_URL="postgresql://..." pytest tests/integration/test_balance_pipeline.py
```

## Reference

- CLI contract: [contracts/cli-interface.md](contracts/cli-interface.md)
- Schema contract: [contracts/database-schema.md](contracts/database-schema.md)
- Data model: [data-model.md](data-model.md)
