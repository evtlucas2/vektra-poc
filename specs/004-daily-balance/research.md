# Research: Calculate Daily Balance

**Branch**: `004-daily-balance` | **Date**: 2026-06-08

## Decision 1: New CLI Command via Package `__main__.py`

**Decision**: Add a new package `src/balance/` with a `__main__.py`, invoked as
`python -m src.balance <initial-balance>`. The existing loader (`python -m src.cli`)
is untouched.

**Rationale**: The user asked for a "new CLI command." A package with `__main__.py`
groups the balance ETL phases and exposes a clean, self-documenting invocation. It keeps
the two pipelines fully independent (Constitution Principle II) without a shared
sub-command dispatcher, which would add coupling for no benefit (Principle V).

**Alternatives considered**:
- `argparse` sub-commands on the existing `src/cli.py` (e.g. `cli load`, `cli balance`) —
  couples two unrelated pipelines behind one entry point; rejected for simplicity.
- A standalone `src/balance_cli.py` module — works, but a package better groups
  extract/compute/load for this pipeline.

---

## Decision 2: Day-of-Week and Weekend Convention

**Decision**: Use Python's `datetime.date.weekday()` directly: `0 = Monday … 6 = Sunday`.
Weekend is `1` when `weekday() in {5, 6}` (Saturday, Sunday), else `0`. Store
`WEEKEND_DAYS = frozenset({5, 6})` as a module constant.

**Rationale**: The updated spec (FR-009, FR-010) explicitly requires Python's default
`weekday()` convention, so no remapping is needed — `date.weekday()` returns the value
directly. A `frozenset` membership check is clean and O(1) (Principle IV).

**Note**: This replaces the earlier `strftime("%w")` (0=Sunday) approach considered in the
first spec draft; the spec was amended to Python's convention.

---

## Decision 3: Pure Compute Function for the Series

**Decision**: `compute_daily_balances(daily_net: dict[date, Decimal], initial_balance:
Decimal) -> list[DailyBalance]` is a pure function with no database access. The extract
phase produces `daily_net` (net amount per `effective_date`); compute gap-fills and builds
the running series.

Algorithm:

```
if daily_net is empty: return []
start, end = min(keys), max(keys)
prev = None
for d in each calendar day from start to end inclusive:
    net = daily_net.get(d, 0)
    if prev is None:                      # first day
        balance = initial_balance + net
        difference = 0
    else:
        balance = prev + net
        difference = balance - prev       # equals net for non-first days
    emit DailyBalance(d, d.weekday(), weekend_flag(d), balance, difference)
    prev = balance
```

**Rationale**: Isolating the math in a pure function makes the trickiest logic (gap-fill,
first-day difference = 0, running balance) trivially unit-testable without a database
(Principle III). Days with no transactions naturally get `net = 0`, so `balance = prev`
and `difference = 0`, satisfying FR-008 and SC-004.

**Edge note**: For the first day, `difference` is `0` by definition even though
`balance = initial + net` (FR-012). For all later days `difference == net`, but it is
computed as `balance - prev` to follow the spec's definition literally.

---

## Decision 4: Aggregation Query (Extract)

**Decision**:

```sql
SELECT effective_date, SUM(amount)
FROM transactions
GROUP BY effective_date
ORDER BY effective_date;
```

Returns one net amount per date across **all** accounts (global scope, per clarification).
`extract` returns a `dict[date, Decimal]`.

**Rationale**: A single grouped query pushes aggregation to the database — efficient and
simple. `account_label` is intentionally not in the GROUP BY (global scope, FR-004).

---

## Decision 5: Idempotent Persistence (Load)

**Decision**: `replace_daily_balances(conn, rows)` runs `DELETE FROM daily_balance;` then
inserts all computed rows, within a single transaction (commit once at the end).

**Rationale**: The series is fully recomputed each run and the initial balance can change
between runs, so the simplest correct way to "reflect the latest computed series" (FR-013)
is delete-all-then-insert. An upsert keyed on date would leave stale rows if the
transaction date range shrank between runs.

**Alternatives considered**:
- `INSERT ... ON CONFLICT (balance_date) DO UPDATE` — does not remove dates that fall out
  of a shrunken range; rejected.
- `TRUNCATE` — faster but heavier (table locks, resets identity); `DELETE` is sufficient
  at this scale (Principle V).

---

## Decision 6: Empty-Transactions Behavior

**Decision**: The CLI checks the aggregation result; if there are no transactions, it
prints `[INFO] No transactions found. Nothing to do.` and exits `0` **without** touching
the `daily_balance` table (FR-014).

**Rationale**: With no transactions there is no date range and no series to produce. Not
modifying the table avoids surprising deletion of a prior series when the command is run
against an empty/unloaded database.

---

## Decision 7: Schema Migration

**Decision**: New migration `migrations/0004_create_daily_balance.sql` creates the
`daily_balance` table with `balance_date DATE PRIMARY KEY`. Applied via the existing
`apply_migrations(database_url)` at command startup.

**Rationale**: Consistent with features 002/003 — yoyo is the single schema owner. Date as
primary key enforces one row per day (global scope) and supports the delete+insert cycle.
