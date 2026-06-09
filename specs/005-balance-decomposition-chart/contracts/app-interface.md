# Contract: Streamlit App Interface

**Feature**: Daily Balance Decomposition Chart | **Date**: 2026-06-08

## Launch

```
streamlit run src/timeseries/app.py
```

Opens the app in the browser (default `http://localhost:8501`).

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | YES | PostgreSQL DSN. Loaded from `config/.env`. |

## UI Elements

| Element | Purpose |
|---------|---------|
| Title / header | Names the view ("Daily Balance Decomposition") |
| Seasonal period control (sidebar) | Integer input; default `7` (weekly); overridable |
| Decomposition figure | Four stacked panels: observed, trend, seasonal, residual |
| Download button | Saves the current figure as a PNG |
| Warning message | Shown instead of a chart when data is empty or insufficient |

## Behavior

1. Load `config/.env`; read `DATABASE_URL`.
2. Connect and fetch the daily balance series (`balance` by date).
3. If the series is empty → show `st.warning("No daily balance data. Run the daily balance command first.")` and stop.
4. Read the seasonal period from the sidebar (default 7).
5. If the series has fewer than `2 * period` points → show `st.warning("Need at least <N> data points for a <period>-day decomposition.")` and stop.
6. Decompose (additive) and render the four-panel figure via `st.pyplot`.
7. Offer the figure as a downloadable PNG via `st.download_button`.

## Underlying Function Contracts (unit-testable, no Streamlit)

```python
# extract.py
fetch_balance_series(conn) -> pandas.Series   # float values, DatetimeIndex freq="D"

# decompose.py
DEFAULT_PERIOD = 7
decompose_balance(series, period=DEFAULT_PERIOD) -> statsmodels DecomposeResult
#   raises ValueError on empty series or len(series) < 2 * period

# plot.py
build_decomposition_figure(result) -> matplotlib.figure.Figure   # 4 labeled, date-aligned axes
```

## Error Cases

| Condition | App behavior |
|-----------|--------------|
| `DATABASE_URL` unset / DB unreachable | Streamlit surfaces the connection error |
| Empty `daily_balance` | Warning, no chart |
| Series shorter than `2 * period` | Warning naming the minimum, no chart |
