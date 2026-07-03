import uuid
from datetime import UTC, datetime

from sqlalchemy import select

from src.db.database import async_session_factory
from src.db.models import ResearchRecord


class ResearchRepository:
    async def create(self, research_id: str, topic: str) -> None:
        async with async_session_factory() as session:
            record = ResearchRecord(id=uuid.UUID(research_id), topic=topic)
            session.add(record)
            await session.commit()

    async def update(
        self,
        research_id: str,
        status: str,
        query: str = "",
        sources: list | None = None,
        claims: list | None = None,
        report: str = "",
        presentation: str = "",
        error: str | None = None,
    ) -> None:
        async with async_session_factory() as session:
            record = await session.get(ResearchRecord, uuid.UUID(research_id))
            if record:
                record.status = status
                record.query = query
                record.sources = sources
                record.verified_claims = claims
                record.report = report
                record.presentation = presentation
                record.error = error
                record.updated_at = datetime.now(UTC)
                await session.commit()

    async def get(self, research_id: str) -> dict | None:
        async with async_session_factory() as session:
            record = await session.get(ResearchRecord, uuid.UUID(research_id))
            if record is None:
                return None
            return self._to_dict(record)

    async def list_all(self, limit: int = 20) -> list[dict]:
        async with async_session_factory() as session:
            stmt = select(ResearchRecord).order_by(ResearchRecord.created_at.desc()).limit(limit)
            rows = (await session.execute(stmt)).scalars().all()
            return [self._to_dict(r) for r in rows]

    def _to_dict(self, r: ResearchRecord) -> dict:
        return {
            "research_id": str(r.id),
            "topic": r.topic,
            "query": r.query or "",
            "status": r.status,
            "sources": r.sources or [],
            "verified_claims": r.verified_claims or [],
            "report": r.report or "",
            "presentation": r.presentation or "",
            "error": r.error,
            "done": r.status == "completed",
            "timestamp": (
                r.updated_at or r.created_at
            ).isoformat() if (r.updated_at or r.created_at) else "",
        }
