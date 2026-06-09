from decimal import Decimal

import pytest

from src.balance.__main__ import _parse_initial_balance, main


def test_missing_argument_returns_none(capsys):
    assert _parse_initial_balance([]) is None
    assert "Usage" in capsys.readouterr().err


def test_invalid_argument_returns_none(capsys):
    assert _parse_initial_balance(["not-a-number"]) is None
    assert "valid number" in capsys.readouterr().err


@pytest.mark.parametrize("value", ["1000.00", "-250.75", "0"])
def test_valid_arguments_parse(value):
    assert _parse_initial_balance([value]) == Decimal(value)


def test_main_without_args_exits_1():
    assert main([]) == 1
