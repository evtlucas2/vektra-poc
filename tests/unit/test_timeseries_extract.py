from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.timeseries.extract import fetch_balance_series, fetch_daily_balance_frame


@pytest.fixture
def cursor_mock():
    return MagicMock()


@pytest.fixture
def mock_conn(cursor_mock):
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor_mock
    conn.cursor.return_value.__exit__.return_value = False
    return conn


def test_fetch_balance_series_returns_float_series_indexed_by_date(mock_conn, cursor_mock):
    cursor_mock.fetchall.return_value = [
        (date(2026, 1, 5), Decimal("1000.00")),
        (date(2026, 1, 6), Decimal("1100.00")),
        (date(2026, 1, 7), Decimal("900.00")),
    ]
    series = fetch_balance_series(mock_conn)

    assert isinstance(series, pd.Series)
    assert len(series) == 3
    assert isinstance(series.index, pd.DatetimeIndex)
    assert series.iloc[0] == 1000.0
    assert series.dtype == float


def test_fetch_balance_series_empty(mock_conn, cursor_mock):
    cursor_mock.fetchall.return_value = []
    series = fetch_balance_series(mock_conn)
    assert isinstance(series, pd.Series)
    assert len(series) == 0


def test_fetch_daily_balance_frame_returns_dataframe(mock_conn, cursor_mock):
    cursor_mock.fetchall.return_value = [
        (date(2026, 1, 5), 0, 0, Decimal("1000.00"), Decimal("0.00")),
        (date(2026, 1, 6), 1, 0, Decimal("900.00"), Decimal("-100.00")),
    ]
    frame = fetch_daily_balance_frame(mock_conn)

    assert isinstance(frame, pd.DataFrame)
    assert list(frame.columns) == [
        "balance_date", "day_of_week", "weekend", "balance", "difference"
    ]
    assert len(frame) == 2
    assert float(frame.iloc[1]["difference"]) == -100.0


def test_fetch_daily_balance_frame_empty(mock_conn, cursor_mock):
    cursor_mock.fetchall.return_value = []
    frame = fetch_daily_balance_frame(mock_conn)
    assert isinstance(frame, pd.DataFrame)
    assert frame.empty
    assert list(frame.columns) == [
        "balance_date", "day_of_week", "weekend", "balance", "difference"
    ]
