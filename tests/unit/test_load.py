from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from src.etl.load import insert_transactions
from src.models.transaction import Transaction


@pytest.fixture
def cursor_mock():
    return MagicMock()


@pytest.fixture
def mock_conn(cursor_mock):
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor_mock
    conn.cursor.return_value.__exit__.return_value = False
    return conn


def _txn(label: str = "checking", hash_val: str = "hash1") -> Transaction:
    return Transaction(
        posted_date=date(2026, 5, 10),
        effective_date=date(2026, 5, 10),
        description="SUPERMERCADO",
        amount=Decimal("-150.00"),
        account_label=label,
        transaction_hash=hash_val,
    )


def test_insert_includes_account_label(mock_conn, cursor_mock):
    cursor_mock.rowcount = 1
    insert_transactions(mock_conn, [_txn("checking", "h1")])
    call_args = cursor_mock.execute.call_args[0]
    sql, params = call_args[0], call_args[1]
    assert "account_label" in sql
    assert "checking" in params


def test_insert_transactions_returns_inserted_count(mock_conn, cursor_mock):
    cursor_mock.rowcount = 1
    count = insert_transactions(mock_conn, [_txn("a", "h1"), _txn("b", "h2")])
    assert cursor_mock.execute.call_count == 2
    mock_conn.commit.assert_called_once()
    assert count == 2


def test_insert_transactions_empty_list_returns_zero(mock_conn, cursor_mock):
    count = insert_transactions(mock_conn, [])
    cursor_mock.execute.assert_not_called()
    assert count == 0
