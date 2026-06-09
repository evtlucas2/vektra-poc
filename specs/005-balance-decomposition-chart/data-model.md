# Data Model: Daily Balance Decomposition Chart

**Branch**: `005-balance-decomposition-chart` | **Date**: 2026-06-08

This feature introduces **no database schema changes**. It reads the existing
`daily_balance` table and works with in-memory time-series structures.

## Input: Balance Series (in-memory)

Built by `extract.fetch_balance_series(conn)`:

| Aspect | Detail |
|--------|--------|
| Type | `pandas.Series` of `float` |
| Index | `DatetimeIndex`, daily frequency (`freq="D"`) |
| Values | `balance` from `daily_balance`, cast to float |
| Order | Ascending by `balance_date` |
| Source query | `SELECT balance_date, balance FROM daily_balance ORDER BY balance_date` |

Because `daily_balance` is gap-filled (one row per calendar day), the series is regular with
no missing dates.

## Computation: Decomposition Result

Produced by `decompose.decompose_balance(series, period=7)`:

| Component | Type | Meaning |
|-----------|------|---------|
| `observed` | pandas Series | The input daily balance |
| `trend` | pandas Series | Longer-term direction (NaN at the ends where the window is incomplete) |
| `seasonal` | pandas Series | Repeating weekly pattern |
| `resid` | pandas Series | Remainder = observed − trend − seasonal |

Validation rules:

- Empty series → `ValueError("no daily balance data")`
- `len(series) < 2 * period` → `ValueError("need at least {2*period} data points; got {n}")`
- Model is additive: `observed ≈ trend + seasonal + resid` where all are defined

## Output: Decomposition Figure (artifact)

Produced by `plot.build_decomposition_figure(result)`:

| Aspect | Detail |
|--------|--------|
| Type | `matplotlib.figure.Figure` |
| Panels | 4 stacked subplots, shared x-axis (date) |
| Panel order | (1) Observed daily balance (line plot), (2) Trend, (3) Seasonal, (4) Residual |
| Labels | Each subplot titled/labeled with its component name |

The Streamlit app renders this Figure and offers it as a downloadable PNG.

## Entities Summary

- **Daily Balance** (existing table, read-only) — source of the series.
- **Balance Series** (in-memory pandas Series) — regular daily series fed to decomposition.
- **Decomposition Result** (in-memory) — observed/trend/seasonal/resid components.
- **Decomposition Figure** (artifact) — the four-panel chart shown and downloadable.
