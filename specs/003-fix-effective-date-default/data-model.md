# Data Model: Fix Effective Date — Always Non-Null

**Branch**: `003-fix-effective-date-default` | **Date**: 2026-06-05

## Entity: Transaction (updated)

### Changed Field

| Field | Before | After | Notes |
|-------|--------|-------|-------|
| `effective_date` | `DATE NULL` | `DATE NOT NULL` | Defaults to `posted_date` when MEMO has no date |

All other fields are unchanged.

### Derivation Rule (updated)

**`effective_date`**

| Condition | Value |
|-----------|-------|
| MEMO matches `DD/MM HH:MM <text>` and date is valid | Derived date: `DD/MM/YYYY` (year from `DTPOSTED`) |
| MEMO matches pattern but derived date is invalid (e.g., `31/02`) | `posted_date` (with warning logged) |
| MEMO does not match pattern | `posted_date` |
| MEMO is blank or absent | `posted_date` |

### Python Dataclass (updated)

```python
@dataclass
class Transaction:
    posted_date: date
    effective_date: date          # was: date | None
    description: str | None
    amount: Decimal
    account_label: str
    transaction_hash: str
```

---

## Schema Migration History (updated)

| Migration | Operation |
|-----------|-----------|
| `0001_create_transactions.sql` | CREATE TABLE (feature 001) |
| `0002_add_account_label.sql` | ADD COLUMN account_label (feature 002) |
| `0003_effective_date_not_null.sql` | UPDATE nulls to posted_date; SET NOT NULL (this feature) |
