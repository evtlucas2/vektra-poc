# Feature Specification: Add Account Label to Transactions

**Feature Branch**: `002-add-account-label`

**Created**: 2026-06-05

**Status**: Draft

**Input**: Each OFX directory represents a single bank account. When loading transactions,
the user provides a label identifying that account. Every transaction stored in the
database from that directory is tagged with the account label, and the label is included
in the transaction's unique identifier so that the same transaction amounts/dates from
different accounts are never mistakenly treated as duplicates.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Load Transactions Tagged with Account Label (Priority: P1)

A user has two directories of OFX files — one for their checking account and one for
their savings account. When running the pipeline, the user supplies a label for the
account (e.g. `"checking"` or `"savings"`). Every transaction loaded from that directory
is stored with that label. The user can then query the database to see which account each
transaction belongs to.

**Why this priority**: Without the account label, all transactions are anonymous — the
user cannot distinguish which account they came from, making multi-account analysis
impossible.

**Independent Test**: Load the same OFX directory twice — once with label `"checking"`
and once with label `"savings"`. Query the database and confirm: (a) both runs inserted
rows, (b) each row has the correct account label, (c) rows from the two runs are distinct
(no duplicate-rejection between accounts).

**Acceptance Scenarios**:

1. **Given** a directory of OFX files and the label `"checking"`, **When** the pipeline
   runs, **Then** every inserted row has `account_label = "checking"`.

2. **Given** the same directory and the label `"savings"`, **When** the pipeline runs,
   **Then** every inserted row has `account_label = "savings"`, and the rows from the
   first run (label `"checking"`) are still present and unaffected.

3. **Given** two transactions with identical date, amount, and MEMO but different account
   labels, **When** both are loaded, **Then** both are stored as separate rows (account
   label is part of the unique identifier).

---

### User Story 2 - Idempotent Reload with Account Label (Priority: P2)

A user re-runs the pipeline against the same directory with the same account label. No
duplicate rows are inserted.

**Why this priority**: Re-runs must remain safe; the account label must be part of the
de-duplication key so idempotency still works correctly.

**Independent Test**: Run the pipeline twice with the same directory and the same label.
Confirm the row count after the second run equals the row count after the first run.

**Acceptance Scenarios**:

1. **Given** the pipeline has already loaded a directory with label `"checking"`,
   **When** the same directory is loaded again with label `"checking"`, **Then** no
   duplicate rows are inserted.

---

### Edge Cases

- What happens if the user provides an empty label?
  → Pipeline rejects the input with a clear error message; no rows are inserted.
- What happens if the label contains special characters (spaces, slashes)?
  → The label is stored as-is; leading/trailing whitespace is trimmed before use.
- What happens if two different users accidentally use the same label for different
  accounts?
  → The system has no way to detect this; correct labelling is the user's responsibility.
  This is documented in assumptions.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The pipeline MUST accept an account label as a required input parameter
  alongside the OFX directory path.
- **FR-002**: The account label MUST be stored as a non-null field on every transaction
  row inserted during that pipeline run.
- **FR-003**: The account label MUST be included in the transaction's unique identifier
  so that the same source data loaded under different labels produces distinct rows.
- **FR-004**: The pipeline MUST reject an empty or whitespace-only account label with
  a clear error message and exit without inserting any rows.
- **FR-005**: The account label MUST be trimmed of leading and trailing whitespace before
  use and before storage.
- **FR-006**: Existing rows already in the database MUST NOT be modified when a new load
  is performed under a different account label.

### Key Entities *(include if feature involves data)*

- **Transaction** (updated): Gains a new required field `account_label` — a short,
  user-defined string identifying the bank account the transaction belongs to.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every transaction row in the database has a non-null, non-empty
  `account_label` value after a pipeline run.
- **SC-002**: Loading the same OFX directory under two different labels produces two
  distinct sets of rows — one per label — with no cross-contamination.
- **SC-003**: Re-running the pipeline with the same directory and the same label inserts
  zero additional rows (idempotency preserved).
- **SC-004**: Attempting to run the pipeline without providing an account label results
  in an immediate error with a descriptive message, and zero rows are inserted.

## Assumptions

- The account label is a free-form, user-defined string (no fixed vocabulary or
  validation beyond non-empty).
- The label is supplied as a CLI argument (or equivalent input mechanism); it is not
  derived automatically from the directory name or file content.
- Correct and consistent labelling across runs is the user's responsibility; the system
  does not enforce uniqueness of labels across accounts.
- This feature extends the existing OFX-to-database pipeline; all other pipeline
  behaviour (filtering, MEMO splitting, idempotency, empty-directory handling) remains
  unchanged.
- The `account_label` column is added to the existing `transactions` table; no separate
  account registry table is required for this version.
