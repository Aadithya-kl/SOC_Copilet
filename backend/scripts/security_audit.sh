#!/bin/bash
set -e

echo "Starting Security Audit..."

echo "[1/4] Running Bandit for static analysis..."
bandit -r app/ -f json -o reports/bandit.json || true

echo "[2/4] Running pip-audit for dependency vulnerabilities..."
pip-audit --desc --format json > reports/pip-audit.json || true

echo "[3/4] Running Trivy for container scanning..."
trivy image soc-copilot-backend:latest --format json > reports/trivy.json || true

echo "[4/4] Generating SBOM using Syft..."
syft dir:. -o cyclonedx-json=reports/sbom.json || true

echo "Security audit completed. Check the 'reports/' directory."
