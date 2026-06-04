# Quickstart: Load OFX Transactions

**Branch**: `001-load-ofx-transactions` | **Date**: 2026-06-04 (updated for directory input)

## Prerequisites

- Python 3.11+
- PostgreSQL server running and accessible
- `psycopg2-binary` and `python-dotenv` installed (see Setup)

## Setup

```bash
# 1. Install dependencies
pip install psycopg2-binary python-dotenv pytest pytest-mock

# 2. Configure environment
cp config/.env.example config/.env
# Edit config/.env — set DATABASE_URL and DATA_ROOT

# 3. Verify database connection
psql "$DATABASE_URL" -c "SELECT 1;"
```

`config/.env.example` contents:

```dotenv
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
DATA_ROOT=/path/to/data/root
```

## Running the Pipeline

```bash
# Load all OFX files in a directory (path relative to DATA_ROOT, or absolute)
python -m src.cli raw/statements/
```

Expected output (2 files found):

```
[INFO] january.ofx → 47 inserted, 2 skipped (filtered), 0 errors
[INFO] february.ofx → 31 inserted, 1 skipped (filtered), 0 errors
[INFO] Total: 78 inserted, 3 skipped, 0 errors across 2 file(s)
```

Expected output (empty directory):

```
[INFO] No OFX files found in raw/statements. Nothing to do.
```

## Verifying the Result

```sql
-- Check total row count
SELECT COUNT(*) FROM transactions;

-- Inspect recent entries
SELECT posted_date, effective_date, description, amount
FROM transactions
ORDER BY posted_date DESC
LIMIT 10;

-- Confirm filtered names are absent
SELECT COUNT(*) FROM transactions
WHERE description IN ('Saldo do dia', 'Saldo Anterior');
-- Expected: 0
```

## Running Tests

```bash
# All tests
pytest

# Unit tests only (no database required)
pytest tests/unit/

# Integration tests (requires DATABASE_URL pointing to a test database)
DATABASE_URL="postgresql://user:pass@localhost/testdb" pytest tests/integration/
```

## Re-running the Pipeline (Idempotency Check)

```bash
# Run twice with the same directory
python -m src.cli raw/statements/
python -m src.cli raw/statements/

# Row count must be identical after both runs
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM transactions;"
```

## Edge Case: Empty Directory

```bash
mkdir /tmp/empty_statements
python -m src.cli /tmp/empty_statements/
# Expected: [INFO] No OFX files found in /tmp/empty_statements. Nothing to do.
# Exit code: 0
echo $?  # → 0
```

## Edge Case: One Malformed File in a Multi-File Directory

If one OFX file cannot be parsed, it is skipped with an error log and the remaining
files are still processed:

```
[INFO] january.ofx → 47 inserted, 2 skipped (filtered), 0 errors
[ERROR] Skipped file: corrupt.ofx — XML parse error: mismatched tag at line 42
[INFO] february.ofx → 31 inserted, 1 skipped (filtered), 0 errors
[INFO] Total: 78 inserted, 3 skipped, 1 file error(s) across 3 file(s)
```

Exit code: `0` (partial success); the caller can check stderr for errors.

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `psycopg2.OperationalError` | DATABASE_URL wrong or DB unreachable | Check DSN and PostgreSQL status |
| `FileNotFoundError` / `NotADirectoryError` | Directory path incorrect | Check DATA_ROOT and argument |
| `0 rows inserted` on valid directory | All rows filtered or already loaded | Check that files have non-filtered transactions; check `transaction_hash` uniqueness |
| `xml.etree.ElementTree.ParseError` | OFX file has no valid XML body | Inspect the file manually for the `<OFX>` tag |

## Reference

- CLI contract: [contracts/cli-interface.md](contracts/cli-interface.md)
- Database schema: [contracts/database-schema.md](contracts/database-schema.md)
- Data model: [data-model.md](data-model.md)
