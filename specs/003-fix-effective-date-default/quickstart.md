# Quickstart: Fix Effective Date — Always Non-Null

**Branch**: `003-fix-effective-date-default` | **Date**: 2026-06-05

## What Changed

- Transactions without a MEMO date now store `effective_date = posted_date`
  instead of `null`.
- The database column is now `NOT NULL`.
- Migration `0003` backfills any existing null rows.

## Applying the Migration

Migrations run automatically when the CLI starts. To apply manually:

```bash
yoyo apply --database "$DATABASE_URL" migrations/
```

Expected output includes `0003_effective_date_not_null`.

## Verifying the Fix

```sql
-- Zero nulls expected after migration
SELECT COUNT(*) FROM transactions WHERE effective_date IS NULL;
-- Expected: 0

-- Rows without MEMO date should have effective_date = posted_date
SELECT posted_date, effective_date, description
FROM transactions
WHERE description NOT LIKE '__/__/%'   -- rough filter for non-MEMO-date rows
LIMIT 10;
-- effective_date and posted_date should match for these rows
```

## Running Tests

```bash
pytest tests/unit/test_transform.py -v
pytest tests/unit/ -q
```

All tests should pass; assertions for `effective_date is None` have been replaced
with assertions for `effective_date == posted_date`.

## Reference

- Data model: [data-model.md](data-model.md)
- Migration file: `migrations/0003_effective_date_not_null.sql`
