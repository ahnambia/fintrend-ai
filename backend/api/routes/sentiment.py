from typing import List, Dict
from fastapi import APIRouter, HTTPException, Query
import os, psycopg2, psycopg2.extras

# This file contains routes for sentiment analysis
router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL", "").replace("+psycopg2", "")

def _conn():
    return psycopg2.connect(DATABASE_URL)

@router.get("/latest")
def latest(ticker: str = Query(..., min_length=1), limit: int = 50) -> List[Dict]:
    sql = """
    SELECT ni.id, ni.source, ni.url, ni.published_at, ni.raw_title, s.sentiment, s.score, s.label_confidence
    FROM news_items ni
    JOIN sentiments s ON s.news_id = ni.id
    WHERE %s = ANY(ni.tickers)
    ORDER BY ni.published_at DESC
    LIMIT %s;
    """
    with _conn() as c, c.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, (ticker.upper(), limit))
        return cur.fetchall()

@router.get("/series")
def series(ticker: str = Query(..., min_length=1),
           window: str = "1 day",
           bucket: str = "15 minutes") -> List[Dict]:
    # for now we only created 15m; we'll filter by time here
    sql = """
    SELECT bucket, ticker, n, avg_score, net_votes, avg_conf
    FROM sentiment_agg_15m
    WHERE ticker = %s AND bucket >= (NOW() - %s::interval)
    ORDER BY bucket ASC;
    """
    with _conn() as c, c.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, (ticker.upper(), window))
        return cur.fetchall()
