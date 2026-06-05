# Quickstart: Add Account Label to Transactions

**Branch**: `002-add-account-label` | **Date**: 2026-06-05

## Prerequisites

Same as feature 001, plus `yoyo-migrations>=9.0` in `requirements.txt`.

```bash
pip install -r requirements.txt
```

## Schema Migration

Migrations run automatically when the CLI starts. To apply manually:

```bash
yoyo apply --database "$DATABASE_URL" migrations/
```

To inspect migration status:

```bash
yoyo list --database "$DATABASE_URL" migrations/
```

## Running the Pipeline (updated syntax)

```bash
# Load checking account
python -m src.cli /data/raw/checking/ checking

# Load savings account from the same OFX files (both runs succeed)
python -m src.cli /data/raw/checking/ savings
```

Expected output (first run):

```
[INFO] january.ofx → 3 inserted, 0 skipped (filtered), 0 errors  [account: checking]
[INFO] february.ofx → 2 inserted, 1 skipped (filtered), 0 errors  [account: checking]
[INFO] Total: 5 inserted, 1 skipped, 0 errors across 2 file(s)  [account: checking]
```

Expected output (second run, same label):

```
[INFO] january.ofx → 0 inserted, 0 skipped (filtered), 0 errors  [account: checking]
[INFO] february.ofx → 0 inserted, 1 skipped (filtered), 0 errors  [account: checking]
[INFO] Total: 0 inserted, 1 skipped, 0 errors across 2 file(s)  [account: checking]
```

## Verifying the Result

```sql
-- Check account labels present
SELECT account_label, COUNT(*) FROM transactions GROUP BY account_label;

-- Confirm rows per account
SELECT account_label, posted_date, description, amount
FROM transactions
ORDER BY account_label, posted_date DESC
LIMIT 20;
```

## Two-Account Scenario

```bash
python -m src.cli /data/raw/statements/ account-a
python -m src.cli /data/raw/statements/ account-b

# Both labels should appear, each with the same transaction count
psql "$DATABASE_URL" -c "SELECT account_label, COUNT(*) FROM transactions GROUP BY account_label;"
```

Expected: two rows, one per label, same count.

## Error Cases

```bash
# Missing label
python -m src.cli /data/raw/statements/
# stderr: [ERROR] Account label must not be empty.
# exit code: 1

# Empty label
python -m src.cli /data/raw/statements/ "   "
# stderr: [ERROR] Account label must not be empty.
# exit code: 1
```

## Running Tests

```bash
pytest tests/unit/
DATABASE_URL="postgresql://..." pytest tests/integration/
```

## Reference

- CLI contract: [contracts/cli-interface.md](contracts/cli-interface.md)
- Data model: [data-model.md](data-model.md)
- Feature 001 schema: `specs/001-load-ofx-transactions/contracts/database-schema.md`
