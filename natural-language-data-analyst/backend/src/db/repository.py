import json
import uuid

from sqlalchemy import select

from src.db.database import async_session_factory
from src.db.models import ChartRecord, DashboardRecord, DatasetRecord, QueryRecord, ReportRecord


class DatasetRepo:
    @staticmethod
    async def create(
        name: str, filename: str, table_name: str, row_count: int, column_info: list[dict],
    ) -> DatasetRecord:
        async with async_session_factory() as session:
            rec = DatasetRecord(
                name=name, filename=filename, table_name=table_name,
                row_count=row_count, column_info=json.dumps(column_info),
            )
            session.add(rec)
            await session.commit()
            await session.refresh(rec)
            return rec

    @staticmethod
    async def get(dataset_id: str) -> DatasetRecord | None:
        async with async_session_factory() as session:
            return await session.get(DatasetRecord, uuid.UUID(dataset_id))

    @staticmethod
    async def list_all() -> list[DatasetRecord]:
        async with async_session_factory() as session:
            stmt = select(DatasetRecord).order_by(DatasetRecord.created_at.desc())
            rows = (await session.execute(stmt)).scalars().all()
            return list(rows)


class QueryRepo:
    @staticmethod
    async def create(
        question: str, generated_sql: str, results_summary: str | None = None,
        insight_text: str | None = None, chart_id: str | None = None,
        dataset_id: str | None = None,
    ) -> QueryRecord:
        async with async_session_factory() as session:
            rec = QueryRecord(
                question=question, generated_sql=generated_sql,
                results_summary=results_summary, insight_text=insight_text,
                chart_id=uuid.UUID(chart_id) if chart_id else None,
                dataset_id=uuid.UUID(dataset_id) if dataset_id else None,
            )
            session.add(rec)
            await session.commit()
            await session.refresh(rec)
            return rec

    @staticmethod
    async def list_all(limit: int = 50) -> list[QueryRecord]:
        async with async_session_factory() as session:
            stmt = select(QueryRecord).order_by(QueryRecord.created_at.desc()).limit(limit)
            rows = (await session.execute(stmt)).scalars().all()
            return list(rows)


class ChartRepo:
    @staticmethod
    async def create(
        title: str, chart_type: str, config: dict, html_content: str | None = None,
        dataset_id: str | None = None,
    ) -> ChartRecord:
        async with async_session_factory() as session:
            rec = ChartRecord(
                title=title, chart_type=chart_type, config=json.dumps(config),
                html_content=html_content,
                dataset_id=uuid.UUID(dataset_id) if dataset_id else None,
            )
            session.add(rec)
            await session.commit()
            await session.refresh(rec)
            return rec

    @staticmethod
    async def get(chart_id: str) -> ChartRecord | None:
        async with async_session_factory() as session:
            return await session.get(ChartRecord, uuid.UUID(chart_id))


class DashboardRepo:
    @staticmethod
    async def create(title: str, layout: dict) -> DashboardRecord:
        async with async_session_factory() as session:
            rec = DashboardRecord(title=title, layout=json.dumps(layout))
            session.add(rec)
            await session.commit()
            await session.refresh(rec)
            return rec

    @staticmethod
    async def list_all() -> list[DashboardRecord]:
        async with async_session_factory() as session:
            stmt = select(DashboardRecord).order_by(DashboardRecord.created_at.desc())
            rows = (await session.execute(stmt)).scalars().all()
            return list(rows)


class ReportRepo:
    @staticmethod
    async def create(title: str, content: str) -> ReportRecord:
        async with async_session_factory() as session:
            rec = ReportRecord(title=title, content=content)
            session.add(rec)
            await session.commit()
            await session.refresh(rec)
            return rec

    @staticmethod
    async def list_all() -> list[ReportRecord]:
        async with async_session_factory() as session:
            stmt = select(ReportRecord).order_by(ReportRecord.created_at.desc())
            rows = (await session.execute(stmt)).scalars().all()
            return list(rows)
