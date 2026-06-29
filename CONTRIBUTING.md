# Contributing to SOC Copilot

We welcome contributions from the community!

## Development Environment Setup
To get started, clone the repository and run:
`make dev`

## Code Structure Overview
- `backend/app/main.py`: Application factory
- `backend/app/modules/`: Feature modules (auth, incidents, threat_intel, etc.)
- `backend/app/agents/`: Investigation pipeline and agents
- `backend/app/llm/`: Universal LLM Service
- `backend/app/core/`: Cross-cutting concerns (config, db, logging)

## Testing Requirements
- Python unit tests: `pytest tests/unit/`
- All CI checks must pass.

## Commit Message Format
Please use Conventional Commits (e.g., `feat(parsers): add Palo Alto firewall log parser`).

## Reporting Security Vulnerabilities
Please see [SECURITY.md](SECURITY.md).
