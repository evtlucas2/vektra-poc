from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from psycopg2.extensions import connection as PgConnection

_SELECT_SQL = "SELECT balance_date, balance FROM daily_balance ORDER BY balance_date;"

_FRAME_SQL = (
    "SELECT balance_date, day_of_week, weekend, balance, difference "
    "FROM daily_balance ORDER BY balance_date;"
)

_FRAME_COLUMNS = ["balance_date", "day_of_week", "weekend", "balance", "difference"]


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


def fetch_daily_balance_frame(conn: "PgConnection") -> pd.DataFrame:
    """Return all daily_balance rows as a DataFrame ordered by date."""
    with conn.cursor() as cur:
        cur.execute(_FRAME_SQL)
        rows = cur.fetchall()
    frame = pd.DataFrame(rows, columns=_FRAME_COLUMNS)
    frame["difference"] = frame["difference"].astype(float)
    frame["balance"] = frame["balance"].astype(float)
    return frame
