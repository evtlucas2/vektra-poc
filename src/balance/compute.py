from datetime import date, timedelta
from decimal import Decimal

from src.models.daily_balance import DailyBalance

WEEKEND_DAYS: frozenset[int] = frozenset({5, 6})  # Saturday, Sunday


def _build_row(day: date, balance: Decimal, difference: Decimal) -> DailyBalance:
    weekday = day.weekday()
    return DailyBalance(
        balance_date=day,
        day_of_week=weekday,
        weekend=1 if weekday in WEEKEND_DAYS else 0,
        balance=balance,
        difference=difference,
    )


def compute_daily_balances(
    daily_net: dict[date, Decimal], initial_balance: Decimal
) -> list[DailyBalance]:
    """Build a gap-filled running daily balance series. Pure function (no I/O)."""
    if not daily_net:
        return []
    current, end = min(daily_net), max(daily_net)
    rows: list[DailyBalance] = []
    prev_balance: Decimal | None = None
    while current <= end:
        net = daily_net.get(current, Decimal("0"))
        balance = (initial_balance if prev_balance is None else prev_balance) + net
        difference = Decimal("0") if prev_balance is None else balance - prev_balance
        rows.append(_build_row(current, balance, difference))
        prev_balance = balance
        current += timedelta(days=1)
    return rows
