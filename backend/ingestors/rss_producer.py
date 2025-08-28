import os, time, json, feedparser, redis
from .common import extract_tickers, url_hash, now_utc

'''Polls configured RSS feeds, dedupes by URL hash, and publishes items into a Redis Stream.'''

STREAM_KEY = os.getenv("NEWS_STREAM_KEY", "news:stream")
RSS_SOURCES = [s.strip() for s in os.getenv("RSS_SOURCES", "").split(",") if s.strip()]
POLL_SEC = int(os.getenv("RSS_POLL_SECONDS", "60"))
r = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"), decode_responses=True)

def main():
    if not RSS_SOURCES: return print("No RSS_SOURCES configured.")
    print(f"[rss_producer] polling {len(RSS_SOURCES)} feeds every {POLL_SEC}s")
    while True:
        for src in RSS_SOURCES:
            try:
                feed = feedparser.parse(src)
                for entry in feed.entries:
                    url, title = entry.get("link",""), entry.get("title","")
                    payload = {
                        "id": url_hash(url)[:32], "source": src, "url": url,
                        "raw_title": title, "raw_text": entry.get("summary",""),
                        "tickers": extract_tickers(f"{title} {entry.get('summary','')}"),
                        "ingested_at": now_utc().isoformat()
                    }
                    if r.sadd("news:dedup:urlhash", url_hash(url)):
                        r.xadd(STREAM_KEY, {"payload": json.dumps(payload)}, maxlen=10000, approximate=True)
            except Exception as e: print(f"[rss_producer] error {src}: {e}")
        time.sleep(POLL_SEC)

if __name__ == "__main__": main()