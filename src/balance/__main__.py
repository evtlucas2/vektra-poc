import os
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

from dotenv import load_dotenv

_ENV_FILE = Path(__file__).parent.parent.parent / "config" / ".env"

from src.balance.compute import compute_daily_balances
from src.balance.extract import fetch_daily_net
from src.balance.load import replace_daily_balances
from src.db.migrations import apply_migrations
from src.etl.load import db_connect


def _parse_initial_balance(args: list[str]) -> Decimal | None:
    if not args:
        print("[ERROR] Usage: python -m src.balance <initial-balance>", file=sys.stderr)
        return None
    try:
        return Decimal(args[0])
    except InvalidOperation:
        print("[ERROR] Initial balance must be a valid number.", file=sys.stderr)
        return None


def main(argv: list[str] | None = None) -> int:
    load_dotenv(_ENV_FILE)
    args = argv if argv is not None else sys.argv[1:]
    initial_balance = _parse_initial_balance(args)
    if initial_balance is None:
        return 1
    apply_migrations(os.environ.get("DATABASE_URL", ""))
    conn = db_connect()
    daily_net = fetch_daily_net(conn)
    if not daily_net:
        conn.close()
        print("[INFO] No transactions found. Nothing to do.")
        return 0
    rows = compute_daily_balances(daily_net, initial_balance)
    replace_daily_balances(conn, rows)
    conn.close()
    print(
        f"[INFO] Daily balance: {len(rows)} day(s) written from "
        f"{rows[0].balance_date} to {rows[-1].balance_date} (initial {initial_balance})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
