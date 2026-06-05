import hashlib
import re
from datetime import date
from decimal import Decimal, InvalidOperation

from src.models.transaction import Transaction

FILTERED_NAMES: frozenset[str] = frozenset({"Saldo do dia", "Saldo Anterior"})

MEMO_PATTERN = re.compile(r"^(\d{1,2}/\d{1,2})\s+\d{1,2}:\d{2}\s+(.+)$")


def _parse_posted_date(dtposted: str) -> date:
    return date(int(dtposted[:4]), int(dtposted[4:6]), int(dtposted[6:8]))


def _parse_effective_date(day_month: str, year: int) -> date:
    day_str, month_str = day_month.split("/")
    return date(year, int(month_str), int(day_str))


def _compute_hash(dtposted: str, trnamt: str, memo: str, name: str, label: str) -> str:
    return hashlib.sha256(f"{dtposted}|{trnamt}|{memo}|{name}|{label}".encode()).hexdigest()


def _transform_row(row: dict, account_label: str) -> Transaction | None:
    if row["NAME"] in FILTERED_NAMES:
        return None
    try:
        posted_date = _parse_posted_date(row["DTPOSTED"])
        amount = Decimal(row["TRNAMT"])
    except (ValueError, InvalidOperation) as exc:
        print(f"[WARN] Skipped row: {exc} — row={row}", flush=True)
        return None
    memo = row["MEMO"]
    match = MEMO_PATTERN.match(memo) if memo else None
    effective_date = _parse_effective_date(match.group(1), posted_date.year) if match else None
    description: str | None = match.group(2) if match else (memo if memo else None)
    return Transaction(
        posted_date=posted_date,
        effective_date=effective_date,
        description=description,
        amount=amount,
        account_label=account_label,
        transaction_hash=_compute_hash(row["DTPOSTED"], row["TRNAMT"], memo, row["NAME"], account_label),
    )


def transform_transactions(raw: list[dict], account_label: str) -> list[Transaction]:
    return [t for row in raw if (t := _transform_row(row, account_label)) is not None]
