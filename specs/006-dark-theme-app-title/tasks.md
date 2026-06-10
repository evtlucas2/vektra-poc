---
description: "Task list for Dark Mode Theme and Vektra App Title"
---

# Tasks: Dark Mode Theme and Vektra App Title

**Input**: Design documents from `specs/006-dark-theme-app-title/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/ ✅

**TDD Note**: Tests are **mandatory** (Constitution Principle III). The testable surface —
the `APP_TITLE` constant and the `base = "dark"` theme config — is asserted by tests written
before the change. Visual rendering is verified manually (quickstart).

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no shared state dependencies)
- **[Story]**: Maps to user story from spec.md (US1)

---

## Phase 1: Setup

**Purpose**: No project scaffolding needed — presentation-only change to the existing app.

- [X] T001 Confirm the existing Streamlit app and tests are green baseline (`pytest tests/unit/ -q`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: None — this feature has no shared infrastructure prerequisites. Proceed to US1.

*(No foundational tasks.)*

---

## Phase 3: User Story 1 — Branded, Always-Dark Interface (Priority: P1) 🎯 MVP

**Goal**: The app always renders in dark mode (no light option) and the title (tab + heading)
reads "Vektra - Data science for personal finance".

**Independent Test**: `pytest tests/unit/test_app_appearance.py` (APP_TITLE + theme config),
then `streamlit run src/timeseries/app.py` shows a dark UI titled "Vektra - Data science for
personal finance" even with the OS in light mode.

### Tests for User Story 1 ⚠️ Write FIRST — confirm they FAIL before implementation

- [X] T002 [P] [US1] Write failing unit tests in `tests/unit/test_app_appearance.py`: (a) `from src.timeseries import app` then `app.APP_TITLE == "Vektra - Data science for personal finance"`; (b) `.streamlit/config.toml` exists and contains `base = "dark"`; (c) the config contains `toolbarMode = "minimal"`

### Implementation for User Story 1

- [X] T003 [P] [US1] Create `.streamlit/config.toml` at the project root with `[theme]\nbase = "dark"` and `[client]\ntoolbarMode = "minimal"` (depends T002)
- [X] T004 [US1] Update `src/timeseries/app.py`: add `APP_TITLE = "Vektra - Data science for personal finance"`; call `st.set_page_config(page_title=APP_TITLE)` as the first Streamlit command in `main()`; change `st.title(...)` to `st.title(APP_TITLE)`; guard the bottom call with `if __name__ == "__main__":\n    main()` (depends T002)
- [X] T005 [US1] Run `pytest tests/unit/test_app_appearance.py` (Green) and confirm `src/timeseries/app.py` still imports without connecting to the database (main is guarded) (depends T003, T004)

**Checkpoint**: US1 complete — forced dark theme + Vektra title, asserted by tests.

---

## Phase 4: Polish & Cross-Cutting Concerns

- [X] T006 [P] Verify all functions in `src/timeseries/app.py` remain ≤25 lines (Constitution Principle IV)
- [X] T007 Run the full unit suite and confirm all tests pass: `pytest tests/unit/`
- [ ] T008 Manual visual check per quickstart: with the OS in light mode, `streamlit run src/timeseries/app.py` renders dark, tab + heading show the Vektra title, and no light-mode switch is reachable

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 baseline check
- **Foundational (Phase 2)**: none
- **US1 (Phase 3)**: T002 (test, Red) → T003 + T004 (parallel, different files) → T005 (Green)
- **Polish (Phase 4)**: after US1

### Within US1

- T002 first (Red)
- T003 (`.streamlit/config.toml`) and T004 (`app.py`) are parallel — different files
- T005 verifies Green

### Parallel Opportunities

```bash
# After the failing test (T002), the two edits are parallel:
Task: T003 — .streamlit/config.toml
Task: T004 — src/timeseries/app.py
```

---

## Implementation Strategy

### MVP (US1)

1. T001 baseline → T002 failing test → T003 + T004 → T005 Green
2. `pytest tests/unit/` all pass
3. Manual visual check (T008)

### Notes

- Presentation-only: no data, schema, migration, or dependency changes
- `main()` is guarded so unit tests import `app.py` without a database connection (Streamlit
  still runs it because it execs the script as `"__main__"`)
- Title lives in one `APP_TITLE` constant used for both the tab title and the heading
