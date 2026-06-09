---
description: "Task list for Daily Balance Decomposition Chart feature"
---

# Tasks: Daily Balance Decomposition Chart

**Input**: Design documents from `specs/005-balance-decomposition-chart/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/ ✅

**TDD Note**: Tests are **mandatory** (Constitution Principle III). The three functions
behind the UI (`extract`, `decompose`, `plot`) are written test-first. The Streamlit
`app.py` is a thin presentation layer wired from those tested functions.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no shared state dependencies)
- **[Story]**: Maps to user story from spec.md (US1)

---

## Phase 1: Setup

**Purpose**: Add new dependencies and scaffold the `src/timeseries/` package.

- [X] T001 Add `streamlit`, `statsmodels`, `matplotlib`, `pandas` to `requirements.txt` and run `pip install -r requirements.txt`
- [X] T002 [P] Create package marker `src/timeseries/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Confirm the new dependencies import. No model/migration needed (read-only,
no schema change).

- [X] T003 Verify `import streamlit`, `import statsmodels`, `import matplotlib`, `import pandas` all succeed after T001 (run `python -c "import streamlit, statsmodels, matplotlib, pandas"`)

**Checkpoint**: Dependencies available — US1 can begin.

---

## Phase 3: User Story 1 — Generate the Decomposition Chart (Priority: P1) 🎯 MVP

**Goal**: A Streamlit app reads the `daily_balance` series, decomposes it (additive, weekly),
and renders a four-panel chart (observed, trend, seasonal, residual) with a PNG download.

**Independent Test**: `pytest tests/unit/test_timeseries_decompose.py
tests/unit/test_timeseries_plot.py tests/unit/test_timeseries_extract.py` plus integration
`test_timeseries_pipeline.py`; then `streamlit run src/timeseries/app.py` shows the 4 panels.

### Tests for User Story 1 ⚠️ Write FIRST — confirm all FAIL before implementation

- [X] T004 [P] [US1] Write failing unit tests for `fetch_balance_series(conn)` in `tests/unit/test_timeseries_extract.py`: returns a pandas Series of floats indexed by date (mocked cursor); empty result → empty Series
- [X] T005 [P] [US1] Write failing unit tests for `decompose_balance(series, period)` in `tests/unit/test_timeseries_decompose.py`: returns object with observed/trend/seasonal/resid; additive recombination (`trend+seasonal+resid ≈ observed` where not NaN); empty series → `ValueError`; `len < 2*period` → `ValueError` naming the minimum; uses `DEFAULT_PERIOD == 7`
- [X] T006 [P] [US1] Write failing unit tests for `build_decomposition_figure(result)` in `tests/unit/test_timeseries_plot.py`: returns a `matplotlib.figure.Figure` with exactly 4 axes, each with a non-empty title/label
- [X] T007 [P] [US1] Write failing integration test in `tests/integration/test_timeseries_pipeline.py`: seed `daily_balance` with ≥ 2 weeks of rows, run `fetch_balance_series` + `decompose_balance`, assert component lengths equal the series length (skips without `DATABASE_URL`)

### Implementation for User Story 1 (after T004–T007 confirmed failing)

- [X] T008 [P] [US1] Implement `fetch_balance_series(conn) -> pandas.Series` in `src/timeseries/extract.py`: `SELECT balance_date, balance FROM daily_balance ORDER BY balance_date`, build a float Series with a `DatetimeIndex` (freq="D") (depends T004)
- [X] T009 [P] [US1] Implement `decompose_balance(series, period=DEFAULT_PERIOD)` in `src/timeseries/decompose.py` with `DEFAULT_PERIOD = 7`: raise `ValueError` on empty series and on `len(series) < 2*period`; else return `statsmodels.tsa.seasonal.seasonal_decompose(series, model="additive", period=period)` (depends T005)
- [X] T010 [P] [US1] Implement `build_decomposition_figure(result) -> Figure` in `src/timeseries/plot.py`: 4 stacked, date-aligned subplots labeled Observed / Trend / Seasonal / Residual; top panel is a line plot of `result.observed` (depends T006)
- [X] T011 [US1] Implement `src/timeseries/app.py` Streamlit app: load `config/.env`, connect via `DATABASE_URL`, fetch series; if empty → `st.warning` and stop; sidebar period input (default 7); if `len < 2*period` → `st.warning` and stop; else decompose, `st.pyplot(build_decomposition_figure(...))`, and `st.download_button` for the PNG (depends T008, T009, T010)
- [X] T012 [US1] Run unit tests T004–T006 (Green) and the integration test T007; confirm the app renders by launching `streamlit run src/timeseries/app.py` against a populated database (depends T008–T011)

**Checkpoint**: US1 complete — decomposition chart hosted in Streamlit.

---

## Phase 4: Polish & Cross-Cutting Concerns

- [X] T013 [P] Validate all functions ≤25 lines across `src/timeseries/*.py` (Constitution Principle IV); refactor if needed (extract a per-panel helper in `plot.py` if required)
- [X] T014 [P] Update `config/.env.example` only if a new variable is introduced (none expected — `DATABASE_URL` already documented); otherwise no change
- [X] T015 Run full unit suite and confirm all tests pass: `pytest tests/unit/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 (deps) → T002 (package marker)
- **Foundational (Phase 2)**: T003 verifies imports — depends on T001
- **US1 (Phase 3)**: depends on Phase 2 — MVP
- **Polish (Phase 4)**: depends on US1

### Within US1

- Tests T004–T007 all parallel (different files) — all Red before implementation
- Implementations T008, T009, T010 parallel (different files)
- T011 (app) depends on T008+T009+T010; T012 verifies everything

### Parallel Opportunities

```bash
# US1 tests — all parallel (Red):
Task: T004 — tests/unit/test_timeseries_extract.py
Task: T005 — tests/unit/test_timeseries_decompose.py
Task: T006 — tests/unit/test_timeseries_plot.py
Task: T007 — tests/integration/test_timeseries_pipeline.py

# US1 implementation — extract/decompose/plot parallel:
Task: T008 — src/timeseries/extract.py
Task: T009 — src/timeseries/decompose.py
Task: T010 — src/timeseries/plot.py
# then:
Task: T011 — src/timeseries/app.py
```

---

## Implementation Strategy

### MVP (US1)

1. Phase 1 Setup → Phase 2 Foundational → Phase 3 US1
2. Run `pytest tests/unit/` — all pass
3. Launch `streamlit run src/timeseries/app.py` against a populated database and confirm the
   four panels render

### Incremental Delivery

1. Setup + Foundational → dependencies available
2. US1 → tested extract/decompose/plot + Streamlit app (MVP)
3. Polish → line-length check, full suite

---

## Notes

- `decompose` and `plot` are pure (no I/O) — the primary unit-test targets
- The Streamlit UI itself is not unit-tested; its behavior is covered by the tested functions
- Integration tests auto-skip without `DATABASE_URL`
- No database schema change and no new migration — reads `daily_balance` read-only
- Existing commands (`python -m src.cli`, `python -m src.balance`) are untouched
- Seasonal period defaults to 7 (weekly), overridable in the app sidebar; additive model
