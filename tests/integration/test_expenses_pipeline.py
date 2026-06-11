"""Integration test for the top-expense-days selection — requires DATABASE_URL."""
import os
from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.db.migrations import apply_migrations
from src.etl.load import db_connect
from src.timeseries.expenses import top_expense_days
from src.timeseries.extract import fetch_daily_balance_frame


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


def _seed(conn, diffs):
    start = date(2026, 1, 1)
    with conn.cursor() as cur:
        for i, d in enumerate(diffs):
            day = start + timedelta(days=i)
            cur.execute(
                """INSERT INTO daily_balance
                   (balance_date, day_of_week, weekend, balance, difference)
                   VALUES (%s, %s, %s, %s, %s)""",
                (day, day.weekday(), 1 if day.weekday() >= 5 else 0,
                 Decimal("1000.00"), Decimal(str(d))),
            )
    conn.commit()


def test_top_expense_days(conn):
    # 20 days: one extreme expense (-500) is the clear top; mild noise otherwise
    diffs = [-500] + [-1] * 9 + [1] * 10
    _seed(conn, diffs)

    frame = fetch_daily_balance_frame(conn)
    result = top_expense_days(frame)

    assert len(result) >= 1
    # Largest expense first, and it is the -500 day
    assert result.iloc[0]["expense"] == 500.0
    assert result.iloc[0]["balance_date"] == date(2026, 1, 1)
    # All selected rows are expenses, sorted descending
    expenses = list(result["expense"])
    assert expenses == sorted(expenses, reverse=True)
    assert all(e > 0 for e in expenses)
