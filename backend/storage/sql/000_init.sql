CREATE TABLE IF NOT EXISTS news_items (
    id UUID PRIMARY KEY,
    source TEXT,
    url TEXT UNIQUE,
    published_at TIMESTAMPTZ,
    raw_title TEXT,
    raw_text TEXT,
    tickers TEXT[],
    lang TEXT,
    ingested_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sentiments (
    id UUID PRIMARY KEY,
    news_id UUID REFERENCES news_items(id),
    model TEXT,
    sentiment TEXT,
    score DOUBLE PRECISION,
    label_confidence DOUBLE PRECISION,
    run_ts TIMESTAMPTZ DEFAULT now()
);

-- prices: composite PK that includes the time column
CREATE TABLE IF NOT EXISTS prices (
  ticker TEXT NOT NULL,
  ts TIMESTAMPTZ NOT NULL,
  open NUMERIC,
  high NUMERIC,
  low NUMERIC,
  close NUMERIC,
  volume BIGINT,
  id BIGSERIAL,                     -- optional surrogate key (not PK)
  PRIMARY KEY (ticker, ts)
);


CREATE TABLE IF NOT EXISTS signals (
    id UUID PRIMARY KEY,
    ticker TEXT,
    ts TIMESTAMPTZ,
    signal TEXT,
    horizon TEXT,
    confidence DOUBLE PRECISION,
    features_json JSONB,
    explain TEXT
);


