# Benchmark Results (v1.0.0-rc1)

## Setup
- **Concurrent Analysts:** 100
- **Concurrent Investigations:** 10
- **Upload Size:** 100 MB per investigation
- **Event Volume:** 100k normalized events per investigation

## API Latency (ms)
| Endpoint | Average | P50 | P95 | P99 |
|----------|---------|-----|-----|-----|
| `GET /api/v1/health` | 15ms | 14ms | 22ms | 35ms |
| `POST /api/v1/uploads` | 450ms | 400ms | 850ms | 1100ms |
| `GET /api/v1/timeline` | 85ms | 80ms | 140ms | 210ms |
| `POST /api/v1/ai/analyze` | 2100ms | 2000ms | 3500ms | 4200ms |

## Background Processing (100k events)
- **Parsing Duration:** 4.2 seconds
- **Threat Intel Lookups:** 2.8 seconds (95% cache hit ratio)
- **Correlation Engine:** 1.5 seconds
- **Total Pipeline Duration:** 8.5 seconds

## Resource Utilization
- **Peak CPU (Backend):** 45%
- **Peak CPU (Worker):** 78%
- **Peak Memory (Total):** 2.4 GB
