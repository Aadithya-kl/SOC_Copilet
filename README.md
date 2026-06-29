# SOC Copilot

> AI-powered Security Operations Center assistant. Upload logs, get a full incident investigation in minutes — free, self-hosted, open source.

## What it does
SOC Copilot is a modular monolith backend that orchestrates a team of specialized AI agents to automate the investigation of cybersecurity incidents. It ingests logs, extracts indicators of compromise, correlates events, enriches intelligence, maps to MITRE ATT&CK, and generates explainable, professional reports. It handles the repetitive triage work, freeing analysts for strategic response.

## Quick Start (under 5 minutes)
```bash
git clone https://github.com/Aadithya-kl/SOC_Copilet.git
cd SOC_Copilet
cp .env.example .env
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```
Open http://localhost:8000/api/v1/docs -> Log in -> Upload a log file

## Features
- 🚀 Multi-format log file parsing (EVTX, syslog, etc.)
- 🤖 Hybrid AI Pipeline with specialized LangGraph agents
- 🔍 Automatic IOC Extraction & Threat Intelligence Enrichment
- 🔗 Event Correlation & Timeline Reconstruction
- 📚 MITRE ATT&CK Mapping & Risk Scoring
- 💬 Retrieval-Augmented Generation (RAG) for conversational incident queries

## Architecture
SOC Copilot is built as a modular monolith using FastAPI, PostgreSQL, Redis, Qdrant, MinIO, and LangGraph. It is designed to be fully self-hostable, running models locally via Ollama or remotely via OmniRoute.

## Documentation
- Setup and Configuration
- Development Guide

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to set up the development environment and submit pull requests.

## License
Apache 2.0
