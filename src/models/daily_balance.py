from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class DailyBalance:
    balance_date: date
    day_of_week: int
    weekend: int
    balance: Decimal
    difference: Decimal
