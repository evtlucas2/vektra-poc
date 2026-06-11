# Feature Specification: Top Expense Days Table

**Feature Branch**: `008-top-expense-days-table`

**Created**: 2026-06-11

**Status**: Draft

**Input**: On the application's main page, add a table that lists the days with the highest
expenses from the daily balance data — specifically the days whose daily change places them in
the most-extreme 5% (the 5th-percentile tail) of expenses — sorted from the largest expense
downward.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See My Worst Spending Days (Priority: P1)

A user opens the application's main page and, alongside the existing chart, sees a table of
their highest-expense days. Each row is a single day, and the table contains only the days in
the worst 5% by expense (the 5th-percentile tail of the daily change). The rows are ordered
with the single largest-expense day at the top, descending to the smallest expense within that
group. This lets the user immediately spot which days drained their balance the most.

**Why this priority**: Surfacing the worst spending days is the entire deliverable and the
direct user value.

**Independent Test**: Load daily balance data with a known spread of daily changes, open the
main page, and confirm the table shows exactly the days in the bottom 5% of daily change
(the highest expenses), ordered with the largest expense first.

**Acceptance Scenarios**:

1. **Given** daily balance data exists, **When** the user opens the main page, **Then** a
   table of the highest-expense days appears below the chart.

2. **Given** the table is shown, **When** the user reads it top-to-bottom, **Then** the day
   with the largest expense is first and each following row has an equal or smaller expense.

3. **Given** the table is shown, **When** the user inspects which days are included, **Then**
   only the days whose daily change falls at or below the 5th-percentile threshold (the
   most-extreme 5% of expenses) are present.

4. **Given** each row in the table, **When** the user reads it, **Then** it shows the day's
   date and its expense amount (and supporting context such as the day of week and the end-of-
   day balance).

---

### Edge Cases

- What happens when there is no daily balance data?
  → The table area shows a message that there is nothing to display; no table rows.
- What happens when no day has an expense (every daily change is zero or positive)?
  → The table shows a message that there are no expense days; no rows.
- What happens when there are very few days, so the 5% tail is less than one full day?
  → At least one day (the largest expense) is shown, so the table is never empty when at least
  one expense day exists.
- How are days with no spending (zero or positive daily change) treated?
  → They are not expenses and are excluded from the table.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The main page MUST display a table of the highest-expense days derived from the
  daily balance data.
- **FR-002**: A day's expense MUST be defined as a negative daily change (the day's balance
  decreased versus the previous day); the expense amount is the size of that decrease. Days
  whose daily change is zero or positive are not expenses.
- **FR-003**: The system MUST determine the 5th-percentile threshold of the daily change across
  the available daily balance data and include only the days whose daily change is at or below
  that threshold (the most-extreme 5% — the highest expenses).
- **FR-004**: The table MUST be ordered by expense in descending order — the largest expense at
  the top, decreasing downward.
- **FR-005**: Each table row MUST identify the day (its date) and its expense amount, and SHOULD
  include supporting context already available for that day (day of week, end-of-day balance).
- **FR-006**: When there is no daily balance data, or no day qualifies as an expense, the system
  MUST show a clear "nothing to display" message instead of an empty table.
- **FR-007**: When at least one expense day exists, the table MUST contain at least one row even
  if 5% of the day count rounds to less than one.

### Key Entities *(include if feature involves data)*

- **Daily Balance** (existing, read-only): the per-day record produced by the daily balance
  feature. Relevant attributes used here: the date, the daily change (difference from the
  previous day), the end-of-day balance, and the day of week. Not modified by this feature.
- **Top Expense Row** (derived, display-only): one selected high-expense day shown in the
  table — its date, expense amount, day of week, and end-of-day balance.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With known daily balance data, the table contains exactly the days whose daily
  change is at or below the 5th-percentile threshold — verifiable by independent recomputation
  of the threshold and selection.
- **SC-002**: The rows are sorted so that the largest expense is first and each subsequent row's
  expense is less than or equal to the previous row's.
- **SC-003**: No day with a zero or positive daily change appears in the table.
- **SC-004**: When no daily balance data exists, or no day is an expense, the page shows a clear
  message and no table rows.
- **SC-005**: When at least one expense day exists, the table is never empty (shows at least the
  single largest-expense day).

## Assumptions

- "Expenses" come solely from the existing daily balance data (as the request specifies); a
  day's expense is the magnitude of its negative daily change. The application does not look at
  individual transactions for this feature.
- The 5th-percentile threshold is computed over the daily change values present in the daily
  balance data; the selected days are those in the most-extreme 5% (largest expenses).
- "Descending order" means ordered by expense amount, largest first.
- The table is added to the existing main page of the chart application (the Streamlit-hosted
  view), below the existing chart, and is read-only.
- The table reads already-computed daily balance data; producing that data is a prerequisite
  handled by the daily balance feature and is out of scope here.
- Standard, well-defined percentile interpolation is acceptable; no specific percentile method
  was mandated.
