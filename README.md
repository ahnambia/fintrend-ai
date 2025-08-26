# FinTrend AI — Real-time Financial Sentiment & Signals (MVP)

**What it is:** A Bloomberg-lite dashboard that ingests finance news + Reddit, scores sentiment (FinBERT), joins with prices, and emits bullish/bearish trade flags in near-real time. Includes a basic backtest for demos.

## Architecture (overview)
- **Streams:** Redis Streams for ingestion (upgradeable to Kafka).
- **Backend:** FastAPI; SSE/WebSockets for live updates.
- **DB:** Postgres 16 + TimescaleDB for time-series.
- **NLP:** FinBERT/RoBERTa for finance sentiment.
- **Frontend:** React + Vite + Recharts.
- **Monitoring:** Prometheus + Grafana.
- **Deploy:** Docker Compose.

Details in `docs/architecture.md` and `docs/data-contracts.md`.

## Services (high-level)
- `backend/api`: REST + live streams.
- `backend/ingestors`: RSS/Reddit/Prices producers → Redis Streams.
- `backend/workers`: Consumers → DB writes & feature jobs.
- `backend/nlp`: Model loader & scoring.
- `backend/signals`: Indicators + rule engine.
- `infra`: Docker, Prometheus, Grafana setup.
- `frontend`: Vite app (charts & live feed).
- `notebooks`: Backtest notebook (later).

## Development
- Python 3.11+, Node 20+.
- Formatting/linting via `pre-commit` (ruff/black/mypy).
- Conventional Commits; branches: `feat/*`, `fix/*`, `chore/*`.

## Quickstart (Day 2)

1. Copy `.env.sample` → `.env`
2. Run stack:  
   ```bash
   docker compose -f infra/compose/docker-compose.yml up --build

## Roadmap (Day-by-day)
- **Day 3:** RSS/Reddit ingestors → Redis Streams; worker writes to DB.
- **Day 4:** Price ingestor (API + cached fallback) and prices table.
- **Day 5:** Sentiment scorer (FinBERT) + `sentiments` writes.
- **Day 6:** Timescale continuous aggregates; `/tickers/{T}/sentiment`.
- **Day 7:** Frontend bootstrap + `/health`, `/news` views.
- **Day 8:** SSE/WebSocket & live feed.
- **Day 9:** Indicators + rule engine → `signals`.
- **Day 10:** Charts (price + sentiment + signals).
- **Day 11:** Watchlist & per-ticker page.
- **Day 12:** Prometheus/Grafana dashboards.
- **Day 13:** Backtest MVP.
- **Day 14:** Alerts prototype (email/SMS).
- **Day 15+:** Polish, screenshots, demo script, stretch goals.



## License
MIT. See `LICENSE`.

