# Contract: CLI Interface (updated)

**Feature**: Add Account Label | **Date**: 2026-06-05

## Command

```
python -m src.cli <ofx-directory> <account-label>
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `<ofx-directory>` | YES | Path to directory containing `.ofx` files (as before) |
| `<account-label>` | YES | Short string identifying the bank account. Trimmed of whitespace. Must be non-empty after trimming. |

## Environment Variables

Unchanged from feature 001 (`DATABASE_URL`, `DATA_ROOT`).

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success (zero or more rows inserted, including empty-directory case) |
| `1` | Fatal error: missing argument, empty label, directory not found, DB unreachable |

## Standard Output (updated)

Per-file summary now shows account label:

```
[INFO] january.ofx → 47 inserted, 2 skipped (filtered), 0 errors  [account: checking]
[INFO] february.ofx → 31 inserted, 1 skipped (filtered), 0 errors  [account: checking]
[INFO] Total: 78 inserted, 3 skipped, 0 errors across 2 file(s)  [account: checking]
```

Empty-directory case:

```
[INFO] No OFX files found in /data/raw/statements. Nothing to do.
```

## Validation

The label is validated **before** any database connection is attempted:

```
[ERROR] Account label must not be empty.
```

## Examples

```bash
# Load checking account directory
python -m src.cli /data/raw/checking/ checking

# Load savings account directory
python -m src.cli /data/raw/savings/ savings

# Same OFX directory, two accounts — both runs succeed, no duplicates within each
python -m src.cli /data/raw/shared/ account-a
python -m src.cli /data/raw/shared/ account-b

# Missing label → error, no DB connection
python -m src.cli /data/raw/checking/
# stderr: [ERROR] Account label must not be empty.
# exit code: 1
```
