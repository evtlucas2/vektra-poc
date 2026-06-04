from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from src.etl.load import create_table_if_not_exists, insert_transactions
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


def test_create_table_if_not_exists_executes_ddl(mock_conn, cursor_mock):
    create_table_if_not_exists(mock_conn)
    cursor_mock.execute.assert_called_once()
    ddl = cursor_mock.execute.call_args[0][0]
    assert "CREATE TABLE IF NOT EXISTS transactions" in ddl
    assert "transaction_hash" in ddl
    mock_conn.commit.assert_called_once()


def test_insert_transactions_returns_inserted_count(mock_conn, cursor_mock):
    cursor_mock.rowcount = 1

    txns = [
        Transaction(
            posted_date=date(2026, 5, 10),
            effective_date=date(2026, 5, 10),
            description="SUPERMERCADO",
            amount=Decimal("-150.00"),
            transaction_hash="hash1",
        ),
        Transaction(
            posted_date=date(2026, 5, 15),
            effective_date=None,
            description="Deposito",
            amount=Decimal("5000.00"),
            transaction_hash="hash2",
        ),
    ]

    count = insert_transactions(mock_conn, txns)
    assert cursor_mock.execute.call_count == 2
    mock_conn.commit.assert_called_once()
    assert count == 2


def test_insert_transactions_empty_list_returns_zero(mock_conn, cursor_mock):
    count = insert_transactions(mock_conn, [])
    cursor_mock.execute.assert_not_called()
    assert count == 0
