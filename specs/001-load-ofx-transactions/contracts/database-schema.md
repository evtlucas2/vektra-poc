# Contract: Database Schema

**Feature**: Load OFX Transactions | **Date**: 2026-06-04

## Table: `transactions`

> **Schema is managed by yoyo-migrations** (added in feature 002). See `migrations/`
> for the full DDL history.

```sql
-- After migration 0003_effective_date_not_null (feature 003):
CREATE TABLE IF NOT EXISTS transactions (
    id               SERIAL PRIMARY KEY,
    posted_date      DATE           NOT NULL,
    effective_date   DATE           NOT NULL,
    description      TEXT,
    amount           NUMERIC(15, 2) NOT NULL,
    account_label    TEXT           NOT NULL DEFAULT 'unknown',
    transaction_hash TEXT           NOT NULL,
    CONSTRAINT uq_transaction_hash UNIQUE (transaction_hash)
);
```

## Column Descriptions

| Column | Nullable | Description |
|--------|----------|-------------|
| `id` | NO | Auto-incrementing surrogate key |
| `posted_date` | NO | Date the bank posted the transaction (from `DTPOSTED`) |
| `effective_date` | NO | Derived from MEMO pattern `DD/MM HH:MM` when present; otherwise equals `posted_date` (never null — feature 003) |
| `description` | YES | Transaction description; from MEMO (full or split) |
| `amount` | NO | Transaction amount; positive = credit, negative = debit |
| `account_label` | NO | User-supplied account identifier (added in feature 002); rows from feature 001 default to `'unknown'` |
| `transaction_hash` | NO | SHA-256 of source fields + account_label; unique — idempotency key |

## Idempotency

Re-loading the same OFX file uses:

```sql
INSERT INTO transactions (posted_date, effective_date, description, amount, transaction_hash)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (transaction_hash) DO NOTHING;
```

Duplicate rows are silently ignored; no error is raised.

## Index

The `UNIQUE` constraint on `transaction_hash` implicitly creates a B-tree index,
making conflict detection efficient even for large tables.

## Migration

The pipeline creates the table automatically on first run using `CREATE TABLE IF NOT
EXISTS`. No migration framework is required for this version.
