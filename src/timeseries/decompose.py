import pandas as pd
from statsmodels.tsa.seasonal import DecomposeResult, seasonal_decompose

DEFAULT_PERIOD = 7  # weekly seasonality


def decompose_balance(series: pd.Series, period: int = DEFAULT_PERIOD) -> DecomposeResult:
    """Additively decompose the balance series into trend, seasonal, residual.

    Raises ValueError when the series is empty or shorter than two full periods.
    """
    if series.empty:
        raise ValueError("no daily balance data")
    minimum = 2 * period
    if len(series) < minimum:
        raise ValueError(f"need at least {minimum} data points; got {len(series)}")
    return seasonal_decompose(series, model="additive", period=period)
