.PHONY: dev test migrate seed lint build

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

test:
	docker compose -f docker-compose.test.yml up -d
	cd backend && poetry run pytest
	docker compose -f docker-compose.test.yml down

migrate:
	docker compose exec backend alembic upgrade head

seed:
	docker compose exec backend python scripts/seed_mitre.py

lint:
	cd backend && poetry run ruff check .
	cd backend && poetry run ruff format --check .
	cd backend && poetry run mypy .

build:
	docker compose build
