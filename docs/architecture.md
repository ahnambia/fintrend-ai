# Architecture (MVP)

**Ingestion:** RSS + subreddit RSS producers publish items to **Redis Streams**.  
**Processing:** Workers consume streams, perform de-dup (by URL/content hash), persist to Postgres/Timescale, and trigger NLP scoring.  
**NLP:** FinBERT/finance RoBERTa scores headlines/body → `sentiments` table.  
**Aggregation:** Timescale continuous aggregates compute rolling sentiment metrics per ticker.  
**Signals:** Indicators (ROC/EMA/RSI + sentiment z-score) feed rule engine → `signals`.  
**API:** FastAPI provides REST for history and SSE/WebSockets for live updates.  
**Frontend:** React/Vite dashboard subscribes to live streams and renders charts via Recharts.  
**Monitoring:** Prometheus scrapes app metrics; Grafana visualizes (latency, throughput, lag).

Data flow: Producers → Redis → Workers → DB → Aggregates/Signals → API (SSE) → Frontend.
