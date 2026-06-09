# Data Model: Calculate Daily Balance

**Branch**: `004-daily-balance` | **Date**: 2026-06-08

## Entity: DailyBalance (new)

One record per calendar day in the transaction date range.

### Fields

| Field | Type | Nullable | Source | Notes |
|-------|------|----------|--------|-------|
| `balance_date` | date | NO | `transactions.effective_date` (range) | Primary key; one row per day |
| `day_of_week` | smallint | NO | derived | Python `weekday()`: 0=Mon … 6=Sun |
| `weekend` | smallint | NO | derived | 1 when `day_of_week` ∈ {5, 6}, else 0 |
| `balance` | numeric(15,2) | NO | computed | Running balance at end of day |
| `difference` | numeric(15,2) | NO | computed | `balance` − previous day's `balance`; 0 on first day |

### Derivation Rules

**`balance_date`**: every calendar day from `min(effective_date)` to `max(effective_date)`
inclusive (gap-filled).

**`day_of_week`**: `balance_date.weekday()` (Monday=0 … Sunday=6).

**`weekend`**: `1 if day_of_week in {5, 6} else 0`.

**`balance`**:
- First day: `initial_balance + net_sum(first_day)`
- Subsequent day: `previous_balance + net_sum(day)`
- Day with no transactions: `net_sum = 0`, so `balance = previous_balance`

**`difference`**:
- First day: `0` (always, by definition — no previous day)
- Subsequent day: `balance − previous_balance` (equals that day's net sum; negative,
  zero, or positive)

where `net_sum(day) = SUM(transactions.amount WHERE effective_date = day)` across all
accounts.

### Python Dataclass

```python
@dataclass
class DailyBalance:
    balance_date: date
    day_of_week: int
    weekend: int
    balance: Decimal
    difference: Decimal
```

---

## Entity: Transaction (existing, read-only)

Read-only source for this feature. Only `effective_date` and `amount` are consumed.
`account_label` is intentionally ignored (global scope). Not modified by this feature.

---

## Schema Migration History (updated)

| Migration | Operation |
|-----------|-----------|
| `0001_create_transactions.sql` | CREATE TABLE transactions (feature 001) |
| `0002_add_account_label.sql` | ADD COLUMN account_label (feature 002) |
| `0003_effective_date_not_null.sql` | effective_date NOT NULL + backfill (feature 003) |
| `0004_create_daily_balance.sql` | CREATE TABLE daily_balance (this feature) |
