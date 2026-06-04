# Feature Specification: Load OFX Transactions

**Feature Branch**: `001-load-ofx-transactions`

**Created**: 2026-06-04

**Status**: Draft (updated 2026-06-04 — batch directory input)

**Input**: Load bank transactions from a directory containing zero or more OFX files
into a relational database. Each OFX file is processed sequentially. When the directory
is empty, the pipeline exits cleanly without error.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Load OFX Directory into Database (Priority: P1)

A user points the ETL pipeline at a directory that holds one or more OFX files exported
from their bank. The pipeline discovers every OFX file in that directory, processes each
one in turn, and persists all valid transactions into the database. After the run, the
user can query the table and see every transaction from every file — each with its
posting date, description, and amount.

**Why this priority**: Core value of the feature — without a successful load, nothing
else works.

**Independent Test**: Run the pipeline against a directory containing two sample OFX
files with known transactions. Query the database and confirm: (a) the total row count
matches the combined non-filtered transactions across both files, (b) each row has the
correct date, description, and amount.

**Acceptance Scenarios**:

1. **Given** a directory with 1 OFX file containing 10 transactions (none filtered),
   **When** the pipeline runs, **Then** 10 rows are inserted into the transactions table.

2. **Given** a directory with 3 OFX files containing 10, 5, and 8 transactions
   respectively (none filtered), **When** the pipeline runs, **Then** 23 rows are
   inserted.

3. **Given** an OFX file that includes transactions named "Saldo do dia" and
   "Saldo Anterior", **When** the pipeline processes that file, **Then** those
   transactions are excluded and do not appear in the database.

4. **Given** a transaction whose MEMO tag value matches the pattern
   `DD/MM HH:MM description`, **When** the pipeline runs, **Then** the row contains:
   `effective_date = DD/MM/YYYY` (year from DTPOSTED) and `description = description text`.

5. **Given** a transaction whose MEMO tag does not match the `DD/MM HH:MM description`
   pattern, **When** the pipeline runs, **Then** the MEMO value is stored as-is in the
   description field and `effective_date` is left null.

---

### User Story 2 - Empty Directory (Priority: P2)

A user runs the pipeline against a directory that contains no OFX files. The pipeline
exits without error and without inserting any rows.

**Why this priority**: Graceful handling of an empty input directory prevents false
alarms in scheduled or automated runs.

**Independent Test**: Run the pipeline against an empty directory. Confirm: exit code
is 0, no rows are inserted, and an informational message is logged.

**Acceptance Scenarios**:

1. **Given** an empty directory, **When** the pipeline runs, **Then** the process exits
   with success, 0 rows are inserted, and the output contains a message indicating no
   files were found.

---

### User Story 3 - Idempotent Reload (Priority: P3)

A user re-runs the pipeline against the same directory. The resulting database state
reflects exactly the transactions from all files without duplicate rows.

**Why this priority**: Bank exports are often re-downloaded; duplicate data corrupts
downstream analysis.

**Independent Test**: Run the pipeline twice against the same directory. Confirm the
row count after the second run equals the row count after the first run.

**Acceptance Scenarios**:

1. **Given** the pipeline has already loaded all files in a directory, **When** the
   same directory is processed again, **Then** no duplicate rows appear in the database.

---

### Edge Cases

- What happens when the directory path does not exist?
  → Pipeline exits with an error and a clear message; no partial writes.
- What happens when the directory is empty (no OFX files)?
  → Pipeline exits with code 0; zero rows inserted; info message logged.
- What happens when one OFX file in the directory is malformed?
  → That file is skipped with an error log; the remaining files are still processed.
- What happens when a single OFX file is empty (header only, no transactions)?
  → File is processed; zero rows inserted from that file; pipeline continues.
- What happens when the MEMO tag is absent or blank?
  → Row is stored with `description = null` and `effective_date = null`.
- What happens when DTPOSTED contains a malformed date?
  → The row is skipped and logged; pipeline does not crash.
