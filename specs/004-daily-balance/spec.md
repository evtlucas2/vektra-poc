# Feature Specification: Calculate Daily Balance

**Feature Branch**: `004-daily-balance`

**Created**: 2026-06-08

**Status**: Draft (updated 2026-06-08 — add daily difference field; switch weekday convention to Python default)

**Input**: Calculate a running daily balance from stored transactions and persist it to a
dedicated table separate from `transactions`. The user supplies an initial balance on the
command line. For each calendar day, the balance is the previous day's balance (or the
initial balance on the first day) plus the net sum of that day's transaction amounts
(positive = income, negative = expense). Each daily record also stores: the day of week
(following Python's default `weekday()` convention — 0 = Monday … 6 = Sunday); a weekend
flag (1 when the day is Saturday or Sunday, otherwise 0); and a difference field holding the
change from the previous day's balance to the current day's balance (0 for the first day).
Days with no transactions carry forward the previous day's balance. The balance is computed
across **all** transactions regardless of account.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate Daily Balance Series (Priority: P1)

A user has loaded transactions into the database. They run the daily-balance calculation
with a starting balance (e.g. `1000.00`). The system reads every transaction, groups the
amounts by their `effective_date`, and produces one row per calendar day from the earliest
to the latest transaction date. Each row records the date, day of week, weekend flag, the
running balance, and the difference from the previous day's balance. The user can then query
the daily-balance table to see how the balance evolved over time and how much it changed each
day.

**Why this priority**: This is the entire feature — without the generated series there is
no value to deliver.

**Independent Test**: Load a known set of transactions, run the calculation with a known
initial balance, and verify each day's balance equals the previous day's balance plus that
day's net transaction sum, with correct day-of-week, weekend, and difference values.

**Acceptance Scenarios**:

1. **Given** transactions exist with effective dates spanning several days and an initial
   balance of `1000.00`, **When** the calculation runs, **Then** the first day's balance
   equals `1000.00` plus the net sum of that first day's transactions, and the first day's
   difference is `0`.

2. **Given** a day that has both incomes (positive amounts) and expenses (negative amounts),
   **When** the calculation runs, **Then** that day's balance equals the previous day's
   balance plus the net of all that day's amounts, and that day's difference equals the
   current day's balance minus the previous day's balance.

3. **Given** a calendar day within the date range that has no transactions, **When** the
   calculation runs, **Then** a row is still produced for that day with a balance equal to
   the previous day's balance and a difference of `0`.

4. **Given** any generated daily row, **When** inspected, **Then** `day_of_week` is `0` for
   Monday through `6` for Sunday, and `weekend` is `1` when `day_of_week` is `5` (Saturday)
   or `6` (Sunday) and `0` otherwise.

5. **Given** a day whose net transactions are negative (expenses exceed incomes), **When**
   the calculation runs, **Then** that day's difference is a negative value; for a day whose
   net is positive, the difference is positive.

6. **Given** the calculation has already been run, **When** it is run again with the same
   inputs, **Then** the daily-balance table reflects the same result without duplicate rows.

---

### Edge Cases

- What happens when there are no transactions at all?
  → No daily-balance rows are produced; the operation completes with an informational
  message.
- What happens when all transactions fall on a single day?
  → Exactly one daily-balance row is produced; its difference is `0` (it is the first day).
- What happens if the initial balance is negative or zero?
  → It is accepted as-is; the running balance is computed normally and may be negative.
- What happens when the initial balance is missing from the command line?
  → The operation stops with a clear error and produces no rows.
- How is the difference computed for the first day?
  → It is always `0`, regardless of that day's transactions, because there is no previous
  day to compare against.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept an initial balance value supplied on the command line
  and use it as the starting point for the first day's calculation.
- **FR-002**: The system MUST persist daily balance records to a table that is separate from
  the `transactions` table.
- **FR-003**: The system MUST derive each daily record's date from the `effective_date`
  field of the `transactions` table.
- **FR-004**: The system MUST aggregate transaction amounts by `effective_date` across **all**
  transactions, regardless of account, treating positive amounts as income and negative
  amounts as expense.
- **FR-005**: The system MUST produce one daily record for every calendar day from the
  earliest to the latest `effective_date` present in the transactions, inclusive — including
  days that have no transactions.
- **FR-006**: For the first day in the range, the system MUST compute the balance as the
  initial balance plus the net sum of that day's transaction amounts.
- **FR-007**: For every subsequent day, the system MUST compute the balance as the previous
  day's balance plus the net sum of that day's transaction amounts.
- **FR-008**: For a day with no transactions, the system MUST store that day with a balance
  equal to the previous day's balance.
- **FR-009**: The system MUST store a `day_of_week` value for each record following Python's
  default `weekday()` convention, where `0` represents Monday and `6` represents Sunday.
- **FR-010**: The system MUST store a `weekend` flag for each record set to `1` when
  `day_of_week` is `5` (Saturday) or `6` (Sunday), and `0` otherwise.
- **FR-011**: The system MUST store a `difference` value for each record representing the
  change from the previous day's balance to the current day's balance (current day's balance
  minus previous day's balance).
- **FR-012**: For the first day in the range, the system MUST set `difference` to `0`. For
  subsequent days, `difference` MAY be negative, zero, or positive.
- **FR-013**: Re-running the calculation MUST NOT create duplicate daily records for the same
  date; the table MUST reflect the latest computed series.
- **FR-014**: When no transactions exist, the system MUST complete without error and produce
  no daily records.

### Key Entities *(include if feature involves data)*

- **Daily Balance**: One record per calendar day in the transaction date range. Attributes:
  `date` (the calendar day, sourced from transaction `effective_date`), `day_of_week`
  (0 = Monday … 6 = Sunday, Python `weekday()` convention), `weekend` (1 for Saturday/Sunday,
  else 0), `balance` (the running balance at the end of that day), and `difference` (the
  current day's balance minus the previous day's balance; 0 for the first day). One record
  per distinct date.
- **Transaction** (existing, read-only here): Source of `effective_date` and `amount`. Not
  modified by this feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After running the calculation, the daily-balance table contains exactly one row
  for every calendar day between the earliest and latest transaction `effective_date`,
  inclusive.
- **SC-002**: Each day's stored balance equals the previous day's balance (or the initial
  balance for the first day) plus the net sum of that day's transaction amounts — verifiable
  by independent recomputation.
- **SC-003**: Every row's `day_of_week` correctly maps to the calendar date (0 = Monday … 6 =
  Sunday) and `weekend` is `1` exactly when `day_of_week` is `5` or `6`.
- **SC-004**: Days within the range that have no transactions appear with a balance identical
  to the prior day's balance and a difference of `0`.
- **SC-005**: Each row's `difference` equals that day's balance minus the prior day's balance,
  and the first day's difference is `0` — verifiable by independent recomputation.
- **SC-006**: Running the calculation twice with the same inputs yields the same set of rows
  with no duplicates.

## Assumptions

- The daily balance is computed across all transactions in the table; account is not a factor
  (confirmed: global scope).
- The `difference` field is defined as current day's balance minus previous day's balance, so
  a net-expense day yields a negative value and a net-income day yields a positive value.
- The first day's `difference` is always `0` by definition, even if that day had transactions,
  because there is no previous day to compare against.
- The date range is continuous and gap-filled: every calendar day from the first to the last
  transaction `effective_date` gets a row, even if no transactions occurred that day.
- The initial balance applies to the first day of the range only; it is not itself stored as
  a separate "day zero" row.
- The calculation reads already-loaded transactions; loading OFX files is a prerequisite
  handled by the existing pipeline and is out of scope here.
- Re-running the calculation replaces the prior series rather than appending to it, so the
  table always reflects the most recent computation.
- The initial balance is a monetary value that may be negative, zero, or positive.
- This calculation is a separate command/operation from the transaction loader.
