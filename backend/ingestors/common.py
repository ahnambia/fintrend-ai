import re, hashlib
from datetime import datetime, timezone
from typing import List

'''Utility functions for dedupe (URL hash), ticker extraction, and timestamps shared by all producers.'''
TICKER_RE = re.compile(r"(?<![A-Z0-9])\$?([A-Z]{1,5})(?![A-Z])") # Match tickers like $AAPL, AAPL, or AAPL 

'''Extract tickers from text, removing common false positives.'''
def extract_tickers(text: str) -> List[str]:
    raw = {m.group(1).upper() for m in TICKER_RE.finditer(text.upper())}
    blacklist = {"USA", "CEO", "EPS", "IPO", "GDP", "ETF", "SEC"}
    return [t for t in raw if t not in blacklist]

def url_norm(url: str) -> str: return (url or "").strip().lower()

'''Generate a URL hash for deduplication.'''
def url_hash(url: str) -> str:
    return hashlib.sha256(url_norm(url).encode()).hexdigest()

'''Generate a timestamp for the current time.'''
def current_timestamp() -> int:
    return datetime.now(timezone.utc).timestamp()
