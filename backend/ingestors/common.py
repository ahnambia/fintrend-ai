# backend/ingestors/common.py
import re
import hashlib
from datetime import datetime, timezone
from typing import List

TICKER_RE = re.compile(r"(?<![A-Z0-9])\$?([A-Z]{1,5})(?![A-Z])")

def extract_tickers(text: str) -> List[str]:
    text = (text or "").upper()
    raw = {m.group(1).upper() for m in TICKER_RE.finditer(text)}
    blacklist = {"USA", "CEO", "EPS", "IPO", "GDP", "ETF", "SEC"}
    return [t for t in raw if t not in blacklist]

def url_norm(url: str) -> str:
    return (url or "").strip().lower()

def url_hash(url: str) -> str:
    return hashlib.sha256(url_norm(url).encode("utf-8")).hexdigest()

def now_utc() -> datetime:
    return datetime.now(timezone.utc)
