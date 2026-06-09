# Implementation Plan: Daily Balance Decomposition Chart

**Branch**: `005-balance-decomposition-chart` | **Date**: 2026-06-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/005-balance-decomposition-chart/spec.md`

## Summary

A Streamlit web app hosts a four-panel decomposition chart of the daily balance series.
The app reads the `daily_balance` table into a regular daily time series, runs an additive
seasonal decomposition (weekly period by default), and renders a single figure with four
stacked, date-aligned panels — observed, trend, seasonal, residual. A new `src/timeseries/`
package separates data fetching (`extract`), the pure decomposition (`decompose`), and
figure building (`plot`) from the Streamlit presentation layer (`app.py`). The app offers a
download button to save the chart as a PNG (satisfying the "save to file" requirement).

## Technical Context

**Language/Version**: Python 3.13 (system)

**Primary Dependencies**: Existing — `psycopg2-binary`, `python-dotenv`. **New** —
`streamlit` (host/UI), `statsmodels` (seasonal decomposition), `matplotlib` (figure),
`pandas` (regular time-series indexing). Test deps unchanged (`pytest`, `pytest-mock`).

**Storage**: PostgreSQL — reads the existing `daily_balance` table (read-only). No schema
change, no new migration.

**Testing**: `pytest`, `pytest-mock`. Pure functions (`decompose`, `plot`) and `extract`
(mocked cursor) are unit-tested; the Streamlit UI is driven by these tested functions.

**Target Platform**: Local Streamlit server in the browser (`streamlit run`)

**Project Type**: Time-series analysis + web UI (Streamlit)

**Performance Goals**: Chart generated in under 10 seconds for a multi-month daily series

**Constraints**:
- `DATABASE_URL` from env / `config/.env`; no hardcoded paths (Principle I)
- Seasonal period defaults to 7 (weekly), overridable in the app
- Requires ≥ 2 full seasonal cycles (≥ 14 daily points for weekly)

**Scale/Scope**: One global series; single decomposition figure per view

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Data Decoupling | ✅ PASS | `DATABASE_URL` from env; chart shown in-app and downloaded by the user (no hardcoded output path) |
| II. ETL Discipline | ✅ PASS | Separate phases: `extract.py` (I/O → pandas Series), `decompose.py` (pure), `plot.py` (pure → Figure); `app.py` is presentation only |
| III. Test-First | ✅ PASS | `decompose`, `plot`, and `extract` unit-tested before implementation; insufficient-data and empty-series guards tested |
| IV. Clean Code | ✅ PASS | Functions ≤25 lines; `DEFAULT_PERIOD = 7` named constant; thin app layer |
| V. Simplicity First | ✅ PASS | Standard `statsmodels.seasonal_decompose`; Streamlit as requested; no custom decomposition math |

*Post-design re-check*: All gates hold after Phase 1.

## Project Structure

### Documentation (this feature)

```text
specs/005-balance-decomposition-chart/
├── plan.md          # This file
├── research.md      # Phase 0 output
├── data-model.md    # Phase 1 output
├── quickstart.md    # Phase 1 output
├── contracts/       # Phase 1 output
│   └── app-interface.md
└── tasks.md         # Phase 2 output (/speckit-tasks)
```

### Source Code Changes

```text
src/
└── timeseries/                     # NEW package — time-series analysis + UI
    ├── __init__.py
    ├── extract.py                  # fetch_balance_series(conn) -> pandas Series (balance by date, freq=D)
    ├── decompose.py                # decompose_balance(series, period=7) -> DecomposeResult (PURE; validates >=2 cycles)
    ├── plot.py                     # build_decomposition_figure(result) -> matplotlib Figure (4 panels)
    └── app.py                      # Streamlit app: connect, extract, decompose, render, download PNG

requirements.txt                    # UPDATED: add streamlit, statsmodels, matplotlib, pandas

tests/
├── unit/
│   ├── test_timeseries_extract.py  # NEW — series shape/index from mocked cursor
│   ├── test_timeseries_decompose.py# NEW — components, additive recombination, insufficient/empty guards
│   └── test_timeseries_plot.py     # NEW — figure has 4 labeled axes
└── integration/
    └── test_timeseries_pipeline.py # NEW — extract+decompose against PostgreSQL (skips without DATABASE_URL)
```

**Structure Decision**: New `src/timeseries/` package matching the constitution's time-series
feature area. The three computational concerns (extract → decompose → plot) are separated and
independently testable per Principle II; `app.py` is a thin Streamlit presentation layer that
wires them together. Hosted via `streamlit run src/timeseries/app.py`. The existing loader
(`python -m src.cli`) and balance command (`python -m src.balance`) are untouched.

## Complexity Tracking

> **No violations — no entries required.**
