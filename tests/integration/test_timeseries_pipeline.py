"""Integration test for the decomposition pipeline — requires DATABASE_URL."""
import os
from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.db.migrations import apply_migrations
from src.etl.load import db_connect
from src.timeseries.decompose import decompose_balance
from src.timeseries.extract import fetch_balance_series


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
        cur.execute("DELETE FROM daily_balance;")
    conn.commit()


def _seed_daily_balance(conn, days=28):
    start = date(2026, 1, 1)
    with conn.cursor() as cur:
        for i in range(days):
            d = start + timedelta(days=i)
            balance = Decimal("1000.00") + Decimal(i * 5)
            cur.execute(
                """INSERT INTO daily_balance
                   (balance_date, day_of_week, weekend, balance, difference)
                   VALUES (%s, %s, %s, %s, %s)""",
                (d, d.weekday(), 1 if d.weekday() >= 5 else 0, balance, Decimal("5.00")),
            )
    conn.commit()


def test_extract_and_decompose(conn):
    _seed_daily_balance(conn, days=28)

    series = fetch_balance_series(conn)
    assert len(series) == 28

    result = decompose_balance(series, period=7)
    assert len(result.observed) == 28
    assert len(result.seasonal) == 28
