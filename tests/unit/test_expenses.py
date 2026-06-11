from datetime import date

import pandas as pd
import pytest

from src.timeseries.expenses import EXPENSE_PERCENTILE, top_expense_days


def _frame(diffs):
    """Build a daily_balance-like frame from a list of difference values."""
    n = len(diffs)
    return pd.DataFrame({
        "balance_date": pd.date_range("2026-01-01", periods=n, freq="D").date,
        "day_of_week": [0] * n,
        "weekend": [0] * n,
        "balance": [1000.0] * n,
        "difference": [float(d) for d in diffs],
    })


def test_expense_percentile_constant():
    assert EXPENSE_PERCENTILE == 5


def test_empty_frame_returns_empty():
    result = top_expense_days(_frame([]))
    assert result.empty


def test_all_non_negative_returns_empty():
    # No expense days (every difference >= 0)
    result = top_expense_days(_frame([0, 5, 10, 0, 3]))
    assert result.empty


def test_selects_only_low_tail_below_threshold():
    # 20 days: one extreme expense (-100) plus mild moves
    diffs = [-100] + [-1] * 9 + [1] * 10
    result = top_expense_days(_frame(diffs))
    threshold = _frame(diffs)["difference"].quantile(0.05)
    assert (result["difference"] <= threshold).all()
    assert (result["difference"] < 0).all()


def test_adds_positive_expense_column():
    result = top_expense_days(_frame([-100] + [-1] * 9 + [1] * 10))
    assert "expense" in result.columns
    assert (result["expense"] > 0).all()
    # expense is the magnitude of the negative difference
    assert result.iloc[0]["expense"] == 100.0


def test_sorted_expense_descending():
    diffs = [-100, -80, -60] + [1] * 17
    result = top_expense_days(_frame(diffs))
    expenses = list(result["expense"])
    assert expenses == sorted(expenses, reverse=True)


def test_non_empty_guard_min_always_included():
    # Only 3 days; 5% rounds below 1, but the single largest expense must still appear
    result = top_expense_days(_frame([-50, -10, 5]))
    assert len(result) >= 1
    assert result.iloc[0]["expense"] == 50.0
