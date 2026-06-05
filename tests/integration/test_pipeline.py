"""Integration tests — require DATABASE_URL to point to a real PostgreSQL database."""
import os
from pathlib import Path

import pytest

from src.db.migrations import apply_migrations
from src.etl.extract import extract_transactions
from src.etl.load import db_connect, insert_transactions
from src.etl.scan import scan
from src.etl.transform import transform_transactions

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.fixture(scope="module")
def conn():
    if "DATABASE_URL" not in os.environ:
        pytest.skip("DATABASE_URL not set — skipping integration tests")
    apply_migrations(os.environ["DATABASE_URL"])
    c = db_connect()
    yield c
    c.close()


@pytest.fixture(autouse=True)
def clean_table(conn):
    yield
    with conn.cursor() as cur:
        cur.execute("DELETE FROM transactions;")
    conn.commit()


def _load_directory(conn, directory: Path, label: str) -> int:
    files = scan(directory)
    total = 0
    for path in files:
        raw = extract_transactions(path)
        txns = transform_transactions(raw, label)
        total += insert_transactions(conn, txns)
    return total


def test_load_directory(conn):
    inserted = _load_directory(conn, FIXTURES / "multi", "checking")
    # january: 3, february: 2 (1 filtered "Saldo Anterior")
    assert inserted == 5


def test_empty_directory(conn):
    assert _load_directory(conn, FIXTURES / "empty_dir", "checking") == 0


def test_idempotent_reload(conn):
    first = _load_directory(conn, FIXTURES / "multi", "checking")
    second = _load_directory(conn, FIXTURES / "multi", "checking")
    assert second == 0

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM transactions;")
        assert cur.fetchone()[0] == first


def test_two_account_labels(conn):
    checking = _load_directory(conn, FIXTURES / "multi", "checking")
    savings = _load_directory(conn, FIXTURES / "multi", "savings")
    assert checking > 0
    assert savings == checking  # same file, different label → all inserted

    with conn.cursor() as cur:
        cur.execute(
            "SELECT account_label, COUNT(*) FROM transactions GROUP BY account_label ORDER BY account_label;"
        )
        rows = cur.fetchall()
    assert len(rows) == 2
    assert rows[0] == ("checking", checking)
    assert rows[1] == ("savings", savings)


def test_idempotent_reload_with_label(conn):
    first = _load_directory(conn, FIXTURES / "multi", "checking")
    second = _load_directory(conn, FIXTURES / "multi", "checking")
    assert second == 0

    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM transactions WHERE account_label = 'checking';"
        )
        assert cur.fetchone()[0] == first
