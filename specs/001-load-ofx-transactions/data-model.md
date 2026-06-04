# Data Model: Load OFX Transactions

**Branch**: `001-load-ofx-transactions` | **Date**: 2026-06-04

## Entity: Transactions

Represents a single financial movement read from an OFX `<STMTTRN>` element and
persisted to the database.

### Fields

| Field | Type | Nullable | Source | Notes |
|-------|------|----------|--------|-------|
| `id` | integer (auto) | NO | database | Surrogate primary key |
| `posted_date` | date | NO | `DTPOSTED` | Posting date from OFX; first 8 chars (`YYYYMMDD`) |
| `effective_date` | date | YES | `MEMO` (derived) | Set when MEMO matches `DD/MM HH:MM desc`; year from `DTPOSTED` |
| `description` | text | YES | `MEMO` | Full MEMO when no pattern match; trailing text after `HH:MM` when matched |
| `amount` | numeric(15,2) | NO | `TRNAMT` | Positive = credit, negative = debit |
| `transaction_hash` | text | NO | computed | SHA-256 of (`posted_date` + `amount` + raw `MEMO` + `NAME`) |

### Constraints

- `PRIMARY KEY (id)`
- `UNIQUE (transaction_hash)` — idempotency key; enables `ON CONFLICT DO NOTHING`
- `NOT NULL` on `posted_date`, `amount`, `transaction_hash`

### Derived Field Rules

**`posted_date`**
- Source: `DTPOSTED` field in OFX
- Format: `YYYYMMDD` (first 8 characters; remainder is time and offset, ignored)
- Error: if parsing fails, skip the transaction and log the issue

**`effective_date`** (nullable)
- Condition: MEMO matches `^(\d{1,2}/\d{1,2})\s+\d{1,2}:\d{2}\s+(.+)$`
- When matched: combine `DD/MM` (from group 1) with year from `DTPOSTED[:4]`
  → store as `datetime.date`
- When not matched: `NULL`

**`description`** (nullable)
- When MEMO matches pattern: group 2 (text after `HH:MM `)
- When MEMO does not match: full raw MEMO value
- When MEMO is absent or blank: `NULL`

**`transaction_hash`**
- Input string: `f"{posted_date_str}|{amount_str}|{raw_memo}|{name}"`
- Algorithm: SHA-256, hex digest

### Filtered Transactions (not stored)

Transactions whose `NAME` field equals any value in this set are discarded before
any further processing:

```
{"Saldo do dia", "Saldo Anterior"}
```

---

## Python Dataclass Representation

```python
@dataclass
class Transaction:
    posted_date: date
    effective_date: date | None
    description: str | None
    amount: Decimal
    transaction_hash: str
```

---

---

## ETL Phase: Scan

Before extraction, a scan phase enumerates OFX files in the input directory:

```
scan(directory: Path) → list[Path]
```

- Returns a sorted list of `.ofx` files (case-insensitive match).
- Returns an empty list if the directory contains no matching files.
- An empty list triggers the no-op exit path in `cli.py`.

---

## OFX Source Mapping

| OFX Tag | Field Used |
|---------|-----------|
| `<DTPOSTED>` | `posted_date`, year for `effective_date` |
| `<TRNAMT>` | `amount` |
| `<NAME>` | filter check + hash input |
| `<MEMO>` | `description`, `effective_date` derivation, hash input |

Tags `<TRNTYPE>`, `<FITID>`, and others are read but not persisted in this version.
