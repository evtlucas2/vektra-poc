"""Integration tests — require DATABASE_URL to point to a real PostgreSQL database."""
import os
from pathlib import Path

import psycopg2
import pytest

from src.etl.extract import extract_transactions
from src.etl.load import create_table_if_not_exists, db_connect, insert_transactions
from src.etl.scan import scan
from src.etl.transform import transform_transactions

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.fixture(scope="module")
def conn():
    if "DATABASE_URL" not in os.environ:
        pytest.skip("DATABASE_URL not set — skipping integration tests")
    c = db_connect()
    create_table_if_not_exists(c)
    yield c
    c.close()


@pytest.fixture(autouse=True)
def clean_table(conn):
    yield
    with conn.cursor() as cur:
        cur.execute("DELETE FROM transactions;")
    conn.commit()


def _load_directory(conn, directory: Path) -> int:
    files = scan(directory)
    total = 0
    for path in files:
        raw = extract_transactions(path)
        txns = transform_transactions(raw)
        total += insert_transactions(conn, txns)
    return total


def test_load_directory(conn):
    inserted = _load_directory(conn, FIXTURES / "multi")
    # january: 3 transactions, february: 2 (1 filtered "Saldo Anterior")
    assert inserted == 5


def test_empty_directory(conn):
    inserted = _load_directory(conn, FIXTURES / "empty_dir")
    assert inserted == 0


def test_idempotent_reload(conn):
    first = _load_directory(conn, FIXTURES / "multi")
    second = _load_directory(conn, FIXTURES / "multi")
    assert second == 0  # all conflict on transaction_hash

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM transactions;")
        count = cur.fetchone()[0]
    assert count == first
