from datetime import date
from decimal import Decimal

import pytest

from src.balance.compute import compute_daily_balances


def test_empty_input_returns_empty_list():
    assert compute_daily_balances({}, Decimal("1000.00")) == []


def test_first_day_balance_is_initial_plus_net_and_difference_zero():
    daily_net = {date(2026, 1, 5): Decimal("250.00")}
    rows = compute_daily_balances(daily_net, Decimal("1000.00"))
    assert len(rows) == 1
    assert rows[0].balance == Decimal("1250.00")
    assert rows[0].difference == Decimal("0")


def test_subsequent_day_balance_and_difference():
    daily_net = {
        date(2026, 1, 5): Decimal("250.00"),
        date(2026, 1, 6): Decimal("-100.00"),
    }
    rows = compute_daily_balances(daily_net, Decimal("1000.00"))
    assert rows[1].balance == Decimal("1150.00")
    assert rows[1].difference == Decimal("-100.00")


def test_gap_day_carries_previous_balance_with_zero_difference():
    daily_net = {
        date(2026, 1, 5): Decimal("250.00"),
        date(2026, 1, 7): Decimal("50.00"),
    }
    rows = compute_daily_balances(daily_net, Decimal("1000.00"))
    # 3 days: 05, 06 (gap), 07
    assert len(rows) == 3
    assert rows[1].balance_date == date(2026, 1, 6)
    assert rows[1].balance == Decimal("1250.00")  # same as day before
    assert rows[1].difference == Decimal("0")


def test_day_of_week_python_convention():
    # 2026-01-05 is a Monday
    rows = compute_daily_balances({date(2026, 1, 5): Decimal("0")}, Decimal("0"))
    assert rows[0].day_of_week == 0  # Monday


def test_weekend_flag_saturday_and_sunday():
    # 2026-01-10 = Saturday (5), 2026-01-11 = Sunday (6)
    daily_net = {date(2026, 1, 10): Decimal("0"), date(2026, 1, 11): Decimal("0")}
    rows = compute_daily_balances(daily_net, Decimal("0"))
    assert rows[0].day_of_week == 5 and rows[0].weekend == 1
    assert rows[1].day_of_week == 6 and rows[1].weekend == 1


def test_weekday_not_flagged_weekend():
    # 2026-01-07 = Wednesday (2)
    rows = compute_daily_balances({date(2026, 1, 7): Decimal("0")}, Decimal("0"))
    assert rows[0].day_of_week == 2
    assert rows[0].weekend == 0


def test_negative_net_gives_negative_difference():
    daily_net = {
        date(2026, 1, 5): Decimal("0"),
        date(2026, 1, 6): Decimal("-300.00"),
    }
    rows = compute_daily_balances(daily_net, Decimal("500.00"))
    assert rows[1].difference == Decimal("-300.00")


def test_one_row_per_calendar_day_in_range():
    daily_net = {date(2026, 1, 1): Decimal("0"), date(2026, 1, 31): Decimal("0")}
    rows = compute_daily_balances(daily_net, Decimal("0"))
    assert len(rows) == 31  # Jan 1 .. Jan 31 inclusive
