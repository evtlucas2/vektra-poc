from datetime import date
from decimal import Decimal

from src.models.daily_balance import DailyBalance


def test_daily_balance_fields_all_present():
    row = DailyBalance(
        balance_date=date(2026, 1, 5),
        day_of_week=0,
        weekend=0,
        balance=Decimal("1000.00"),
        difference=Decimal("0"),
    )
    assert row.balance_date == date(2026, 1, 5)
    assert row.day_of_week == 0
    assert row.weekend == 0
    assert row.balance == Decimal("1000.00")
    assert row.difference == Decimal("0")


def test_daily_balance_accepts_negative_difference():
    row = DailyBalance(
        balance_date=date(2026, 1, 6),
        day_of_week=1,
        weekend=0,
        balance=Decimal("800.00"),
        difference=Decimal("-200.00"),
    )
    assert row.difference == Decimal("-200.00")
