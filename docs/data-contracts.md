# Data Contracts

## news_items
- id: uuid (pk)
- source: text
- url: text (unique)
- published_at: timestamptz
- raw_title: text
- raw_text: text
- tickers: text[]        # e.g., {"AAPL","MSFT"}
- lang: text
- ingested_at: timestamptz (default now)

Indexes: (published_at), unique(url)

## sentiments
- id: uuid (pk)
- news_id: uuid (fk → news_items.id)
- model: text
- sentiment: enum('pos','neu','neg')
- score: double precision
- label_confidence: double precision
- run_ts: timestamptz (default now)

Indexes: (news_id)

## prices
- id: bigserial (pk)
- ticker: text
- ts: timestamptz
- open, high, low, close: numeric
- volume: bigint

Indexes: (ticker, ts)

## sentiment_agg (continuous aggregate)
- ticker: text
- bucket_start: timestamptz
- pos_count, neg_count, neu_count: integer
- avg_score: double precision
- ewma_score: double precision

## signals
- id: uuid (pk)
- ticker: text
- ts: timestamptz
- signal: enum('bullish','bearish','neutral')
- horizon: text   # e.g., '1h','1d'
- confidence: double precision
- features_json: jsonb
- explain: text

Indexes: (ticker, ts)
