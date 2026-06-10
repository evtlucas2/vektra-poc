# Implementation Plan: Dark Mode Theme and Vektra App Title

**Branch**: `006-dark-theme-app-title` | **Date**: 2026-06-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/006-dark-theme-app-title/spec.md`

## Summary

A presentation-only change to the existing Streamlit app. A project-level Streamlit theme
config forces dark mode on every load (independent of the viewer's system setting) and hides
the toolbar menu so no light-mode switch is reachable. The app sets its browser-tab title and
in-app heading to "Vektra - Data science for personal finance" via a single `APP_TITLE`
constant. No data, schema, or pipeline changes.

## Technical Context

**Language/Version**: Python 3.13 (system)

**Primary Dependencies**: Unchanged (existing `streamlit`). No new dependencies.

**Storage**: None touched (this feature reads/writes no data)

**Testing**: `pytest` — assert the `APP_TITLE` constant and the theme config file contents
(the visual rendering itself is verified manually)

**Target Platform**: Local Streamlit server in the browser

**Project Type**: UI presentation/configuration change

**Performance Goals**: No change

**Constraints**:
- Dark mode must apply on first load without user action and must not follow the system theme
- No light-mode option exposed to the user
- Title string must be exactly "Vektra - Data science for personal finance"

**Scale/Scope**: Two files — `.streamlit/config.toml` (new) and `src/timeseries/app.py` (edit)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Data Decoupling | ✅ PASS | No data or connection paths involved; only UI config |
| II. ETL Discipline | ✅ PASS | Change is confined to the presentation layer (`app.py`) + a config file; ETL modules untouched |
| III. Test-First | ✅ PASS | Tests assert `APP_TITLE` value and `.streamlit/config.toml` has `base = "dark"`, written before the edit; `main()` guarded so the module is importable for tests |
| IV. Clean Code | ✅ PASS | Title centralized in one `APP_TITLE` constant (no magic string duplication); functions stay ≤25 lines |
| V. Simplicity First | ✅ PASS | Native Streamlit theme config (`base="dark"`) + `toolbarMode="minimal"`; no custom CSS, no new dependency |

*Post-design re-check*: All gates hold after Phase 1.

## Project Structure

### Documentation (this feature)

```text
specs/006-dark-theme-app-title/
├── plan.md          # This file
├── research.md      # Phase 0 output
├── data-model.md    # Phase 1 output (no entities — noted)
├── quickstart.md    # Phase 1 output
├── contracts/       # Phase 1 output
│   └── ui-appearance.md
└── tasks.md         # Phase 2 output (/speckit-tasks)
```

### Source Code Changes

```text
.streamlit/
└── config.toml                     # NEW — [theme] base="dark"; [client] toolbarMode="minimal"

src/timeseries/
└── app.py                          # UPDATED: APP_TITLE constant; st.set_page_config(page_title=APP_TITLE)
                                    #   as first Streamlit call; st.title(APP_TITLE); guard main() with __main__

tests/
└── unit/
    └── test_app_appearance.py      # NEW — APP_TITLE value + config.toml contains base="dark"
```

**Structure Decision**: Theme is set declaratively in the standard `.streamlit/config.toml`
at the project root (read by `streamlit run` from the working directory), keeping forced dark
mode out of code (Principle V). The title is the only code change in `app.py`, centralized in
one constant so the heading and tab title cannot drift apart. Guarding `main()` behind
`if __name__ == "__main__":` lets tests import the module to inspect `APP_TITLE` without
launching Streamlit or connecting to the database.

## Complexity Tracking

> **No violations — no entries required.**
