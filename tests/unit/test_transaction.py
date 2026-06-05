from datetime import date
from decimal import Decimal

from src.models.transaction import Transaction


def test_transaction_fields_all_present():
    t = Transaction(
        posted_date=date(2026, 5, 10),
        effective_date=date(2026, 5, 10),
        description="SUPERMERCADO ABC",
        amount=Decimal("-150.00"),
        account_label="checking",
        transaction_hash="abc123",
    )
    assert t.posted_date == date(2026, 5, 10)
    assert t.effective_date == date(2026, 5, 10)
    assert t.description == "SUPERMERCADO ABC"
    assert t.amount == Decimal("-150.00")
    assert t.account_label == "checking"
    assert t.transaction_hash == "abc123"


def test_transaction_nullable_fields_accept_none():
    t = Transaction(
        posted_date=date(2026, 5, 10),
        effective_date=None,
        description=None,
        amount=Decimal("5000.00"),
        account_label="savings",
        transaction_hash="def456",
    )
    assert t.effective_date is None
    assert t.description is None
    assert t.account_label == "savings"