- What happens when the amount field is non-numeric?
  → The row is skipped and logged; pipeline does not crash.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept a directory path as input and scan it for files
  with the `.ofx` extension (case-insensitive).
- **FR-002**: If the directory contains zero OFX files, the system MUST exit
  successfully with an informational log message and insert zero rows.
- **FR-003**: If the directory contains one or more OFX files, the system MUST process
  each file sequentially, one at a time.
- **FR-004**: For each OFX file, the system MUST parse the XML portion, ignoring the
  plain-text header section before the XML root element.
- **FR-005**: For each `<STMTTRN>` element, the system MUST extract `DTPOSTED`, `NAME`,
  `MEMO`, and `TRNAMT`.
- **FR-006**: The system MUST filter out any transaction where `NAME` equals
  `"Saldo do dia"` or `"Saldo Anterior"`.
- **FR-007**: For each surviving transaction, the system MUST store the following fields
  in the database: `posted_date`, `description`, `amount`.
- **FR-008**: When `MEMO` matches the pattern `DD/MM HH:MM <text>`, the system MUST:
  - Derive `effective_date` as `DD/MM/YYYY`, where `YYYY` is the year from `DTPOSTED`.
  - Store the trailing `<text>` portion as `description`.
- **FR-009**: When `MEMO` does not match the pattern `DD/MM HH:MM <text>`, the system
  MUST store `MEMO` as-is in `description` and leave `effective_date` as null.
- **FR-010**: The system MUST NOT insert duplicate rows for transactions already present
  in the database (idempotent load — applies across all files and re-runs).
- **FR-011**: The system MUST log each skipped transaction (filtered or malformed) with
  the reason. A malformed or unreadable OFX file MUST be logged and skipped; remaining
  files in the directory MUST still be processed.

### Key Entities *(include if feature involves data)*

- **Transaction**: A single financial movement. Key attributes: posting date
  (`posted_date`), effective date (`effective_date`, nullable), description, amount.
  Source: one `<STMTTRN>` element in an OFX file.
- **OFX File**: A bank export file in a scanned directory. Consists of a plain-text
  header (ignored) followed by an XML document with one or more `<STMTTRN>` elements.
- **OFX Directory**: The input directory scanned for `.ofx` files. May contain zero or
  more files.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All transactions from all OFX files in the input directory (excluding
  filtered names) are present in the database after a single pipeline run.
- **SC-002**: Running the pipeline twice against the same directory produces the same
  number of rows as running it once — no duplicates.
- **SC-003**: Any transaction row whose MEMO matched the date-time pattern has a
  correctly populated `effective_date` and `description`.
- **SC-004**: A malformed or unreadable OFX file is skipped without crashing the
  pipeline; remaining files in the directory are still processed; at least one log
  entry per skipped row or file is produced.
- **SC-005**: Each individual OFX file of up to 1,000 transactions is processed in
  under 10 seconds on commodity hardware.
- **SC-006**: When the input directory is empty, the pipeline exits in under 1 second
  with a success code and an informational message.

## Assumptions

- The input directory path is supplied externally (environment variable or CLI argument),
  consistent with the Data Decoupling principle.
- Files are processed sequentially, not in parallel; parallel processing is out of scope
  for this version.
- Only files with the `.ofx` extension (case-insensitive) are processed; other files in
  the directory are ignored without error.
- The OFX file encoding is UTF-8 or Latin-1 (common for Brazilian bank exports).
- The relational database is already provisioned; the pipeline is responsible only for
  table creation (if absent) and row insertion — not for database server setup.
- The `DTPOSTED` field follows the OFX date format `YYYYMMDD` (possibly with time
  suffix); only the date portion is used.
- The `DD/MM HH:MM` pattern in MEMO uses zero-padded day and month (e.g., `03/06`).
- The database connection details are supplied externally (environment variables or
  configuration file), consistent with the Data Decoupling principle.
- A single OFX file corresponds to a single bank account statement; multi-account
  files are out of scope for this version.
- If an OFX file fails to parse, it is skipped and an error is logged; the pipeline
  continues processing remaining files rather than aborting.
