from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from src.balance.load import replace_daily_balances
from src.models.daily_balance import DailyBalance


@pytest.fixture
def cursor_mock():
    return MagicMock()


@pytest.fixture
def mock_conn(cursor_mock):
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor_mock
    conn.cursor.return_value.__exit__.return_value = False
    return conn


def _row(d=date(2026, 1, 5)):
    return DailyBalance(d, 0, 0, Decimal("1000.00"), Decimal("0"))


def test_replace_deletes_then_inserts(mock_conn, cursor_mock):
    rows = [_row(date(2026, 1, 5)), _row(date(2026, 1, 6))]
    replace_daily_balances(mock_conn, rows)

    statements = [c.args[0] for c in cursor_mock.execute.call_args_list]
    assert any("DELETE FROM daily_balance" in s for s in statements)
    insert_count = sum(1 for s in statements if "INSERT INTO daily_balance" in s)
    assert insert_count == 2
    mock_conn.commit.assert_called_once()


def test_replace_empty_rows_only_deletes(mock_conn, cursor_mock):
    replace_daily_balances(mock_conn, [])
    statements = [c.args[0] for c in cursor_mock.execute.call_args_list]
    assert any("DELETE FROM daily_balance" in s for s in statements)
    assert not any("INSERT INTO daily_balance" in s for s in statements)
    mock_conn.commit.assert_called_once()
