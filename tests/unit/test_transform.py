from datetime import date
from decimal import Decimal

import pytest

from src.etl.transform import transform_transactions


def _raw(dtposted="20260510120000", name="Loja", memo="compra", trnamt="-50.00"):
    return {"DTPOSTED": dtposted, "NAME": name, "MEMO": memo, "TRNAMT": trnamt}


def test_filtered_names_are_excluded():
    rows = [
        _raw(name="Saldo do dia"),
        _raw(name="Saldo Anterior"),
        _raw(name="Loja Normal"),
    ]
    result = transform_transactions(rows, "checking")
    assert len(result) == 1
    assert result[0].description == "compra"


def test_account_label_stored_on_transaction():
    rows = [_raw()]
    result = transform_transactions(rows, "savings")
    assert result[0].account_label == "savings"


def test_memo_pattern_splits_date_and_description():
    rows = [_raw(dtposted="20260510120000", memo="10/05 14:30 SUPERMERCADO ABC")]
    result = transform_transactions(rows, "checking")
    assert len(result) == 1
    txn = result[0]
    assert txn.effective_date == date(2026, 5, 10)
    assert txn.description == "SUPERMERCADO ABC"


def test_memo_no_pattern_stores_full_memo():
    rows = [_raw(memo="Deposito salario")]
    result = transform_transactions(rows, "checking")
    assert result[0].effective_date is None
    assert result[0].description == "Deposito salario"


def test_posted_date_parsed_from_dtposted():
    rows = [_raw(dtposted="20260515000000")]
    result = transform_transactions(rows, "checking")
    assert result[0].posted_date == date(2026, 5, 15)


def test_amount_stored_as_decimal():
    rows = [_raw(trnamt="-150.50")]
    result = transform_transactions(rows, "checking")
    assert result[0].amount == Decimal("-150.50")


def test_hash_differs_by_account_label():
    row = _raw()
    r1 = transform_transactions([row], "checking")
    r2 = transform_transactions([row], "savings")
    assert r1[0].transaction_hash != r2[0].transaction_hash


def test_hash_consistent_same_label():
    row = _raw()
    r1 = transform_transactions([row], "checking")
    r2 = transform_transactions([row], "checking")
    assert r1[0].transaction_hash == r2[0].transaction_hash


def test_blank_memo_gives_null_description():
    rows = [_raw(memo="")]
    result = transform_transactions(rows, "checking")
    assert result[0].description is None
    assert result[0].effective_date is None
