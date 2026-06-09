# Research: Daily Balance Decomposition Chart

**Branch**: `005-balance-decomposition-chart` | **Date**: 2026-06-08

## Decision 1: Decomposition Method — statsmodels `seasonal_decompose`

**Decision**: Use `statsmodels.tsa.seasonal.seasonal_decompose(series, model="additive",
period=7)`. It returns a `DecomposeResult` with `.observed`, `.trend`, `.seasonal`, and
`.resid` pandas Series — exactly the four panels the spec requires.

**Rationale**: It is the standard, well-documented classical decomposition and maps 1:1 to
the requested output (observed/trend/seasonal/residual) with a single call (Principle V).
The daily balance series is gap-filled (one row per calendar day), so it is already a
regular series with no missing dates — a precondition `seasonal_decompose` needs.

**Alternatives considered**:
- `STL` (statsmodels) — more robust to changing seasonality but heavier and unnecessary for
  a first version; classical additive decomposition is sufficient and simpler.
- Hand-rolled moving-average decomposition — reinvents a solved problem; rejected
  (Principle V).

---

## Decision 2: Additive Model

**Decision**: `model="additive"`, so `observed ≈ trend + seasonal + resid`.

**Rationale**: Balances can be negative or zero; multiplicative decomposition is undefined
for non-positive values. Additive is the safe, correct default (matches the spec assumption)
and makes the recombination check in SC-003 straightforward.

---

## Decision 3: Weekly Seasonal Period (default 7, overridable)

**Decision**: `DEFAULT_PERIOD = 7`. The Streamlit app exposes a sidebar control to override
the period.

**Rationale**: The daily balance already tracks day-of-week and weekend, so a weekly cycle is
the natural seasonality. `seasonal_decompose` requires at least two full periods, so the
minimum series length is `2 * period` (14 for weekly); the app validates this.

---

## Decision 4: Regular Time Series via pandas

**Decision**: `extract` returns a `pandas.Series` of `balance` indexed by a
`DatetimeIndex` with daily frequency (`freq="D"`), built from `SELECT balance_date, balance
FROM daily_balance ORDER BY balance_date`.

**Rationale**: `seasonal_decompose` works cleanly on a pandas Series with a proper
DatetimeIndex and frequency. Because `daily_balance` is gap-filled, setting `freq="D"` is
valid with no reindexing gaps.

**Edge note**: `balance` is `NUMERIC` (Decimal from psycopg2). Convert to float when building
the Series so statsmodels/matplotlib handle it numerically.

---

## Decision 5: Streamlit as the Host

**Decision**: A Streamlit app (`src/timeseries/app.py`) run via `streamlit run
src/timeseries/app.py`. It loads `config/.env`, connects with `DATABASE_URL`, fetches the
series, decomposes, renders the figure with `st.pyplot(fig)`, and provides a
`st.download_button` to save the chart as a PNG.

**Rationale**: The user explicitly chose Streamlit to host the charts. In-app rendering plus
a download button satisfies FR-006 (user-chosen output location via the browser) without
hardcoding a server-side path (Principle I).

**Alternatives considered**:
- Save a static PNG to `DATA_ROOT/output/` from a CLI — was the original spec framing;
  superseded by the explicit Streamlit request. The download button preserves the
  save-to-file capability.

---

## Decision 6: Figure Construction Separated from UI

**Decision**: `build_decomposition_figure(result) -> matplotlib.figure.Figure` lives in
`plot.py` and returns a Figure with four stacked, date-aligned, labeled subplots (observed,
trend, seasonal, residual). `app.py` only calls it and hands the Figure to `st.pyplot`.

**Rationale**: Keeping figure construction out of the Streamlit script makes it unit-testable
(assert the Figure has four labeled axes) without running a Streamlit server — preserving
Test-First (Principle III) and ETL separation (Principle II).

---

## Decision 7: Insufficient / Empty Data Handling

**Decision**: `decompose_balance` raises `ValueError` with a clear message when the series is
empty ("no daily balance data") or shorter than `2 * period` ("need at least N data points").
The Streamlit app catches these and shows `st.warning(...)` instead of a chart.

**Rationale**: Satisfies FR-008 and FR-009 with explicit, testable behavior; the pure
function fails loudly and the UI translates it into a friendly message.

---

## Decision 8: New Dependencies

**Decision**: Add `streamlit`, `statsmodels`, `matplotlib`, `pandas` to `requirements.txt`.

**Rationale**: All four are required and not yet installed: Streamlit (host), statsmodels
(decomposition), matplotlib (figure), pandas (regular series). statsmodels transitively pulls
numpy/scipy. This is the minimal set for the requested capability (Principle V) — no broader
framework is introduced.
