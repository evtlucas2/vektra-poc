# Quickstart: Daily Balance Decomposition Chart

**Branch**: `005-balance-decomposition-chart` | **Date**: 2026-06-08

## Prerequisites

- Transactions loaded (`python -m src.cli <dir> <label>`) and daily balance computed
  (`python -m src.balance <initial-balance>`), so `daily_balance` has at least two weeks of
  data.
- `DATABASE_URL` set in `config/.env`.
- New dependencies installed:

```bash
pip install -r requirements.txt   # now includes streamlit, statsmodels, matplotlib, pandas
```

## Launching the App

```bash
streamlit run src/timeseries/app.py
```

Open the printed URL (default `http://localhost:8501`). You should see a four-panel chart:

1. **Observed** — line plot of the daily balance fluctuation
2. **Trend** — the longer-term direction
3. **Seasonal** — the repeating weekly pattern
4. **Residual** — what remains after removing trend and seasonal

Use the sidebar to change the seasonal period (default 7). Click **Download** to save the
chart as a PNG.

## Validating Without the UI (unit-level)

```bash
# Pure decomposition + figure + extract (mocked) — no Streamlit, no browser
pytest tests/unit/test_timeseries_decompose.py \
       tests/unit/test_timeseries_plot.py \
       tests/unit/test_timeseries_extract.py -v
```

Expected checks:
- `decompose_balance` returns observed/trend/seasonal/resid; additive recombination matches
  observed where defined.
- `decompose_balance` raises a clear `ValueError` for empty input and for fewer than two
  cycles.
- `build_decomposition_figure` returns a figure with four labeled axes.

## Integration Check (requires database)

```bash
DATABASE_URL="postgresql://..." pytest tests/integration/test_timeseries_pipeline.py
```

Seeds a daily balance series spanning several weeks, then asserts the decomposition produces
components of the expected length.

## Insufficient Data Behavior

If `daily_balance` has fewer than `2 × period` rows (14 for the weekly default), the app
shows a warning naming the minimum required and does not render a chart.

## Reference

- App contract: [contracts/app-interface.md](contracts/app-interface.md)
- Data model: [data-model.md](data-model.md)
- Research/decisions: [research.md](research.md)
