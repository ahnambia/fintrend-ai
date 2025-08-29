'''What: A thin wrapper around ProsusAI/finbert (Hugging Face Transformers) that loads once, cleans input, batches inference, and returns both a 
discrete label (pos/neu/neg) and a signed scalar score (e.g., +0.88 for positive, -0.92 for negative).
Why: Centralizing model logic avoids duplication and ensures identical scoring in the worker, backfills, and tests.
Long-run value: Easier to swap/upgrade models (e.g., a RoBERTa finance model) and tune batching/truncation without touching multiple callers.
How it relates: The worker and backfill call this module; the API never talks to the model directly.'''

from __future__ import annotations
import os
from typing import List, Dict
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline

# Load model once
_MODEL_NAME = os.getenv("SENTIMENT_MODEL", "ProsusAI/finbert")
_MAX_LEN = int(os.getenv("SENT_MAX_TOKENS", "256"))

# Map from Hugging Face label to (label, score)
_LABEL_MAP = {
    "positive": ("pos", +1.0),
    "neutral":  ("neu",  0.0),
    "negative": ("neg", -1.0),
}

# Main class
class SentimentService:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME, use_fast=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(_MODEL_NAME)
        self.pipe = TextClassificationPipeline(
            model=self.model,
            tokenizer=self.tokenizer,
            top_k=None,
            truncation=True,
            max_length=_MAX_LEN,
            return_all_scores=False,
            device=-1,   # CPU
        )
    
    # Clean and concat title/text
    def _prep(self, title: str, text: str) -> str:
        title = (title or "").strip()
        text  = (text or "").strip()
        if not text:
            return title
        # Light concat; tokenizer will truncate
        return f"{title}. {text}"
    
    # Score a batch of news items
    def score_batch(self, items: List[Dict[str, str]]) -> List[Dict]:
        inputs = [self._prep(x.get("raw_title",""), x.get("raw_text","")) for x in items]
        outputs = self.pipe(inputs)
        results = []
        for doc, out in zip(items, outputs):
            # out is dict like {"label": "positive", "score": 0.98}
            label = out["label"].lower()
            short, sign = _LABEL_MAP.get(label, ("neu", 0.0))
            conf = float(out["score"])
            signed = sign * conf   # e.g., +0.95 / -0.87 / 0.0
            results.append({
                "news_id": doc["news_id"],
                "sentiment": short,
                "score": signed,
                "label_confidence": conf,
                "model": _MODEL_NAME,
            })
        return results