# Research: Default Seasonality of 30 Days

**Branch**: `007-default-seasonality-30` | **Date**: 2026-06-11

## Decision 1: Change Only the `DEFAULT_PERIOD` Constant

**Decision**: Set `DEFAULT_PERIOD = 30` in `src/timeseries/decompose.py` (was 7). Update the
inline comment from "weekly" to "monthly (approx)".

**Rationale**: `decompose_balance(series, period=DEFAULT_PERIOD)` and the Streamlit sidebar
(`number_input(..., value=DEFAULT_PERIOD)`) both derive from this single constant, so changing
it updates both the computation default and the displayed default with no other edits
(Principle IV/V).

## Decision 2: Minimum-Data Guard Needs No Change

**Decision**: Leave the `minimum = 2 * period` check as-is.

**Rationale**: The guard already scales with the active period. With the new default it
naturally requires `2 * 30 = 60` daily points (FR-004); explicit overrides keep their own
`2 * period` minimum. No code change beyond the constant.

## Decision 3: Test Updates

**Decision**: Replace `test_default_period_is_seven` with an assertion that `DEFAULT_PERIOD ==
30`, and add a test that the default path rejects a series shorter than 60 points (and accepts
exactly 60). Existing tests that pass `period=7` explicitly remain valid and unchanged.

**Rationale**: TDD — the default-value change is captured by a failing test first, and the new
60-point minimum behavior is pinned so it cannot silently regress (Principle III).
