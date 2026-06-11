# Feature Specification: Default Seasonality of 30 Days

**Feature Branch**: `007-default-seasonality-30`

**Created**: 2026-06-11

**Status**: Draft

**Input**: Change the default seasonal period used by the daily balance decomposition from
the previous weekly (7-day) default to 30 days. The period remains overridable by the user;
only the default changes.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Decompose With a 30-Day Default Season (Priority: P1)

A user opens the decomposition view without choosing a seasonal period. The decomposition
now uses a 30-day seasonal cycle by default (instead of 7 days), so the seasonal panel
reflects a roughly monthly recurring pattern rather than a weekly one. The user can still
override the period when they want a different cycle.

**Why this priority**: The default directly shapes what every user sees on first view; it is
the entire change.

**Independent Test**: Open the decomposition view without specifying a period and confirm the
seasonal component is computed using a 30-day cycle; then override the period and confirm the
override is honored.

**Acceptance Scenarios**:

1. **Given** a user who does not specify a seasonal period, **When** the decomposition runs,
   **Then** it uses a 30-day seasonal cycle.

2. **Given** the decomposition view, **When** it first loads, **Then** the period control
   shows 30 as its default value.

3. **Given** a user who sets the period to a value other than 30, **When** the decomposition
   runs, **Then** the chosen value is used instead of the default.

4. **Given** a balance series with fewer than two full 30-day cycles (fewer than 60 daily
   points) and no period override, **When** the decomposition runs, **Then** the system
   reports that more data is required and produces no chart.

---

### Edge Cases

- What happens when the series has between 14 and 59 daily points (enough for the old weekly
  default but not for the new 30-day default)?
  → With the default period, the system reports insufficient data; the user may still
  override with a smaller period to decompose the shorter series.
- What happens when the user explicitly sets the period back to 7?
  → The decomposition uses 7; the new default does not prevent smaller periods.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The default seasonal period used by the decomposition, when the user does not
  specify one, MUST be 30 days.
- **FR-002**: The period MUST remain user-overridable; supplying a value other than 30 MUST
  cause that value to be used instead of the default.
- **FR-003**: The decomposition view's period control MUST present 30 as its initial/default
  value.
- **FR-004**: The minimum-data rule MUST continue to require at least two full seasonal
  cycles; with the 30-day default this means at least 60 daily data points. When fewer points
  are available and no override is given, the system MUST report insufficient data and produce
  no chart.

### Key Entities *(include if feature involves data)*

- **Decomposition Setting** (configuration, not stored data): the default seasonal period,
  changing from 7 to 30 days. No database entity is affected.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With no period specified, the decomposition uses a 30-day seasonal cycle —
  verifiable because the seasonal pattern repeats every 30 days.
- **SC-002**: The period control's default displayed value is 30.
- **SC-003**: Overriding the period with any valid value other than 30 results in that value
  being used (the default does not override an explicit choice).
- **SC-004**: With fewer than 60 daily points and no override, the system produces no chart
  and returns a clear "insufficient data" message naming the minimum.

## Assumptions

- "Seasonality" refers to the seasonal period of the daily balance decomposition introduced
  in feature 005; this feature changes only its default value (7 → 30).
- 30 days is treated as an approximate monthly cycle; no calendar-month-length adjustment is
  implied (every default cycle is exactly 30 days).
- The override mechanism and all other decomposition behavior (additive model, four-panel
  chart, empty-series handling) are unchanged.
- The minimum-data requirement scales with the active period (two full cycles), so the default
  now needs 60 daily points rather than 14.
