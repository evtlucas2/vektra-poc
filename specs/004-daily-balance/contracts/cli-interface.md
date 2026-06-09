# Contract: Daily Balance CLI

**Feature**: Calculate Daily Balance | **Date**: 2026-06-08

## Command

```
python -m src.balance <initial-balance>
```

This is a **new, separate command** from the OFX loader (`python -m src.cli`).

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `<initial-balance>` | YES | Starting balance for the first day. A decimal number; may be negative, zero, or positive (e.g. `1000.00`, `-50.5`, `0`). |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | YES | PostgreSQL DSN (same as the loader). Loaded from `config/.env`. |

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success (series written, or no transactions found — a valid no-op) |
| `1` | Fatal error: missing/invalid initial balance, or database unreachable |

## Standard Output

```
[INFO] Daily balance: 92 day(s) written from 2026-01-05 to 2026-04-06 (initial 1000.00)
```

No-transactions case:

```
[INFO] No transactions found. Nothing to do.
```

## Standard Error

```
[ERROR] Initial balance must be a valid number.
[ERROR] Usage: python -m src.balance <initial-balance>
```

## Behavior

1. Load `config/.env`, read `DATABASE_URL`.
2. Validate `<initial-balance>` parses as a decimal; else exit 1.
3. Apply migrations (ensures `daily_balance` table exists).
4. Aggregate `transactions` net amount per `effective_date` (all accounts).
5. If no transactions: print info, exit 0 (table untouched).
6. Compute the gap-filled daily series.
7. Replace the `daily_balance` table contents (delete all, insert series).
8. Print summary, exit 0.

## Examples

```bash
# Compute series with starting balance 1000.00
python -m src.balance 1000.00

# Negative starting balance is allowed
python -m src.balance -250.75

# Missing argument
python -m src.balance
# stderr: [ERROR] Usage: python -m src.balance <initial-balance>
# exit code: 1
```
