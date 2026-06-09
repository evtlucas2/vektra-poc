"""Integration tests for the daily-balance pipeline — require DATABASE_URL."""
import os
from datetime import date
from decimal import Decimal

import pytest

from src.balance.compute import compute_daily_balances
from src.balance.extract import fetch_daily_net
from src.balance.load import replace_daily_balances
from src.db.migrations import apply_migrations
from src.etl.load import db_connect


@pytest.fixture(scope="module")
def conn():
    if "DATABASE_URL" not in os.environ:
        pytest.skip("DATABASE_URL not set — skipping integration tests")
    apply_migrations(os.environ["DATABASE_URL"])
    c = db_connect()
    yield c
    c.close()


@pytest.fixture(autouse=True)
def clean_tables(conn):
    yield
    with conn.cursor() as cur:
        cur.execute("DELETE FROM daily_balance;")
        cur.execute("DELETE FROM transactions;")
    conn.commit()


def _seed_transaction(conn, eff_date, amount, txn_hash):
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO transactions
               (posted_date, effective_date, description, amount, account_label, transaction_hash)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (eff_date, eff_date, "test", Decimal(amount), "checking", txn_hash),
        )
    conn.commit()


def _run_pipeline(conn, initial):
    daily_net = fetch_daily_net(conn)
    rows = compute_daily_balances(daily_net, Decimal(initial))
    replace_daily_balances(conn, rows)
    return rows


def test_generate_series(conn):
    # Jan 5 (+250), gap Jan 6, Jan 7 (-100)
    _seed_transaction(conn, date(2026, 1, 5), "250.00", "h1")
    _seed_transaction(conn, date(2026, 1, 7), "-100.00", "h2")

    _run_pipeline(conn, "1000.00")

    with conn.cursor() as cur:
        cur.execute(
            "SELECT balance_date, day_of_week, weekend, balance, difference "
            "FROM daily_balance ORDER BY balance_date;"
        )
        rows = cur.fetchall()

    assert len(rows) == 3  # Jan 5, 6, 7
    # Day 1: 1000 + 250 = 1250, diff 0
    assert rows[0] == (date(2026, 1, 5), 0, 0, Decimal("1250.00"), Decimal("0.00"))
    # Day 2 (gap): carries 1250, diff 0
    assert rows[1] == (date(2026, 1, 6), 1, 0, Decimal("1250.00"), Decimal("0.00"))
    # Day 3: 1250 - 100 = 1150, diff -100
    assert rows[2] == (date(2026, 1, 7), 2, 0, Decimal("1150.00"), Decimal("-100.00"))


def test_idempotent_rerun(conn):
    _seed_transaction(conn, date(2026, 1, 5), "250.00", "h1")
    _seed_transaction(conn, date(2026, 1, 7), "-100.00", "h2")

    _run_pipeline(conn, "1000.00")
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM daily_balance;")
        first = cur.fetchone()[0]

    _run_pipeline(conn, "1000.00")
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM daily_balance;")
        second = cur.fetchone()[0]

    assert first == second == 3
