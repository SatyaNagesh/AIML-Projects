# AI Interview Copilot

An AI-powered interview coach that conducts realistic mock interviews, evaluates responses via voice, and provides improvement suggestions.

## Capabilities

- **Voice Interview** — record answers using your microphone, transcribed via Whisper
- **Answer Evaluation** — GPT-5 scores answers 1-10 with strengths, weaknesses, and tips
- **Resume-Based Questions** — generates tailored questions from your resume and target role
- **Feedback Generation** — comprehensive session feedback with skill gap analysis and resources
- **Progress Tracking** — dashboard showing scores across all sessions

## Architecture

```
Frontend (Next.js) ←→ Backend (FastAPI) ←→ PostgreSQL
                           ↕
                    ┌──────────────┐
                    │  Interview   │
                    │  Engine      │
                    ├──────────────┤
                    │ GPT-5 (eval) │
                    │ Whisper (STT)│
                    └──────────────┘
```

| Layer      | Technology                     |
|------------|---------------------------------|
| Frontend   | Next.js 15, TypeScript, Tailwind CSS |
| Backend    | FastAPI, Python 3.12+           |
| LLM        | OpenAI GPT-5 (questions, eval, feedback) |
| Speech     | OpenAI Whisper API (speech-to-text) |
| Database   | PostgreSQL (async via SQLAlchemy) |

## Quick Start

### Backend
```bash
cd backend
pip install -e ".[dev]"
cp .env.example .env  # add your OPENAI_API_KEY
docker compose up -d db
alembic upgrade head
make run  # starts on :8002
```

### Frontend
```bash
cd frontend
npm install
npm run dev  # starts on :3000
```

### Or both together
```bash
docker compose up  # starts backend + db
# In another terminal:
cd frontend && npm run dev
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/sessions | Create session + generate questions |
| POST | /api/v1/sessions/{id}/answer | Submit + evaluate answer |
| POST | /api/v1/sessions/{id}/feedback | Generate session feedback |
| POST | /api/v1/audio/transcribe | Transcribe audio via Whisper |
| GET | /api/v1/sessions/{id} | Get session details |
| GET | /api/v1/sessions | List all sessions |

## Project Structure

```
backend/src/
├── api/           FastAPI routes + Pydantic schemas
├── interview/     Engine, question generator, evaluator, feedback
├── speech/        Whisper speech-to-text
├── db/            PostgreSQL models + repository
├── llm/           OpenAI GPT-5 client
└── main.py        Entry point

frontend/src/app/
├── page.tsx       Landing page (role + resume form)
├── interview/     Mock interview with voice recording
└── dashboard/     Progress tracking across sessions
```
