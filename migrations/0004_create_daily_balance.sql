CREATE TABLE IF NOT EXISTS daily_balance (
    balance_date  DATE           PRIMARY KEY,
    day_of_week   SMALLINT       NOT NULL,
    weekend       SMALLINT       NOT NULL,
    balance       NUMERIC(15, 2) NOT NULL,
    difference    NUMERIC(15, 2) NOT NULL
);
