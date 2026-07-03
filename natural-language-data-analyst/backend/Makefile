.PHONY: install dev lint test migrate run

install:
	pip install -e ".[dev]"

dev:
	uvicorn src.main:app --reload --port 8004

lint:
	ruff check src/ tests/

test:
	python -m pytest tests/ -v

migrate:
	alembic upgrade head

makemigrations:
	alembic revision --autogenerate -m "$(msg)"
