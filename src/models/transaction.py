from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class Transaction:
    posted_date: date
    effective_date: date | None
    description: str | None
    amount: Decimal
    transaction_hash: str
