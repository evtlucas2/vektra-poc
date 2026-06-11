---
description: "Task list for Default Seasonality of 30 Days"
---

# Tasks: Default Seasonality of 30 Days

**Input**: Design documents from `specs/007-default-seasonality-30/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅

**TDD Note**: Tests are **mandatory** (Constitution Principle III). The default-value change
is captured by a failing test first.

## Format: `[ID] [P?] [Story?] Description`

---

## Phase 1: Setup

- [X] T001 Confirm baseline tests are green (`pytest tests/unit/ -q`)

---

## Phase 2: User Story 1 — Decompose With a 30-Day Default Season (Priority: P1) 🎯 MVP

**Goal**: The decomposition default seasonal period is 30 days; minimum data at the default
becomes 60 points; period stays overridable.

**Independent Test**: `pytest tests/unit/test_timeseries_decompose.py` — default is 30; default
path rejects < 60 points and accepts 60.

### Tests for User Story 1 ⚠️ Write FIRST — confirm they FAIL before implementation

- [X] T002 [US1] Update `tests/unit/test_timeseries_decompose.py`: replace `test_default_period_is_seven` with `test_default_period_is_thirty` asserting `DEFAULT_PERIOD == 30`; add `test_default_requires_sixty_points` (a 59-point series with no period override raises `ValueError` mentioning 60, and a 60-point series succeeds)

### Implementation for User Story 1

- [X] T003 [US1] Change `DEFAULT_PERIOD` from `7` to `30` in `src/timeseries/decompose.py`; update the inline comment to "monthly (approx)" (depends T002)
- [X] T004 [US1] Run `pytest tests/unit/test_timeseries_decompose.py` (Green) (depends T003)

**Checkpoint**: Default seasonality is 30; existing explicit-period tests unaffected.

---

## Phase 3: Polish

- [X] T005 Run the full unit suite: `pytest tests/unit/`

---

## Dependencies & Execution Order

- T001 → T002 (Red) → T003 (Green) → T004 → T005
- The Streamlit sidebar default updates automatically (reads `DEFAULT_PERIOD`); `app.py`
  needs no edit.

## Notes

- One-line production change (`DEFAULT_PERIOD = 30`); the minimum-data guard (`2 * period`)
  and the sidebar default both derive from it.
- Tests passing `period=7` explicitly remain valid and unchanged.
