# Feature Specification: Dark Mode Theme and Vektra App Title

**Feature Branch**: `006-dark-theme-app-title`

**Created**: 2026-06-10

**Status**: Draft

**Input**: The application must always present in dark mode, regardless of the viewer's
system or browser theme preference, and its title must be
"Vektra - Data science for personal finance".

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Branded, Always-Dark Interface (Priority: P1)

A user opens the application to view their personal-finance charts. The interface is
always presented in dark mode — a dark background with light, readable text — and the
title at the top of the app and in the browser tab reads
"Vektra - Data science for personal finance". This holds even when the user's operating
system or browser is set to light mode.

**Why this priority**: The visual identity (name and consistent dark appearance) is the
entire deliverable; there is nothing else to ship for this feature.

**Independent Test**: Open the application with the host system set to light mode and
confirm the interface still renders in dark mode and the title shows
"Vektra - Data science for personal finance".

**Acceptance Scenarios**:

1. **Given** a user whose system theme is light, **When** they open the application,
   **Then** the interface renders in dark mode (dark background, light text).

2. **Given** a user whose system theme is dark, **When** they open the application,
   **Then** the interface also renders in dark mode (unchanged).

3. **Given** the application is open, **When** the user views the main heading and the
   browser tab, **Then** both display "Vektra - Data science for personal finance".

4. **Given** the application is loaded, **When** no user action is taken, **Then** dark
   mode is already applied (no toggle or refresh required).

---

### Edge Cases

- What happens when the viewer's system later switches from light to dark, or vice versa,
  while the app is open?
  → The application stays in dark mode regardless; system theme changes do not affect it.
- Is there a way for the user to switch to light mode?
  → No. The application is always dark; a light option is intentionally not offered.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The application MUST always render in dark mode (dark background with light,
  readable foreground text), independent of the viewer's system or browser theme setting.
- **FR-002**: Dark mode MUST be applied automatically on first load, with no user action,
  toggle, or page refresh required.
- **FR-003**: The application MUST NOT offer a light-mode option; dark mode is the only
  appearance.
- **FR-004**: The application title MUST be "Vektra - Data science for personal finance".
- **FR-005**: The title MUST appear both as the main heading shown inside the application
  and as the browser tab/window title.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With the host system set to light mode, opening the application still shows a
  dark background and light text on first render — verifiable visually with no user action.
- **SC-002**: The exact text "Vektra - Data science for personal finance" appears as the
  application's main heading.
- **SC-003**: The exact text "Vektra - Data science for personal finance" appears as the
  browser tab/window title.
- **SC-004**: No control to switch to light mode is present anywhere in the application.

## Assumptions

- "Title" refers to both the heading displayed at the top of the application and the
  browser tab/window title; both are set to the same exact string for consistency.
- "Always dark mode" means the dark appearance is forced and does not follow the viewer's
  system/browser preference, and the user cannot switch it off.
- This feature applies to the existing chart application (the Streamlit-hosted view from
  feature 005); it changes only presentation (theme and title), not data or behavior.
- Readable contrast is expected (light text on a dark background) using a standard dark
  palette; no specific brand color values were provided, so sensible dark-theme defaults
  are acceptable.
