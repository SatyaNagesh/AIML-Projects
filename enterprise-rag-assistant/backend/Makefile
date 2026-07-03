.PHONY: install dev lint run test db-up db-migrate clean

install:
	pip install -e .
	pip install -e ".[dev]"

dev:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8003

run:
	uvicorn src.main:app --host 0.0.0.0 --port 8003

lint:
	ruff check src/

format:
	ruff format src/

test:
	pytest tests/ -v --asyncio-mode=auto

db-up:
	docker compose up -d db

db-migrate:
	alembic upgrade head

db-revision:
	alembic revision --autogenerate -m "$(message)"

clean:
	rm -rf __pycache__ .ruff_cache .pytest_cache
	find . -name "*.pyc" -delete
	find . -name chroma_data -type d -exec rm -rf {} + 2>/dev/null || true
