-- 002_indexes.sql
-- Purpose: make prices a proper hypertable with a composite PK (ticker, ts)
-- and add the key indexes to keep ingestion/query paths fast.

BEGIN;

-- --- PRICES: ensure hypertable + proper PK and helpful index ---
-- Drop old PK if it exists (safe if it doesn't).
ALTER TABLE IF EXISTS prices DROP CONSTRAINT IF EXISTS prices_pkey;

-- Enforce NOT NULL on partition + dimension columns.
ALTER TABLE IF EXISTS prices
  ALTER COLUMN ticker SET NOT NULL,
  ALTER COLUMN ts     SET NOT NULL;

-- Create hypertable if not already created.
-- (Timescale requires a unique index/PK that includes 'ts'.)
SELECT create_hypertable('prices','ts', if_not_exists => TRUE);

-- Composite primary key including time column.
ALTER TABLE IF EXISTS prices
  ADD CONSTRAINT prices_pkey PRIMARY KEY (ticker, ts);

-- Helpful query pattern index (latest-first per ticker).
CREATE INDEX IF NOT EXISTS idx_prices_ticker_ts_desc ON prices (ticker, ts DESC);

-- --- NEWS: dedupe + fast recency queries ---
-- Normalize URL to lowercase to avoid duplicate-casing issues.
CREATE UNIQUE INDEX IF NOT EXISTS idx_news_url_unique ON news_items ((lower(url)));

-- Speed up "latest news" queries.
CREATE INDEX IF NOT EXISTS idx_news_published_at ON news_items (published_at DESC);

-- --- SENTIMENTS: FK join speed ---
CREATE INDEX IF NOT EXISTS idx_sentiments_news_id ON sentiments (news_id);

-- --- SIGNALS: timeline queries per ticker ---
CREATE INDEX IF NOT EXISTS idx_signals_ticker_ts ON signals (ticker, ts);

COMMIT;
