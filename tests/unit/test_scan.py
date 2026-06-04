from pathlib import Path

import pytest

from src.etl.scan import scan


def test_scan_returns_ofx_files(tmp_path):
    (tmp_path / "january.ofx").touch()
    (tmp_path / "february.ofx").touch()
    (tmp_path / "notes.txt").touch()

    result = scan(tmp_path)

    assert len(result) == 2
    assert all(p.suffix.lower() == ".ofx" for p in result)


def test_scan_returns_sorted_list(tmp_path):
    (tmp_path / "b.ofx").touch()
    (tmp_path / "a.ofx").touch()
    (tmp_path / "c.ofx").touch()

    result = scan(tmp_path)

    assert [p.name for p in result] == ["a.ofx", "b.ofx", "c.ofx"]


def test_scan_empty_directory_returns_empty_list(tmp_path):
    assert scan(tmp_path) == []


def test_scan_case_insensitive_extension(tmp_path):
    (tmp_path / "upper.OFX").touch()
    (tmp_path / "lower.ofx").touch()

    result = scan(tmp_path)

    assert len(result) == 2
