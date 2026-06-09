from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from psycopg2.extensions import connection as PgConnection

from src.models.daily_balance import DailyBalance

_INSERT_SQL = """
INSERT INTO daily_balance (balance_date, day_of_week, weekend, balance, difference)
VALUES (%s, %s, %s, %s, %s);
"""


def replace_daily_balances(conn: "PgConnection", rows: list[DailyBalance]) -> int:
    """Replace the entire daily_balance series with rows. Returns count inserted."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM daily_balance;")
        for row in rows:
            cur.execute(
                _INSERT_SQL,
                (row.balance_date, row.day_of_week, row.weekend, row.balance, row.difference),
            )
    conn.commit()
    return len(rows)
