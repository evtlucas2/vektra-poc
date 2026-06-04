# Contract: CLI Interface

**Feature**: Load OFX Transactions | **Date**: 2026-06-04 (updated for directory input)

## Command

```
python -m src.cli <ofx-directory>
```

Or via installed entry point (if configured):

```
load-ofx <ofx-directory>
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `<ofx-directory>` | YES | Path to a directory containing `.ofx` files. May be absolute or relative to `DATA_ROOT`. May be empty (zero files) — this is a valid no-op. |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | YES | PostgreSQL DSN. Example: `postgresql://user:pass@localhost:5432/mydb` |
| `DATA_ROOT` | NO | Base directory for resolving a relative `<ofx-directory>` argument. Defaults to current working directory. |

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Pipeline completed successfully (zero or more rows inserted, including empty-directory case) |
| `1` | Fatal error: directory not found, database unreachable, or unrecoverable failure |

## Standard Output

Progress and summary messages are written to stdout, one line per file plus a final total:

```
[INFO] No OFX files found in /data/raw/statements. Nothing to do.
```

```
[INFO] january.ofx → 47 inserted, 2 skipped (filtered), 0 errors
[INFO] february.ofx → 31 inserted, 1 skipped (filtered), 0 errors
[INFO] Total: 78 inserted, 3 skipped, 0 errors across 2 file(s)
```

## Standard Error

Per-row and per-file warnings/errors are written to stderr:

```
[WARN] Skipped row: malformed DTPOSTED "2024ABC01" in january.ofx at index 5
[WARN] Skipped row: filtered name "Saldo do dia" in january.ofx at index 8
[ERROR] Skipped file: march.ofx — XML parse error: mismatched tag at line 42
```

A file-level error does not stop processing of subsequent files.

## Examples

```bash
# Basic usage — directory with OFX files
DATABASE_URL="postgresql://user:pass@localhost/mydb" \
  python -m src.cli /data/raw/statements/

# With DATA_ROOT (resolves relative path)
DATA_ROOT=/data/raw \
DATABASE_URL="postgresql://user:pass@localhost/mydb" \
  python -m src.cli statements/

# Empty directory — valid no-op
DATABASE_URL="postgresql://user:pass@localhost/mydb" \
  python -m src.cli /data/raw/empty_dir/
# Output: [INFO] No OFX files found in /data/raw/empty_dir. Nothing to do.

# Using a .env file (loaded automatically at startup)
python -m src.cli statements/
```
