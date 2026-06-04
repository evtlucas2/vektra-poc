from pathlib import Path

import pytest

from src.etl.extract import extract_transactions

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_extract_returns_list_of_dicts():
    result = extract_transactions(FIXTURES / "single" / "sample.ofx")
    assert isinstance(result, list)
    assert all(isinstance(r, dict) for r in result)


def test_extract_correct_field_keys():
    result = extract_transactions(FIXTURES / "single" / "sample.ofx")
    for row in result:
        assert "DTPOSTED" in row
        assert "TRNAMT" in row
        assert "NAME" in row
        assert "MEMO" in row


def test_extract_correct_row_count():
    # sample.ofx has 3 STMTTRN elements (including "Saldo do dia")
    result = extract_transactions(FIXTURES / "single" / "sample.ofx")
    assert len(result) == 3


def test_extract_ignores_header_before_ofx_tag():
    # File has plain-text SGML header — must not raise
    result = extract_transactions(FIXTURES / "single" / "sample.ofx")
    assert len(result) > 0
