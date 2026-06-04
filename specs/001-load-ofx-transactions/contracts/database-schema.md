# Contract: Database Schema

**Feature**: Load OFX Transactions | **Date**: 2026-06-04

## Table: `transactions`

```sql
CREATE TABLE IF NOT EXISTS transactions (
    id               SERIAL PRIMARY KEY,
    posted_date      DATE           NOT NULL,
    effective_date   DATE,
    description      TEXT,
    amount           NUMERIC(15, 2) NOT NULL,
    transaction_hash TEXT           NOT NULL,
    CONSTRAINT uq_transaction_hash UNIQUE (transaction_hash)
);
```

## Column Descriptions

| Column | Nullable | Description |
|--------|----------|-------------|
| `id` | NO | Auto-incrementing surrogate key |
| `posted_date` | NO | Date the bank posted the transaction (from `DTPOSTED`) |
| `effective_date` | YES | Derived date from MEMO pattern `DD/MM HH:MM`; null when pattern not matched |
| `description` | YES | Transaction description; from MEMO (full or split) |
| `amount` | NO | Transaction amount; positive = credit, negative = debit |
| `transaction_hash` | NO | SHA-256 of source fields; unique — idempotency key |

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
