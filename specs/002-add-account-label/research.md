# Research: Add Account Label to Transactions

**Branch**: `002-add-account-label` | **Date**: 2026-06-05

## Decision 1: yoyo-migrations Integration

**Decision**: Use `yoyo-migrations` (v9.0) to manage all schema DDL. The CLI calls
`apply_migrations(database_url)` at startup via `src/db/migrations.py`, which runs
any unapplied migrations in `migrations/` before the ETL loop starts.

**API**:
```python
from yoyo import read_migrations, get_backend

def apply_migrations(database_url: str) -> None:
    backend = get_backend(database_url)
    migrations = read_migrations(str(MIGRATIONS_DIR))
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))
```

`MIGRATIONS_DIR` is resolved relative to the project root
(`Path(__file__).parent.parent.parent / "migrations"`).

yoyo tracks applied migrations in a `_yoyo_migration` table it creates automatically.

**Rationale**: Replaces the ad-hoc `create_table_if_not_exists()` function in
`load.py` with a version-controlled, auditable schema history. Adding future columns
or indexes requires only a new numbered SQL file — no Python code changes.

**Migration file format**: Plain SQL with an optional `-- depends:` header line.
yoyo applies files in lexicographic order by filename.

**Alternatives considered**:
- Alembic — powerful but complex; requires a model layer and env.py scaffold; overkill
  for a simple two-table schema (Principle V).
- Flyway — JVM-based; not Python-native.
- Manual `CREATE TABLE IF NOT EXISTS` — already in place; does not support alter
  operations or rollback tracking.

---

## Decision 2: Migration File Layout

**Decision**: Two migration files at project root `migrations/`:

| File | Content |
|------|---------|
| `0001_create_transactions.sql` | `CREATE TABLE IF NOT EXISTS transactions (...)` — baseline |
| `0002_add_account_label.sql` | `ALTER TABLE transactions ADD COLUMN IF NOT EXISTS account_label TEXT NOT NULL DEFAULT 'unknown'` |

The `DEFAULT 'unknown'` on migration `0002` handles rows loaded before this feature
existed; they receive a sentinel label rather than causing a NOT NULL constraint
violation.

**Rationale**: Separating baseline from amendment keeps each migration small and
independently reviewable. `IF NOT EXISTS` / `IF NOT EXISTS` guards make both
migrations idempotent if run against a fresh database.

---

## Decision 3: account_label in Hash

**Decision**: Include `account_label` in the SHA-256 hash input:
```
f"{dtposted}|{trnamt}|{memo}|{name}|{account_label}"
```

**Rationale**: Satisfies FR-003 — same source data under different labels produces
distinct hashes, allowing a transaction to be stored once per account. Without this,
the same OFX file loaded for two accounts would silently skip the second load (all
hashes conflict).

**Backward compatibility**: Rows inserted by feature 001 used a hash without
`account_label`. Those rows are unaffected — their stored hashes remain valid for
de-duplication against future re-loads of the same data under label `'unknown'`
(the default applied by migration 0002).

---

## Decision 4: CLI Argument for Label

**Decision**: Second positional argument: `python -m src.cli <ofx-directory> <label>`.

**Validation**: Label is stripped of whitespace; if the result is empty, exit with
code 1 and print `[ERROR] Account label must not be empty.` to stderr before any
database connection is made.

**Rationale**: Positional arguments keep the command concise for a two-argument CLI.
A named flag (`--label`) is equivalent but adds visual noise for a required argument.
Validation before DB connection avoids partial-state issues.

**Alternatives considered**:
- `--label <value>` named flag — equally valid; chosen positional for brevity.
- Environment variable `ACCOUNT_LABEL` — less ergonomic; label is per-run, not
  per-environment.

---

## Decision 5: Removal of create_table_if_not_exists()

**Decision**: Remove `create_table_if_not_exists()` from `src/etl/load.py`. Schema
setup is now entirely handled by `apply_migrations()`. The CLI calls
`apply_migrations()` once at startup before the ETL loop.

**Rationale**: Two code paths managing schema DDL violate Principle V. yoyo is now
the single source of truth for schema.

**Impact on tests**: `test_load.py` test `test_create_table_if_not_exists_executes_ddl`
is removed. Integration tests mock the migration call or run against a real DB where
yoyo has already applied migrations.
