from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from psycopg2.extensions import connection as PgConnection

_AGGREGATE_SQL = """
SELECT effective_date, SUM(amount)
FROM transactions
GROUP BY effective_date
ORDER BY effective_date;
"""


def fetch_daily_net(conn: "PgConnection") -> dict[date, Decimal]:
    """Return the net transaction amount per effective_date across all accounts."""
    with conn.cursor() as cur:
        cur.execute(_AGGREGATE_SQL)
        return {row[0]: row[1] for row in cur.fetchall()}
