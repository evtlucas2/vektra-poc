# Contract: Daily Balance Schema

**Feature**: Calculate Daily Balance | **Date**: 2026-06-08

## Table: `daily_balance`

Created by migration `0004_create_daily_balance.sql`. Separate from `transactions`.

```sql
CREATE TABLE IF NOT EXISTS daily_balance (
    balance_date  DATE           PRIMARY KEY,
    day_of_week   SMALLINT       NOT NULL,
    weekend       SMALLINT       NOT NULL,
    balance       NUMERIC(15, 2) NOT NULL,
    difference    NUMERIC(15, 2) NOT NULL
);
```

## Column Descriptions

| Column | Nullable | Description |
|--------|----------|-------------|
| `balance_date` | NO | Calendar day; primary key — one row per day (global, all accounts) |
| `day_of_week` | NO | Python `weekday()`: 0=Monday … 6=Sunday |
| `weekend` | NO | 1 when `day_of_week` is 5 (Sat) or 6 (Sun), else 0 |
| `balance` | NO | Running balance at end of day |
| `difference` | NO | `balance` minus previous day's `balance`; 0 on the first day |

## Idempotency

Each run fully recomputes the series:

```sql
DELETE FROM daily_balance;
-- then INSERT one row per computed day
INSERT INTO daily_balance (balance_date, day_of_week, weekend, balance, difference)
VALUES (%s, %s, %s, %s, %s);
```

Delete-then-insert (within one transaction) guarantees the table reflects only the latest
computed series, with no stale rows if the transaction date range shrinks between runs.

## Relationship

`daily_balance` is derived from `transactions` (read-only). There is no foreign key — the
daily series is an aggregate keyed by date, not a per-transaction reference.
