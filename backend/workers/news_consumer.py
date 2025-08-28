import os, json, uuid, time, psycopg2, psycopg2.extras, redis
from prometheus_client import Counter, start_http_server

'''Consumes Redis Stream messages, inserts them into news_items, and exposes Prometheus ingestion metrics.'''

STREAM_KEY = os.getenv("NEWS_STREAM_KEY","news:stream")
GROUP, CONSUMER = "news_cg", f"c-{uuid.uuid4().hex[:6]}"
DATABASE_URL = os.getenv("DATABASE_URL").replace("+psycopg2","")
r = redis.from_url(os.getenv("REDIS_URL","redis://redis:6379/0"), decode_responses=True)

INGESTED = Counter("fintrend_news_ingested_total","News rows inserted")
DUPLICATE = Counter("fintrend_news_duplicate_total","News skipped on conflict")

SQL = """INSERT INTO news_items (id,source,url,raw_title,raw_text,tickers,ingested_at)
VALUES (%(id)s,%(source)s,%(url)s,%(raw_title)s,%(raw_text)s,%(tickers)s,%(ingested_at)s)
ON CONFLICT DO NOTHING;"""

def ensure_group():
    try: r.xgroup_create(STREAM_KEY,GROUP,"$",mkstream=True)
    except redis.ResponseError as e:
        if "BUSYGROUP" not in str(e): raise

def main():
    start_http_server(9101)
    ensure_group()
    conn = psycopg2.connect(DATABASE_URL); conn.autocommit = True
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    print(f"[worker] consuming {STREAM_KEY} as {GROUP}/{CONSUMER}")
    while True:
        msgs = r.xreadgroup(GROUP,CONSUMER,{STREAM_KEY: ">"},count=50,block=5000)
        for _,entries in msgs:
            for msg_id, fields in entries:
                payload = json.loads(fields["payload"])
                cur.execute(SQL,payload)
                if cur.rowcount==1: INGESTED.inc()
                else: DUPLICATE.inc()
                r.xack(STREAM_KEY,GROUP,msg_id)

if __name__=="__main__": main()
