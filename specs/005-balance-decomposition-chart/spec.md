# Feature Specification: Daily Balance Decomposition Chart

**Feature Branch**: `005-balance-decomposition-chart`

**Created**: 2026-06-08

**Status**: Draft

**Input**: From the daily balance series, produce a visualization that decomposes the
balance over time into trend, seasonal, and residual components. The figure has four
stacked panels: the top panel is a line plot of the observed daily balance fluctuation; the
remaining three panels show the trend, seasonal, and residual components respectively.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate the Decomposition Chart (Priority: P1)

A user has already computed the daily balance series. They run the decomposition command,
which reads the daily balance over time, separates it into its underlying trend, repeating
seasonal pattern, and leftover residual, and saves a single chart image. The chart stacks
four panels vertically: the observed daily balance, the trend, the seasonal component, and
the residual. The user opens the image to understand how the balance moves over time, what
its longer-term direction is, what recurring weekly pattern it follows, and what remains
unexplained.

**Why this priority**: This is the whole feature — the decomposition chart is the single
deliverable.

**Independent Test**: With a daily balance series spanning at least two full seasonal cycles,
run the command and verify an image file is produced containing four labeled panels
(observed, trend, seasonal, residual), where the observed panel matches the stored daily
balance values over time.

**Acceptance Scenarios**:

1. **Given** a daily balance series covering at least two full seasonal cycles, **When** the
   decomposition command runs, **Then** an image file is created containing four stacked
   panels labeled observed, trend, seasonal, and residual.

2. **Given** the generated chart, **When** the top panel is inspected, **Then** it is a line
   plot of the observed daily balance values ordered by date.

3. **Given** the generated chart, **When** the trend, seasonal, and residual panels are
   inspected, **Then** each shows its respective component aligned to the same date axis as
   the observed panel.

4. **Given** a daily balance series with fewer than two full seasonal cycles, **When** the
   command runs, **Then** the system stops with a clear message explaining that more data is
   required and produces no chart.

5. **Given** an empty daily balance series, **When** the command runs, **Then** the system
   reports that there is nothing to decompose and produces no chart.

---

### Edge Cases

- What happens when the daily balance table is empty?
  → The system reports nothing to decompose and exits without producing a chart.
- What happens when there are not enough data points for a full decomposition (fewer than two
  seasonal cycles)?
  → The system stops with a clear "insufficient data" message and produces no chart.
- What happens at the very start and end of the range where the trend/residual cannot be
  computed?
  → Those panels show gaps for the affected dates; this is expected and does not cause an
  error.
- What happens if the output location is not writable?
  → The system reports the error clearly and produces no chart.
- What happens when the balance series contains negative or zero values?
  → The decomposition still works because components are combined additively.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST read the daily balance series (balance value per date), ordered
  chronologically, as the input to the decomposition.
- **FR-002**: The system MUST separate the daily balance series into three components: trend,
  seasonal, and residual.
- **FR-003**: The system MUST produce a single chart image containing four panels stacked
  vertically in this order: (1) observed daily balance, (2) trend, (3) seasonal, (4) residual.
- **FR-004**: The top panel MUST be a line plot of the observed daily balance values over the
  date range.
- **FR-005**: Each panel MUST share the same date axis so the components line up visually with
  the observed series, and each panel MUST be labeled with its component name.
- **FR-006**: The system MUST save the chart to an image file at a user-specified output path,
  or a documented default location when none is provided.
- **FR-007**: The system MUST use a repeating weekly cycle as the seasonal period by default,
  while allowing the period to be overridden.
- **FR-008**: When the series has fewer than two full seasonal cycles, the system MUST stop
  with a clear message and produce no chart.
- **FR-009**: When the daily balance series is empty, the system MUST report that there is
  nothing to decompose and produce no chart.

### Key Entities *(include if feature involves data)*

- **Daily Balance** (existing, read-only): The per-date balance series produced by the daily
  balance feature; the sole input to the decomposition. Not modified by this feature.
- **Decomposition Chart** (output artifact): A single image file containing four stacked,
  date-aligned panels — observed daily balance, trend, seasonal, and residual.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Given a daily balance series of at least two full seasonal cycles, running the
  command produces an image file containing exactly four labeled panels (observed, trend,
  seasonal, residual).
- **SC-002**: The observed panel reproduces the stored daily balance values in date order
  (every plotted point matches the corresponding stored balance).
- **SC-003**: The trend, seasonal, and residual components together reconstruct the observed
  series for every date where all three are defined (additive recombination matches the
  observed value within rounding tolerance).
- **SC-004**: When the input has fewer than two full seasonal cycles, the command produces no
  chart and returns a clear, actionable message.
- **SC-005**: For a typical multi-month daily series, the chart is generated in under 10
  seconds.

## Assumptions

- The seasonal cycle defaults to weekly (a 7-day period), consistent with the day-of-week and
  weekend attributes already tracked on the daily balance; the period is overridable.
- The decomposition is additive (components sum to the observed value), which is the safe
  choice because balances may be negative or zero.
- The decomposition operates on the global daily balance series (all accounts combined),
  consistent with how the daily balance is produced.
- The daily balance feature has already been run, so the daily balance series exists and is
  gap-filled (one continuous row per calendar day), which makes it a regular series suitable
  for decomposition.
- The chart is saved as an image file; the output path is provided on the command line or
  defaults to a documented location outside the project source tree.
- At least two full seasonal cycles of data are required for a meaningful decomposition (for
  the weekly default, at least 14 daily points).
- This is a separate command/operation from both the transaction loader and the daily balance
  calculator.
