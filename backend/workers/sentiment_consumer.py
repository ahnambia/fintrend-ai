import os
import time
import logging
from redis import Redis
from prometheus_client import start_http_server, Counter, Gauge

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [worker_sentiment] %(levelname)s %(message)s"
)

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
STREAM = os.getenv("SENTIMENT_STREAM", "news:stream")  # we read news stream; scoring will come next
GROUP = os.getenv("SENTIMENT_GROUP", "sentiment")
CONSUMER = os.getenv("HOSTNAME", "sentiment-1")

METRICS_PORT = int(os.getenv("SENTIMENT_METRICS_PORT", "9102"))

# Prometheus metrics
SCORED = Counter("fintrend_sent_scored_total", "Number of news items scored")
FAILED = Counter("fintrend_sent_failed_total", "Number of news items failed to score")
BACKLOG = Gauge("fintrend_sent_backlog", "Pending messages in the stream")

def ensure_group(r: Redis):
    try:
        r.xgroup_create(STREAM, GROUP, id="$", mkstream=True)
        logging.info("Created stream group: stream=%s group=%s", STREAM, GROUP)
    except Exception:
        # group probably exists
        pass

# --- keep the imports/metrics/ensure_group as you have them ---

def main():
    # 1) metrics first
    start_http_server(METRICS_PORT)
    logging.info("metrics server up on :%s", METRICS_PORT)

    # 2) redis + group
    r = Redis.from_url(REDIS_URL, decode_responses=True)
    ensure_group(r)
    logging.info("connected to redis at %s; stream=%s group=%s consumer=%s", REDIS_URL, STREAM, GROUP, CONSUMER)

    # 3) simple consume/ack loop (no model yet)
    while True:
        try:
            # keep backlog gauge fresh
            try:
                info = r.xinfo_stream(STREAM)
                BACKLOG.set(info.get("length", 0))
            except Exception as e:
                logging.warning("xinfo_stream failed: %s", e)
                BACKLOG.set(0)

            # block up to 2s for messages
            resp = r.xreadgroup(GROUP, CONSUMER, {STREAM: ">"}, count=10, block=2000)
            if not resp:
                continue

            # resp format: [(stream, [(id, fields), ...])]
            for _stream, entries in resp:
                for msg_id, fields in entries:
                    try:
                        # pretend we “scored” successfully just to validate flow
                        SCORED.inc()
                        # ack the message so backlog drops
                        r.xack(STREAM, GROUP, msg_id)
                    except Exception as ex:
                        FAILED.inc()
                        logging.exception("failed handling msg_id=%s: %s", msg_id, ex)
        except Exception as outer:
            logging.exception("outer loop error: %s", outer)
            time.sleep(1)
