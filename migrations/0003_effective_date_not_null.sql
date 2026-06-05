-- Backfill existing null effective_date values with posted_date
UPDATE transactions
SET effective_date = posted_date
WHERE effective_date IS NULL;

-- Enforce NOT NULL now that no nulls remain
ALTER TABLE transactions
    ALTER COLUMN effective_date SET NOT NULL;
