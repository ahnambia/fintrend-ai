# Runbook (MVP)

## Local dev (to be enabled Day 2)
- Copy `.env.sample` → `.env`.
- `pre-commit install`
- `docker compose up` (from `infra/compose/`) — brings up db, redis, api, frontend, prometheus, grafana.

## Observability
- Prometheus targets: api, workers (HTTP /metrics).
- Grafana dashboards: ingestion lag, API latency, model throughput (to be added).

## Common ops
- Restart worker: `docker compose restart worker-*`
- Reset data (local dev): stop stack, remove `docker-data/` volumes (TBD), `compose up` again.
