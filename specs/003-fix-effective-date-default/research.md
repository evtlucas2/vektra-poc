# Research: Fix Effective Date — Always Non-Null

**Branch**: `003-fix-effective-date-default` | **Date**: 2026-06-05

## Decision 1: Migration Strategy for NOT NULL Backfill

**Decision**: Two-statement migration in a single SQL file:

```sql
-- Step 1: backfill existing nulls
UPDATE transactions
SET effective_date = posted_date
WHERE effective_date IS NULL;

-- Step 2: enforce NOT NULL
ALTER TABLE transactions
    ALTER COLUMN effective_date SET NOT NULL;
```

**Rationale**: PostgreSQL requires that no null values exist before `SET NOT NULL`
can succeed. Combining both statements in one migration file keeps the change atomic
within a single yoyo migration (yoyo wraps each migration in a transaction by default).
If either statement fails, the whole migration rolls back.

**Alternatives considered**:
- Two separate migration files (`0003` for backfill, `0004` for NOT NULL) — unnecessarily
  splits what is logically one operation; risks leaving the DB in an inconsistent state
  if the second migration is not applied promptly.
- `ALTER COLUMN ... SET NOT NULL` with a `DEFAULT posted_date` inline expression —
  PostgreSQL does not support expressions as column defaults that reference other
  columns; not possible.

---

## Decision 2: Transform Fallback Logic

**Decision**: In `_transform_row()`, replace:

```python
effective_date = _parse_effective_date(...) if match else None
```

with:

```python
if match:
    try:
        effective_date = _parse_effective_date(match.group(1), posted_date.year)
    except (ValueError, OverflowError):
        print(f"[WARN] Invalid MEMO date in row {row}, using posted_date", flush=True)
        effective_date = posted_date
else:
    effective_date = posted_date
```

**Rationale**: Satisfies FR-003 (fallback to `posted_date`) and FR-004 (invalid date
falls back with a warning). The guard for `ValueError`/`OverflowError` covers dates
like `31/02` that pass the regex but are not valid calendar dates.

---

## Decision 3: Transaction Dataclass Type Change

**Decision**: Change `effective_date: date | None` to `effective_date: date` in
`src/models/transaction.py`.

**Rationale**: With the fallback now guaranteed, `None` is no longer a valid value.
Removing the `None` type makes the contract explicit and prevents callers from needing
null-guards. All existing test fixtures that passed `effective_date=None` must be
updated to pass a `date` value.

**Impact on tests**: Any test in `test_transaction.py` or `test_transform.py` that
asserts `effective_date is None` must be updated to assert
`effective_date == posted_date`.
