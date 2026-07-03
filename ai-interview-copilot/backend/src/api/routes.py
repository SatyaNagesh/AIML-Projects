import uuid

from fastapi import APIRouter, HTTPException, UploadFile

from src.api.schemas import (
    AnswerResponse,
    AnswerSubmit,
    FeedbackResponse,
    SessionCreate,
    SessionResult,
)
from src.db.repository import SessionRepository
from src.interview.engine import InterviewEngine
from src.speech.whisper import WhisperTranscriber

router = APIRouter(prefix="/api/v1", tags=["interview"])

engine = InterviewEngine()
transcriber = WhisperTranscriber()


@router.post("/sessions", status_code=201)
async def create_session(req: SessionCreate) -> dict:
    session_id = str(uuid.uuid4())
    repo = SessionRepository()
    await repo.create(
        session_id=session_id, role=req.role, resume=req.resume,
        level=req.experience_level,
    )

    questions = await engine.generate_questions(
        resume=req.resume, role=req.role, level=req.experience_level,
    )
    await repo.update_questions(session_id=session_id, questions=questions)

    return {"session_id": session_id, "questions": questions}


@router.post("/sessions/{session_id}/answer")
async def submit_answer(session_id: str, req: AnswerSubmit) -> AnswerResponse:
    repo = SessionRepository()
    session = await repo.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    evaluation = await engine.evaluate_answer(req.question, req.answer)
    await repo.add_answer(
        session_id=session_id,
        question_id=req.question_id,
        question=req.question,
        answer=req.answer,
        evaluation=evaluation,
    )

    return AnswerResponse(
        session_id=session_id,
        question_id=req.question_id,
        score=evaluation.get("score", 5),
        strengths=evaluation.get("strengths", []),
        weaknesses=evaluation.get("weaknesses", []),
        suggested_answer=evaluation.get("suggested_answer", ""),
        tips=evaluation.get("tips", []),
        overall=evaluation.get("overall", ""),
    )


@router.post("/sessions/{session_id}/feedback")
async def get_feedback(session_id: str) -> FeedbackResponse:
    repo = SessionRepository()
    session = await repo.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    qa_pairs = session.get("answers", [])
    feedback = await engine.generate_feedback(qa_pairs)
    await repo.update_feedback(session_id=session_id, feedback=feedback)

    return FeedbackResponse(
        session_id=session_id,
        overall_score=feedback.get("overall_score", 0),
        strengths=feedback.get("strengths", []),
        areas_to_improve=feedback.get("areas_to_improve", []),
        skill_gaps=feedback.get("skill_gaps", []),
        recommended_resources=feedback.get("recommended_resources", []),
        summary=feedback.get("summary", ""),
    )


@router.post("/audio/transcribe")
async def transcribe_audio(file: UploadFile) -> dict:
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")

    text = await transcriber.transcribe(audio_bytes)
    return {"text": text}


@router.get("/sessions/{session_id}")
async def get_session(session_id: str) -> SessionResult:
    repo = SessionRepository()
    session = await repo.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResult(**session)


@router.get("/sessions")
async def list_sessions() -> list[SessionResult]:
    repo = SessionRepository()
    sessions = await repo.list_all()
    return [SessionResult(**s) for s in sessions]
