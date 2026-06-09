from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from psycopg2.extensions import connection as PgConnection

_SELECT_SQL = "SELECT balance_date, balance FROM daily_balance ORDER BY balance_date;"


def fetch_balance_series(conn: "PgConnection") -> pd.Series:
    """Return the daily balance as a float Series indexed by date (daily frequency)."""
    with conn.cursor() as cur:
        cur.execute(_SELECT_SQL)
        rows = cur.fetchall()
    if not rows:
        return pd.Series(dtype=float)
    index = pd.DatetimeIndex([row[0] for row in rows], freq="D")
    values = [float(row[1]) for row in rows]
    return pd.Series(values, index=index, dtype=float)
