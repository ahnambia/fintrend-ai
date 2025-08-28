import os, time, json, requests, feedparser, redis
from .common import extract_tickers, url_hash, now_utc

'''Polls configured Reddit feeds, dedupes by URL hash,
and publishes items into a Redis Stream.'''

STREAM_KEY = os.getenv("NEWS_STREAM_KEY", "news:stream")
SUBS = [s.strip() for s in os.getenv("SUBREDDITS", "").split(",") if s.strip()]
POLL_SEC = int(os.getenv("REDDIT_POLL_SECONDS", "60"))
UA = {"User-Agent": "FinTrendAI/0.1"}
r = redis.from_url(os.getenv("REDIS_URL","redis://redis:6379/0"), decode_responses=True)

def main():
    if not SUBS: return print("No SUBREDDITS configured.")
    print(f"[reddit_producer] polling {SUBS} every {POLL_SEC}s")
    while True:
        for sub in SUBS:
            try:
                resp = requests.get(f"https://www.reddit.com/r/{sub}/new/.rss", headers=UA, timeout=15)
                feed = feedparser.parse(resp.text)
                for entry in feed.entries:
                    url, title = entry.get("link",""), entry.get("title","")
                    payload = {
                        "id": url_hash(url)[:32], "source": f"reddit:{sub}", "url": url,
                        "raw_title": title, "raw_text": entry.get("summary",""),
                        "tickers": extract_tickers(f"{title} {entry.get('summary','')}"),
                        "ingested_at": now_utc().isoformat()
                    }
                    if r.sadd("news:dedup:urlhash", url_hash(url)):
                        r.xadd(STREAM_KEY, {"payload": json.dumps(payload)}, maxlen=10000, approximate=True)
            except Exception as e: print(f"[reddit_producer] error r/{sub}: {e}")
        time.sleep(POLL_SEC)

if __name__ == "__main__": main()