CREATE TABLE IF NOT EXISTS transactions (
    id               SERIAL PRIMARY KEY,
    posted_date      DATE           NOT NULL,
    effective_date   DATE,
    description      TEXT,
    amount           NUMERIC(15, 2) NOT NULL,
    transaction_hash TEXT           NOT NULL,
    CONSTRAINT uq_transaction_hash UNIQUE (transaction_hash)
);
