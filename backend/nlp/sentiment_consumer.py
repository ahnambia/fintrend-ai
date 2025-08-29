''' What: A daemon that polls Postgres for unscored news_items, runs FinBERT in batches, and writes rows to sentiments with sentiment, 
score (signed), and label_confidence, exposing Prometheus counters on :9102.
Why: Keeping scoring asynchronous prevents your API from doing heavy ML work and keeps ingestion decoupled from scoring.
Long-run value: Scales horizontally (multiple workers, batch size tuning) and is resilient if producers burst.
How it relates: Sits between ingestion (Day 3) and analytics (rollups + API queries).'''

import os, time
from typing import List, Dict
import psycopg2, psycopg2.extras
from prometheus_client import Counter, Gauge, start_http_server
from nlp.sentiment_service import SentimentService

# Constants
DATABASE_URL = os.getenv("DATABASE_URL", "").replace("+psycopg2", "")
BATCH = int(os.getenv("SENT_BATCH", "24"))
SLEEP = float(os.getenv("SENT_IDLE_SLEEP_SEC", "3.0"))

# Metrics
SCORED   = Counter("fintrend_sent_scored_total", "Sentiment-scored news rows")
FAILED   = Counter("fintrend_sent_failed_total", "Sentiment scoring failures")
BACKLOG  = Gauge("fintrend_sent_backlog", "Unscored news backlog (rows)")

# SQL
SELECT_UNSCORED = """
SELECT ni.id AS news_id, ni.raw_title, ni.raw_text
FROM news_items ni
LEFT JOIN sentiments s ON s.news_id = ni.id
WHERE s.news_id IS NULL
ORDER BY ni.ingested_at ASC
LIMIT %s;
"""

INSERT_SENT = """
INSERT INTO sentiments (news_id, model, sentiment, score, label_confidence)
VALUES (%(news_id)s, %(model)s, %(sentiment)s, %(score)s, %(label_confidence)s)
ON CONFLICT DO NOTHING;
"""

def main():
    # Start metrics server
    start_http_server(9102)
    
    # Initialize services
    svc = SentimentService()
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    print("[worker_sentiment] up on :9102")

    while True:
        # Poll for backlog
        cur.execute("SELECT COUNT(*) AS c FROM news_items ni LEFT JOIN sentiments s ON s.news_id = ni.id WHERE s.news_id IS NULL;")
        backlog = cur.fetchone()["c"]
        BACKLOG.set(backlog)

        if backlog == 0:
            time.sleep(SLEEP)
            continue

        cur.execute(SELECT_UNSCORED, (BATCH,))
        rows: List[Dict] = cur.fetchall()
        try:
            scored = svc.score_batch(rows)
        except Exception as e:
            FAILED.inc(len(rows))
            print(f"[worker_sentiment] model failure: {e}")
            time.sleep(SLEEP)
            continue

        ok = 0
        for rec in scored:
            try:
                cur.execute(INSERT_SENT, rec)
                if cur.rowcount == 1: ok += 1
            except Exception as e:
                FAILED.inc()
                conn.rollback()
                print(f"[worker_sentiment] insert error: {e}")

        if ok: SCORED.inc(ok)

if __name__ == "__main__":
    main()


