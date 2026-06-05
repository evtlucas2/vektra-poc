# Feature Specification: Fix Effective Date — Always Non-Null

**Feature Branch**: `003-fix-effective-date-default`

**Created**: 2026-06-05

**Status**: Draft

**Input**: The `effective_date` field on every stored transaction must never be null.
When the MEMO tag contains a date pattern (`DD/MM HH:MM description`), `effective_date`
is already derived from that pattern. When the MEMO tag does not match the pattern —
or is absent — `effective_date` must fall back to the transaction's posting date
(`posted_date`). This eliminates null values in the field and makes date-based
queries and analysis reliable for all transactions.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Every Transaction Has an Effective Date (Priority: P1)

A user queries the transactions table and needs to filter or sort by effective date.
After this change, every row has a non-null `effective_date`, regardless of whether the
MEMO contained a parseable date. Transactions without a MEMO date use the posting date
as their effective date.

**Why this priority**: Null values in a date field make range queries and reporting
unreliable. A guaranteed non-null fallback makes the field trustworthy for all use
cases.

**Independent Test**: Load an OFX file containing transactions with and without the
MEMO date pattern. Query the database and confirm: (a) zero rows have a null
`effective_date`, (b) rows with a MEMO date have the derived effective date, (c) rows
without a MEMO date have `effective_date = posted_date`.

**Acceptance Scenarios**:

1. **Given** a transaction whose MEMO matches `DD/MM HH:MM description`,
   **When** it is loaded, **Then** `effective_date` is the date derived from the
   MEMO pattern (day/month from MEMO + year from `DTPOSTED`).

2. **Given** a transaction whose MEMO does not match the date pattern,
   **When** it is loaded, **Then** `effective_date` equals `posted_date`.

3. **Given** a transaction with a blank or absent MEMO,
   **When** it is loaded, **Then** `effective_date` equals `posted_date`.

4. **Given** the database already contains rows with `effective_date = null`
   (loaded before this fix), **When** the schema migration runs, **Then** those
   existing null values are backfilled with the corresponding `posted_date`.

---

### Edge Cases

- What if `posted_date` itself is malformed?
  → The row is skipped and logged (existing behavior, unchanged).
- What if the MEMO date pattern produces an invalid date (e.g., `31/02`)?
  → The row falls back to `effective_date = posted_date` and a warning is logged;
  the pipeline does not crash.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every transaction stored in the database MUST have a non-null
  `effective_date`.
- **FR-002**: When the MEMO tag matches the pattern `DD/MM HH:MM description`,
  `effective_date` MUST be set to the date derived from that pattern (unchanged
  from current behavior).
- **FR-003**: When the MEMO tag does not match the pattern, or is blank/absent,
  `effective_date` MUST be set equal to `posted_date`.
- **FR-004**: If the MEMO date pattern produces an invalid calendar date,
  `effective_date` MUST fall back to `posted_date` and a warning MUST be logged.
- **FR-005**: The database schema MUST enforce the NOT NULL constraint on
  `effective_date`. Existing null rows MUST be backfilled with `posted_date` as
  part of the migration.

### Key Entities *(include if feature involves data)*

- **Transaction** (updated): `effective_date` changes from nullable to required
  (non-null). When no MEMO date is present, `effective_date = posted_date`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After loading any valid OFX file, zero rows in the transactions table
  have a null `effective_date`.
- **SC-002**: Transactions with a MEMO date pattern retain the correct derived
  effective date (no regression).
- **SC-003**: Transactions without a MEMO date pattern have `effective_date` equal
  to `posted_date` — verifiable by querying and comparing the two columns.
- **SC-004**: The schema migration successfully backfills all existing null
  `effective_date` values with the corresponding `posted_date` before enforcing
  the NOT NULL constraint.

## Assumptions

- This change applies to all new transactions loaded after this fix is deployed;
  existing null rows are handled by the schema migration (backfill then NOT NULL).
- The fallback `effective_date = posted_date` applies only when the MEMO date
  pattern is absent or invalid — it does not overwrite a successfully derived date.
- The behavior of all other fields (`description`, `amount`, `account_label`, etc.)
  is unchanged.
- This feature does not require re-processing previously loaded OFX files; the
  backfill migration covers existing data.
