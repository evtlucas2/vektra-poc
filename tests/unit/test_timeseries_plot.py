import matplotlib
import numpy as np
import pandas as pd
import pytest

matplotlib.use("Agg")  # headless backend for tests

from matplotlib.figure import Figure

from src.timeseries.decompose import decompose_balance
from src.timeseries.plot import build_decomposition_figure


def _result():
    n = 28
    idx = pd.date_range("2026-01-01", periods=n, freq="D")
    base = np.arange(n) * 5.0
    seasonal = np.tile([0, 10, 20, 30, 20, 10, 0], 4)
    return decompose_balance(pd.Series(base + seasonal, index=idx), period=7)


def test_returns_matplotlib_figure():
    fig = build_decomposition_figure(_result())
    assert isinstance(fig, Figure)


def test_figure_has_four_axes():
    fig = build_decomposition_figure(_result())
    assert len(fig.axes) == 4


def test_each_axis_has_label():
    fig = build_decomposition_figure(_result())
    labels = [ax.get_ylabel() or ax.get_title() for ax in fig.axes]
    assert all(label for label in labels)
    # First panel is the observed series
    joined = " ".join(labels).lower()
    assert "observed" in joined
    assert "trend" in joined
    assert "seasonal" in joined
    assert "residual" in joined
