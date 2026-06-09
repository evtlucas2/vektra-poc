from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from src.balance.extract import fetch_daily_net


@pytest.fixture
def cursor_mock():
    return MagicMock()


@pytest.fixture
def mock_conn(cursor_mock):
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor_mock
    conn.cursor.return_value.__exit__.return_value = False
    return conn


def test_fetch_daily_net_returns_dict(mock_conn, cursor_mock):
    cursor_mock.fetchall.return_value = [
        (date(2026, 1, 5), Decimal("250.00")),
        (date(2026, 1, 6), Decimal("-100.00")),
    ]
    result = fetch_daily_net(mock_conn)
    assert result == {
        date(2026, 1, 5): Decimal("250.00"),
        date(2026, 1, 6): Decimal("-100.00"),
    }
    cursor_mock.execute.assert_called_once()
    sql = cursor_mock.execute.call_args[0][0]
    assert "SUM(amount)" in sql
    assert "GROUP BY effective_date" in sql


def test_fetch_daily_net_empty(mock_conn, cursor_mock):
    cursor_mock.fetchall.return_value = []
    assert fetch_daily_net(mock_conn) == {}
