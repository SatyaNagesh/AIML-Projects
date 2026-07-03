import uuid

from sqlalchemy import delete, select

from src.db.database import async_session_factory
from src.db.models import ConversationRecord, DocumentRecord


class DocumentRepository:
    async def create(self, doc_id: str, filename: str, chunk_count: int) -> None:
        async with async_session_factory() as session:
            session.add(DocumentRecord(
                id=uuid.UUID(doc_id), filename=filename, chunk_count=chunk_count,
            ))
            await session.commit()

    async def list_all(self, limit: int = 50) -> list[dict]:
        async with async_session_factory() as session:
            stmt = select(DocumentRecord).order_by(DocumentRecord.created_at.desc()).limit(limit)
            rows = (await session.execute(stmt)).scalars().all()
            return [
                {
                    "id": str(r.id),
                    "filename": r.filename,
                    "chunk_count": r.chunk_count,
                    "uploaded_at": r.created_at.isoformat() if r.created_at else "",
                }
                for r in rows
            ]

    async def delete_all(self) -> None:
        async with async_session_factory() as session:
            await session.execute(delete(DocumentRecord))
            await session.commit()


class ConversationRepository:
    async def add(self, question: str, answer: str, sources: list[str]) -> str:
        conv_id = str(uuid.uuid4())
        async with async_session_factory() as session:
            session.add(ConversationRecord(
                id=uuid.UUID(conv_id), question=question,
                answer=answer, sources=", ".join(sources),
            ))
            await session.commit()
        return conv_id

    async def list_all(self, limit: int = 50) -> list[dict]:
        async with async_session_factory() as session:
            stmt = (
                select(ConversationRecord)
                .order_by(ConversationRecord.created_at.desc())
                .limit(limit)
            )
            rows = (await session.execute(stmt)).scalars().all()
            return [
                {
                    "id": str(r.id),
                    "question": r.question,
                    "answer": r.answer[:200],
                    "sources": r.sources or "",
                    "created_at": r.created_at.isoformat() if r.created_at else "",
                }
                for r in rows
            ]
