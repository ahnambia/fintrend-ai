-- What: A materialized view (sentiment_agg_15m) that joins sentiments with news_items, unnests tickers, and precomputes 15-minute aggregates per
-- ticker (avg score, counts).

-- Why: Continuous aggregates require a hypertable source; since we didn’t hypertable news_items, we use a materialized view to get the same fast
-- time-series queries today.

-- Long-run value: Your dashboard and signals engine can query a compact, indexed time series instead of re-aggregating raw rows.

-- How it relates: The API reads from this view to serve /sentiment/series.

BEGIN;

-- Unique guard (optional) to prevent multiple sentiments per news id.
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname='uq_sentiments_news') THEN
    CREATE UNIQUE INDEX uq_sentiments_news ON sentiments(news_id);
  END IF;
END$$;

CREATE MATERIALIZED VIEW IF NOT EXISTS sentiment_agg_15m AS
SELECT
  time_bucket('15 minutes', ni.published_at) AS bucket,
  t.ticker                                        AS ticker,
  COUNT(*)                                        AS n,
  AVG(s.score)                                    AS avg_score,
  SUM(CASE WHEN s.sentiment='pos' THEN 1 WHEN s.sentiment='neg' THEN -1 ELSE 0 END) AS net_votes,
  AVG(s.label_confidence)                         AS avg_conf
FROM sentiments s
JOIN news_items ni ON ni.id = s.news_id
JOIN LATERAL unnest(ni.tickers) AS t(ticker) ON TRUE
GROUP BY 1,2;

CREATE INDEX IF NOT EXISTS idx_sentiment_agg_15m_ticker_time ON sentiment_agg_15m (ticker, bucket DESC);

COMMIT;