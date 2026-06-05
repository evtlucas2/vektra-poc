# Data Model: Add Account Label to Transactions

**Branch**: `002-add-account-label` | **Date**: 2026-06-05

## Entity: Transaction (updated)

### Fields

| Field | Type | Nullable | Change | Notes |
|-------|------|----------|--------|-------|
| `id` | integer (auto) | NO | unchanged | Surrogate primary key |
| `posted_date` | date | NO | unchanged | From `DTPOSTED` |
| `effective_date` | date | YES | unchanged | Derived from MEMO pattern |
| `description` | text | YES | unchanged | Full MEMO or split text |
| `amount` | numeric(15,2) | NO | unchanged | From `TRNAMT` |
| `account_label` | text | NO | **NEW** | User-supplied account identifier |
| `transaction_hash` | text | NO | **UPDATED** | SHA-256 now includes `account_label` |

### Updated Hash Input

```
f"{dtposted}|{trnamt}|{memo}|{name}|{account_label}"
```

The `account_label` is appended to the existing hash fields so that the same source
transaction loaded under two different labels produces two distinct hashes and two
distinct rows.

### Constraints (updated)

- `PRIMARY KEY (id)` — unchanged
- `UNIQUE (transaction_hash)` — unchanged; hash now encodes account_label

---

## Python Dataclass (updated)

```python
@dataclass
class Transaction:
    posted_date: date
    effective_date: date | None
    description: str | None
    amount: Decimal
    account_label: str          # NEW
    transaction_hash: str
```

---

## Schema Migration History

| Migration | Operation |
|-----------|-----------|
| `0001_create_transactions.sql` | `CREATE TABLE IF NOT EXISTS transactions (...)` — original 6-column schema |
| `0002_add_account_label.sql` | `ALTER TABLE transactions ADD COLUMN IF NOT EXISTS account_label TEXT NOT NULL DEFAULT 'unknown'` |

Existing rows (loaded before this feature) receive `account_label = 'unknown'` via
the migration DEFAULT. Their stored `transaction_hash` values do not include
`account_label` — they remain valid as unique keys for future re-loads under label
`'unknown'`.

---

## transform_transactions() signature change

```python
def transform_transactions(raw: list[dict], account_label: str) -> list[Transaction]:
    ...
```

The `account_label` parameter is required and is passed through to every `Transaction`
constructed in the function.
