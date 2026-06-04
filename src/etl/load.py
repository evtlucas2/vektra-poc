import os
from typing import TYPE_CHECKING

import psycopg2

if TYPE_CHECKING:
    from psycopg2.extensions import connection as PgConnection

from src.models.transaction import Transaction

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS transactions (
    id               SERIAL PRIMARY KEY,
    posted_date      DATE           NOT NULL,
    effective_date   DATE,
    description      TEXT,
    amount           NUMERIC(15, 2) NOT NULL,
    transaction_hash TEXT           NOT NULL,
    CONSTRAINT uq_transaction_hash UNIQUE (transaction_hash)
);
"""

_INSERT_SQL = """
INSERT INTO transactions (posted_date, effective_date, description, amount, transaction_hash)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (transaction_hash) DO NOTHING;
"""


def db_connect() -> "PgConnection":
    return psycopg2.connect(os.environ["DATABASE_URL"])


def create_table_if_not_exists(conn: "PgConnection") -> None:
    with conn.cursor() as cur:
        cur.execute(_CREATE_TABLE_SQL)
    conn.commit()


def insert_transactions(conn: "PgConnection", transactions: list[Transaction]) -> int:
    if not transactions:
        return 0
    inserted = 0
    with conn.cursor() as cur:
        for txn in transactions:
            cur.execute(
                _INSERT_SQL,
                (txn.posted_date, txn.effective_date, txn.description, txn.amount, txn.transaction_hash),
            )
            inserted += cur.rowcount
    conn.commit()
    return inserted
