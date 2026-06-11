# Implementation Plan: Default Seasonality of 30 Days

**Branch**: `007-default-seasonality-30` | **Date**: 2026-06-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/007-default-seasonality-30/spec.md`

## Summary

Change the decomposition's default seasonal period from 7 to 30 days. The only code change
is the `DEFAULT_PERIOD` constant in `src/timeseries/decompose.py`. The Streamlit sidebar
already initializes from `DEFAULT_PERIOD` (so its default becomes 30 automatically), and the
minimum-data guard already scales as `2 * period` (so the default minimum becomes 60 points
with no logic change). Tests assert the new default and the 60-point minimum.

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: Unchanged (`statsmodels`, `pandas`, `streamlit`, …)

**Storage**: None touched

**Testing**: `pytest`

**Project Type**: Configuration/default change to the time-series decomposition

**Performance Goals**: No change

**Constraints**: Period remains user-overridable; default = 30

**Scale/Scope**: One constant + test updates

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Data Decoupling | ✅ PASS | No data/paths involved |
| II. ETL Discipline | ✅ PASS | Change confined to the pure `decompose` module's default constant |
| III. Test-First | ✅ PASS | Default-value and 60-point-minimum tests updated/added before the change |
| IV. Clean Code | ✅ PASS | Single named constant `DEFAULT_PERIOD`; comment updated to "monthly" |
| V. Simplicity First | ✅ PASS | One-line change; sidebar + minimum logic already derive from the constant |

*Post-design re-check*: All gates hold.

## Project Structure

### Source Code Changes

```text
src/timeseries/
└── decompose.py                    # UPDATED: DEFAULT_PERIOD = 30 (was 7)

tests/unit/
└── test_timeseries_decompose.py    # UPDATED: assert default == 30; default needs 60 points
```

No schema, migration, dependency, or interface changes. The app (`app.py`) is unchanged —
its sidebar already reads `value=DEFAULT_PERIOD`.

## Complexity Tracking

> **No violations — no entries required.**
