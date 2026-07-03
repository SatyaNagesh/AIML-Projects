# Multi-Agent Deep Research Assistant

An AI system where multiple specialized agents collaborate to research a topic, verify sources, and generate detailed reports and presentations automatically.

## Capabilities

- **Web Research** — searches the web via Tavily, extracts content from multiple sources
- **Fact Verification** — cross-references claims across sources, flags contradictions
- **Source Collection** — organizes citations by type (article, blog, docs, news)
- **Report Generation** — writes comprehensive markdown reports with executive summary, findings, analysis, and references
- **Presentation Creation** — converts the report into structured slide-deck content with speaker notes

## Architecture

```
User Topic
    │
    ▼
  Supervisor (LangGraph orchestrator)
    │
    ├──► Research Agent ─── Tavily search + content extraction
    ├──► Fact-Check Agent ── GPT-5 cross-verification
    ├──► Source Collector ── Citation organization
    ├──► Report Writer ───── GPT-5 report generation
    └──► Presentation Agent ── GPT-5 slide creation
```

Each agent is a node in a LangGraph state graph. The supervisor decides which agent to call next based on the current research state. Agents pass structured data through the shared state.

## Tech Stack

| Layer          | Technology                          |
|----------------|-------------------------------------|
| Orchestration  | LangGraph (supervisor + worker nodes) |
| LLM            | OpenAI GPT-5 (JSON structured output) |
| Web Search     | Tavily API                          |
| API            | FastAPI                             |
| Database       | PostgreSQL (async via SQLAlchemy)   |

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Set environment
cp .env.example .env
# Add OPENAI_API_KEY and TAVILY_API_KEY

# Start database
docker compose up -d db

# Run migrations
alembic upgrade head

# Start API
make run
```

## API

```bash
# Health check
curl http://localhost:8001/health

# Run research
curl -X POST http://localhost:8001/api/v1/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "Latest advances in quantum computing 2026"}'

# List all research
curl http://localhost:8001/api/v1/research

# Get specific research
curl http://localhost:8001/api/v1/research/{research_id}
```

## Project Structure

```
src/
├── agent/
│   ├── graph.py              LangGraph state graph
│   ├── state.py              Typed research state
│   ├── supervisor.py         Orchestrator agent
│   ├── research_agent.py     Web search via Tavily
│   ├── factcheck_agent.py    Fact verification
│   ├── source_collector.py   Citation organization
│   ├── report_writer.py      Report generation
│   └── presentation_agent.py Slide deck creation
├── api/                      FastAPI routes
├── db/                       PostgreSQL models + repository
├── llm/                      OpenAI GPT-5 client
└── main.py                   Entry point
```
