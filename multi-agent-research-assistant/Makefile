.PHONY: install dev lint format run test db-up db-migrate clean

install:
	pip install -e .
	pip install -e ".[dev]"

dev:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8001

run:
	uvicorn src.main:app --host 0.0.0.0 --port 8001

lint:
	ruff check src/

format:
	ruff format src/

test:
	pytest tests/ -v

db-up:
	docker compose up -d db

db-migrate:
	alembic upgrade head

db-revision:
	alembic revision --autogenerate -m "$(message)"

clean:
	rm -rf __pycache__ .ruff_cache .pytest_cache
	find . -name "*.pyc" -delete
