# Quickstart: Default Seasonality of 30 Days

**Branch**: `007-default-seasonality-30` | **Date**: 2026-06-11

## What Changed

- The decomposition's default seasonal period is now **30 days** (was 7).
- The Streamlit sidebar "Seasonal period (days)" now defaults to **30**.
- Using the default now needs at least **60** daily balance points (two 30-day cycles).
- The period is still user-overridable (e.g., set it back to 7 for a weekly view).

## Validation

```bash
# Automated
pytest tests/unit/test_timeseries_decompose.py -v
#   - DEFAULT_PERIOD == 30
#   - default path rejects < 60 points, accepts 60

# Manual (browser)
streamlit run src/timeseries/app.py
#   - sidebar period defaults to 30
#   - with < 60 days loaded and the default period, a warning appears (no chart)
#   - lowering the period (e.g., to 7) decomposes a shorter series again
```

## Reference

- Research/decisions: [research.md](research.md)
- Spec: [spec.md](spec.md)
