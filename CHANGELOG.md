# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0-rc1] - 2026-06-29

### Added
- **Core Architecture:** Clean Architecture modular monolith using FastAPI, PostgreSQL, and Redis.
- **Investigation Pipeline:** Asynchronous background processing pipeline utilizing Arq for high-throughput EVTX parsing.
- **Threat Intelligence Integration:** Robust provider abstraction supporting VT, AbuseIPDB, URLHaus with intelligent local caching.
- **Correlation Engine:** Deterministic Union-Find engine connecting disparate events through shared entities and MITRE mappings.
- **AI Reasoning (OmniRoute):** Universal LLM provider integration producing strictly validated, citation-backed analytical summaries, Chat RAG, and Markdown reports.
- **Observability:** Complete integration of OpenTelemetry and Prometheus for latency tracking and granular subsystem health probes.
- **Security:** Extensive container hardening, rate limiting, and automated Bandit & Trivy static analysis pipelines.

### Changed
- Docker configurations optimized to utilize multi-stage builds and non-root execution contexts.

### Fixed
- N/A (Initial Release)
