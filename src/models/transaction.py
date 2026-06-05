from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class Transaction:
    posted_date: date
    effective_date: date
    description: str | None
    amount: Decimal
    account_label: str
    transaction_hash: str
