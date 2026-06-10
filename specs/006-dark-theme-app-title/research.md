# Research: Dark Mode Theme and Vektra App Title

**Branch**: `006-dark-theme-app-title` | **Date**: 2026-06-10

## Decision 1: Force Dark Mode via `.streamlit/config.toml`

**Decision**: Add a project-root `.streamlit/config.toml` with:

```toml
[theme]
base = "dark"

[client]
toolbarMode = "minimal"
```

`base = "dark"` sets an explicit dark theme as the app's theme, so the app renders dark on
first load regardless of the viewer's operating-system or browser preference (it is not the
"use system setting" mode). `toolbarMode = "minimal"` hides the hamburger/toolbar menu, which
is where the theme switcher lives — so the user has no exposed control to switch to light
mode (FR-003).

**Rationale**: Native Streamlit theming is the simplest, dependency-free way to force dark
mode (Principle V). Keeping it declarative in config keeps theme concerns out of code. The
config file is read by `streamlit run` from the working directory (project root), which is
where the app is launched per the quickstart.

**Alternatives considered**:
- Inject custom CSS (`st.markdown(<style>…</style>)` ) to repaint the app dark — fragile,
  fights Streamlit's own theme, and easy to break on version changes; rejected.
- Set theme only via `base="dark"` without `toolbarMode` — would force dark on load but leave
  the Settings → theme switcher reachable, partially violating FR-003; adding
  `toolbarMode="minimal"` closes that gap.

---

## Decision 2: Title via a Single `APP_TITLE` Constant

**Decision**: Define `APP_TITLE = "Vektra - Data science for personal finance"` in `app.py`.
Use it in two places:
- `st.set_page_config(page_title=APP_TITLE)` — the browser tab/window title (FR-005).
- `st.title(APP_TITLE)` — the in-app main heading (FR-005).

`st.set_page_config(...)` MUST be the first Streamlit command executed, so it is called at the
very start of `main()` before any other `st.*` call.

**Rationale**: One constant guarantees the heading and tab title cannot drift apart (Principle
IV — no duplicated magic strings). Using `set_page_config` for the tab title is the standard
Streamlit mechanism.

---

## Decision 3: Guard `main()` for Testability

**Decision**: Change the bottom of `app.py` from an unconditional `main()` to:

```python
if __name__ == "__main__":
    main()
```

**Rationale**: Streamlit executes the app script as a module named `"__main__"` (verified in
`streamlit.runtime.scriptrunner.script_runner`: `module = self._new_module("__main__")`), so
the guard still runs the app under `streamlit run`. At the same time, it stops `main()` (which
connects to the database) from executing when a unit test imports the module to read
`APP_TITLE`. This satisfies Test-First (Principle III) for a UI module that otherwise could
not be imported safely.

**Alternatives considered**:
- Keep `main()` unconditional and test the title by static file parsing — hacky and brittle;
  the guard is cleaner and idiomatic.

---

## Decision 4: Testing Strategy for a Visual Feature

**Decision**: Unit tests assert (a) `app.APP_TITLE` equals the exact required string and (b)
`.streamlit/config.toml` exists and contains `base = "dark"`. The actual dark rendering and
the tab title are confirmed manually in the browser (documented in quickstart).

**Rationale**: The testable, regression-prone parts are the title string and the theme
setting; both are asserted automatically. Pixel-level appearance is inherently visual and is
validated by a manual check rather than a brittle screenshot test (Principle V).
