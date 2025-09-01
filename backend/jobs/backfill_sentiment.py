import os, argparse
import psycopg2, psycopg2.extras
from nlp.sentiment_service import SentimentService

DATABASE_URL = os.getenv("DATABASE_URL", "").replace("+psycopg2", "")

SELECT = """
SELECT ni.id AS news_id, ni.raw_title, ni.raw_text
FROM news_items ni
LEFT JOIN sentiments s ON s.news_id = ni.id
WHERE s.news_id IS NULL
ORDER BY ni.ingested_at ASC
LIMIT %s;
"""

INSERT = """
INSERT INTO sentiments (news_id, model, sentiment, score, label_confidence)
VALUES (%(news_id)s, %(model)s, %(sentiment)s, %(score)s, %(label_confidence)s)
ON CONFLICT DO NOTHING;
"""

def main(limit: int, batch: int):
    svc = SentimentService()
    conn = psycopg2.connect(DATABASE_URL); conn.autocommit = True
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    total = 0
    while total < limit:
        cur.execute(SELECT, (min(batch, limit-total),))
        rows = cur.fetchall()
        if not rows: break
        scored = svc.score_batch(rows)
        for rec in scored:
            cur.execute(INSERT, rec)
        total += len(rows)
        print(f"[backfill] scored {total}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=500)
    ap.add_argument("--batch", type=int, default=32)
    args = ap.parse_args()
    main(args.limit, args.batch)

