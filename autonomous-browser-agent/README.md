# Autonomous Browser Agent

An AI-powered agent that browses websites, clicks buttons, fills forms, and completes multi-step web tasks — just like a human user.

Built with **LangGraph**, **OpenAI GPT-5**, **Playwright**, **FastAPI**, and **PostgreSQL**.

## Capabilities

- **Search** — navigate websites and extract information
- **Fill forms** — auto-complete login, registration, checkout flows
- **Book appointments** — reserve tables, schedule meetings
- **Extract data** — scrape and organize structured information from pages
- **Multi-step tasks** — chain navigation, form fills, and extractions into complex workflows

## Tech Stack

| Layer        | Technology                     |
| ------------ | ------------------------------ |
| Orchestration| LangGraph (stateful agent graph) |
| LLM          | OpenAI GPT-5 (structured output) |
| Browser      | Playwright (Chromium headless) |
| API          | FastAPI                        |
| Database     | PostgreSQL (async via SQLAlchemy) |

## Quick Start

```bash
# 1. Install dependencies
pip install -e ".[dev]"
playwright install chromium

# 2. Set up environment
cp .env.example .env
# Edit .env — add your OPENAI_API_KEY

# 3. Start PostgreSQL
docker compose up -d db

# 4. Run migrations
alembic upgrade head

# 5. Start the API
make run
```

## API

```bash
# Health check
curl http://localhost:8000/health

# Run a task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"task": "Go to google.com and search for LangGraph"}'

# List tasks
curl http://localhost:8000/api/v1/tasks

# Get task details
curl http://localhost:8000/api/v1/tasks/{task_id}
```

## Project Structure

```
src/
├── agent/          # LangGraph state graph, nodes, prompts
├── browser/        # Playwright controller + action models
├── llm/            # OpenAI GPT-5 client with structured output
├── api/            # FastAPI routes + Pydantic schemas
├── db/             # PostgreSQL models, repository, async session
└── main.py         # FastAPI entry point
```
