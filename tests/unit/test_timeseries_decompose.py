import numpy as np
import pandas as pd
import pytest

from src.timeseries.decompose import DEFAULT_PERIOD, decompose_balance


def _weekly_series(weeks=4):
    n = weeks * 7
    idx = pd.date_range("2026-01-01", periods=n, freq="D")
    # trend + weekly seasonal pattern
    base = np.arange(n) * 5.0
    seasonal = np.tile([0, 10, 20, 30, 20, 10, 0], weeks)
    return pd.Series(base + seasonal, index=idx)


def test_default_period_is_thirty():
    assert DEFAULT_PERIOD == 30


def _daily_series(n):
    idx = pd.date_range("2026-01-01", periods=n, freq="D")
    return pd.Series(np.arange(n) * 1.0, index=idx)


def test_default_requires_sixty_points():
    # With the default 30-day period, two cycles = 60 points are required.
    with pytest.raises(ValueError, match="60"):
        decompose_balance(_daily_series(59))  # no period override -> uses default 30
    # Exactly 60 points succeeds at the default period.
    result = decompose_balance(_daily_series(60))
    assert len(result.observed) == 60


def test_returns_four_components():
    result = decompose_balance(_weekly_series(), period=7)
    assert result.observed is not None
    assert result.trend is not None
    assert result.seasonal is not None
    assert result.resid is not None


def test_additive_recombination_matches_observed():
    result = decompose_balance(_weekly_series(), period=7)
    recombined = result.trend + result.seasonal + result.resid
    # Compare only where all components are defined (trend/resid NaN at the ends)
    mask = recombined.notna()
    assert np.allclose(recombined[mask].values, result.observed[mask].values, atol=1e-6)


def test_empty_series_raises_value_error():
    with pytest.raises(ValueError, match="no daily balance data"):
        decompose_balance(pd.Series(dtype=float), period=7)


def test_insufficient_data_raises_value_error():
    short = _weekly_series(weeks=1)  # 7 points, need >= 14 for period 7
    with pytest.raises(ValueError, match="at least 14"):
        decompose_balance(short, period=7)


def test_exactly_two_cycles_is_allowed():
    series = _weekly_series(weeks=2)  # 14 points == 2 * 7
    result = decompose_balance(series, period=7)
    assert len(result.observed) == 14
