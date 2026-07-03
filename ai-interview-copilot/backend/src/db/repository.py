import uuid
from datetime import UTC, datetime

from sqlalchemy import select

from src.db.database import async_session_factory
from src.db.models import InterviewSession


class SessionRepository:
    async def create(self, session_id: str, role: str, resume: str, level: str) -> None:
        async with async_session_factory() as session:
            record = InterviewSession(
                id=uuid.UUID(session_id), role=role, resume=resume, experience_level=level,
            )
            session.add(record)
            await session.commit()

    async def get(self, session_id: str) -> dict | None:
        async with async_session_factory() as session:
            record = await session.get(InterviewSession, uuid.UUID(session_id))
            if record is None:
                return None
            return self._to_dict(record)

    async def list_all(self, limit: int = 20) -> list[dict]:
        async with async_session_factory() as session:
            stmt = (
                select(InterviewSession)
                .order_by(InterviewSession.created_at.desc())
                .limit(limit)
            )
            rows = (await session.execute(stmt)).scalars().all()
            return [self._to_dict(r) for r in rows]

    async def update_questions(self, session_id: str, questions: list[dict]) -> None:
        async with async_session_factory() as session:
            record = await session.get(InterviewSession, uuid.UUID(session_id))
            if record:
                record.questions = questions
                record.updated_at = datetime.now(UTC)
                await session.commit()

    async def add_answer(
        self, session_id: str, question_id: int,
        question: str, answer: str, evaluation: dict,
    ) -> None:
        async with async_session_factory() as session:
            record = await session.get(InterviewSession, uuid.UUID(session_id))
            if not record:
                return
            entry = {
                "question_id": question_id,
                "question": question,
                "answer": answer,
                **{k: v for k, v in evaluation.items()},
            }
            current = record.answers or []
            current.append(entry)
            record.answers = current
            scores = [a.get("score", 0) for a in current if a.get("score")]
            record.average_score = sum(scores) / len(scores) if scores else 0.0
            record.updated_at = datetime.now(UTC)
            await session.commit()

    async def update_feedback(self, session_id: str, feedback: dict) -> None:
        async with async_session_factory() as session:
            record = await session.get(InterviewSession, uuid.UUID(session_id))
            if record:
                record.feedback = feedback
                record.status = "completed"
                record.updated_at = datetime.now(UTC)
                await session.commit()

    def _to_dict(self, r: InterviewSession) -> dict:
        answers = r.answers or []
        scores = [a.get("score", 0) for a in answers if a.get("score")]
        avg = sum(scores) / len(scores) if scores else 0.0
        return {
            "session_id": str(r.id),
            "role": r.role or "",
            "experience_level": r.experience_level,
            "status": r.status,
            "resume": r.resume or "",
            "questions": r.questions or [],
            "answers": r.answers or [],
            "feedback": r.feedback or {},
            "question_count": len(r.questions or []),
            "average_score": round(avg, 1),
            "created_at": r.created_at.isoformat() if r.created_at else "",
            "updated_at": r.updated_at.isoformat() if r.updated_at else "",
        }
