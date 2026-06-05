ALTER TABLE transactions
    ADD COLUMN IF NOT EXISTS account_label TEXT NOT NULL DEFAULT 'unknown';
