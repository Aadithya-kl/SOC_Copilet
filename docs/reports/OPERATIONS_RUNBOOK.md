# SOC Copilot - Operations Runbook

## Overview
This runbook provides actionable procedures for monitoring, diagnosing, and resolving operational issues in the SOC Copilot backend infrastructure.

## Architecture Topology
The backend is deployed via Docker Compose and consists of:
- `backend`: The FastAPI application server serving HTTP and WebSockets.
- `worker`: The `arq` background processor.
- `postgres`: The primary transactional database (Events, Entities, Graph projection).
- `redis`: Job queue and caching layer.
- `minio`: S3-compatible blob storage for raw EVTX/PCAP uploads.
- `qdrant`: Vector database for semantic log search.
- `prometheus` & `grafana`: Observability and metrics stack.

## Common Operations

### 1. Scaling the Investigation Workers
If the `queue_depth` metric in Grafana continuously grows:
```bash
docker compose up -d --scale worker=3
```

### 2. Provider Rate Limit Recovery
If Threat Intel providers (e.g., VirusTotal) begin returning HTTP 429:
1. Validate the rate limits in `grafana`.
2. Ensure the caching layer (Redis) is active. The system automatically caches TI results for 24h.
3. If necessary, configure a secondary API key via environment variables.

### 3. Out of Memory (OOM) on EVTX Parsing
The pipeline streams large files. If an OOM still occurs:
1. Validate the `max_upload_size` configuration (defaults to 100MB).
2. Ensure the Rust-based `evtx` parser is updated to the latest version.

### 4. Rebuilding the Graph Projection
If the Postgres Graph nodes fall out of sync with Evidence (rare):
The backend provides a recovery script to rebuild the deterministic projection:
```bash
poetry run python -m app.modules.graph.rebuild
```

## Monitoring Health
- Access `/api/v1/health` for an overarching view of subsystem health.
- Access Grafana on port `:3000` to review latency and throughput.
