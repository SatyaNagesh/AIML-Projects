import uuid
from datetime import UTC, datetime

from sqlalchemy import select

from src.db.database import async_session_factory
from src.db.models import TaskRecord


class TaskRepository:
    async def create_task(self, task_id: str, task: str, url: str | None, status: str) -> None:
        async with async_session_factory() as session:
            record = TaskRecord(
                id=uuid.UUID(task_id),
                task=task,
                url=url,
                status=status,
            )
            session.add(record)
            await session.commit()

    async def update_task(
        self,
        task_id: str,
        status: str,
        result: str | None,
        error: str | None,
        actions: list | None,
        steps: list | None,
    ) -> None:
        async with async_session_factory() as session:
            record = await session.get(TaskRecord, uuid.UUID(task_id))
            if record:
                record.status = status
                record.result = result
                record.error = error
                record.actions = actions
                record.steps = steps
                record.updated_at = datetime.now(UTC)
                await session.commit()

    async def get_task(self, task_id: str) -> dict | None:
        async with async_session_factory() as session:
            record = await session.get(TaskRecord, uuid.UUID(task_id))
            if record is None:
                return None
            return self._to_dict(record)

    async def list_tasks(self, limit: int = 20) -> list[dict]:
        async with async_session_factory() as session:
            stmt = select(TaskRecord).order_by(TaskRecord.created_at.desc()).limit(limit)
            result = await session.execute(stmt)
            records = result.scalars().all()
            return [self._to_dict(r) for r in records]

    def _to_dict(self, record: TaskRecord) -> dict:
        return {
            "task_id": str(record.id),
            "task": record.task,
            "url": record.url,
            "status": record.status,
            "result": record.result,
            "error": record.error,
            "actions": record.actions or [],
            "steps": record.steps or [],
            "created_at": record.created_at.isoformat() if record.created_at else "",
            "timestamp": record.updated_at.isoformat() if record.updated_at else "",
            "done": record.status == "completed",
        }
