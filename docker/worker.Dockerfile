# Build Stage
FROM python:3.12.3-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update && apt-get install -y curl build-essential \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app
COPY backend/pyproject.toml backend/poetry.lock* ./
RUN poetry install --only main --no-root

# Run Stage
FROM python:3.12.3-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY backend/ ./

RUN useradd -m -u 1000 soc_copilot \
    && chown -R 1000:1000 /app
USER 1000

# Worker doesn't have an HTTP endpoint by default, 
# but arq allows checking health via redis keys. We can omit healthcheck here or implement a custom one.

CMD ["arq", "app.worker.WorkerSettings"]
