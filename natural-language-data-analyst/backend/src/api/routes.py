import json
import logging
import uuid
from io import StringIO

import pandas as pd
from fastapi import APIRouter, HTTPException, UploadFile
from sqlalchemy import text as sa_text

from src.analyst.engine import compute_insights, execute_sql
from src.api.schemas import (
    ChartRequest,
    ChartResponse,
    DashboardCreate,
    DashboardResponse,
    DatasetResponse,
    QueryHistoryItem,
    QueryRequest,
    QueryResponse,
    ReportCreate,
    ReportResponse,
    SqlValidateRequest,
    SqlValidateResponse,
)
from src.db.database import async_session_factory
from src.db.repository import ChartRepo, DashboardRepo, DatasetRepo, QueryRepo, ReportRepo
from src.nl2sql.converter import generate_sql, validate_sql
from src.visualization.charts import build_chart, figure_to_html, figure_to_json, suggest_chart_type
from src.visualization.templates import build_dashboard_html, build_report_html

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")


def _df_to_serializable(df: pd.DataFrame) -> tuple[list[dict], list[str]]:
    df_clean = df.fillna("").infer_objects(copy=False)
    for col in df_clean.columns:
        if df_clean[col].dtype.kind == "O":
            df_clean[col] = df_clean[col].astype(str)
    return df_clean.to_dict(orient="records"), list(df_clean.columns)


@router.post("/query")
async def ask_question(body: QueryRequest) -> QueryResponse:
    dataset = await DatasetRepo.get(body.dataset_id)
    if not dataset:
        raise HTTPException(404, "Dataset not found")

    column_info = json.loads(dataset.column_info or "[]")

    sql = await generate_sql(body.question, column_info, dataset.table_name)
    err = validate_sql(sql)
    if err:
        raise HTTPException(400, f"Generated SQL is invalid: {err}. SQL was: {sql}")

    df = await execute_sql(sql)
    results, columns = _df_to_serializable(df)
    insights = compute_insights(df, body.question)

    chart_type = suggest_chart_type(df, body.question)
    fig = build_chart(df, chart_type, body.question)
    html = figure_to_html(fig)
    config = figure_to_json(fig)

    chart_rec = await ChartRepo.create(
        title=body.question[:100], chart_type=chart_type, config=config,
        html_content=html, dataset_id=body.dataset_id,
    )

    await QueryRepo.create(
        question=body.question, generated_sql=sql,
        results_summary=json.dumps({"row_count": len(df), "columns": columns}),
        insight_text=insights, chart_id=str(chart_rec.id), dataset_id=body.dataset_id,
    )

    return QueryResponse(
        id=str(chart_rec.id), question=body.question, generated_sql=sql,
        results=results, columns=columns, row_count=len(df),
        insights=insights, chart_html=html, chart_id=str(chart_rec.id),
    )


@router.post("/charts")
async def create_chart(body: ChartRequest) -> ChartResponse:
    dataset = await DatasetRepo.get(body.dataset_id)
    if not dataset:
        raise HTTPException(404, "Dataset not found")

    if body.sql_query:
        df = await execute_sql(body.sql_query)
    else:
        df = await execute_sql(f'SELECT * FROM "{dataset.table_name}" LIMIT 500')

    fig = build_chart(df, body.chart_type, body.title)
    html = figure_to_html(fig)
    config = figure_to_json(fig)

    rec = await ChartRepo.create(
        title=body.title, chart_type=body.chart_type,
        config=config, html_content=html, dataset_id=body.dataset_id,
    )
    return ChartResponse(id=str(rec.id), title=rec.title, chart_type=rec.chart_type, html=html)


@router.get("/charts/{chart_id}")
async def get_chart(chart_id: str) -> ChartResponse:
    rec = await ChartRepo.get(chart_id)
    if not rec:
        raise HTTPException(404, "Chart not found")
    return ChartResponse(
        id=str(rec.id), title=rec.title, chart_type=rec.chart_type, html=rec.html_content or "",
    )


@router.post("/dashboards")
async def create_dashboard(body: DashboardCreate) -> DashboardResponse:
    charts = []
    for cid in body.chart_ids:
        rec = await ChartRepo.get(cid)
        if rec:
            charts.append({"title": rec.title, "html": rec.html_content or "", "width": 1})

    html = build_dashboard_html(body.title, charts)
    rec = await DashboardRepo.create(body.title, {"chart_ids": body.chart_ids})
    return DashboardResponse(id=str(rec.id), title=rec.title, html=html)


@router.get("/dashboards")
async def list_dashboards() -> list[DashboardResponse]:
    recs = await DashboardRepo.list_all()
    return [DashboardResponse(id=str(r.id), title=r.title, html="") for r in recs]


@router.post("/reports")
async def create_report(body: ReportCreate) -> ReportResponse:
    sections = []
    for qid in body.query_ids:
        rec = await QueryRepo.list_all(limit=1000)
        match = next((r for r in rec if str(r.id) == qid), None)
        if not match:
            continue
        sections.append({"type": "text", "content": f"<strong>Q:</strong> {match.question}"})
        if match.insight_text:
            sections.append({"type": "insights", "content": match.insight_text})
        if match.chart_id:
            chart_rec = await ChartRepo.get(str(match.chart_id))
            if chart_rec and chart_rec.html_content:
                sections.append({"type": "chart", "html": chart_rec.html_content})

    html = build_report_html(body.title, sections)
    rec = await ReportRepo.create(body.title, html)
    return ReportResponse(id=str(rec.id), title=rec.title, html=html)


@router.get("/reports")
async def list_reports() -> list[ReportResponse]:
    recs = await ReportRepo.list_all()
    return [ReportResponse(id=str(r.id), title=r.title, html="") for r in recs]


@router.post("/datasets/upload")
async def upload_dataset(file: UploadFile) -> DatasetResponse:
    content = await file.read()
    try:
        df = pd.read_csv(StringIO(content.decode("utf-8")))
    except Exception as e:
        raise HTTPException(400, f"Failed to parse CSV: {e}")

    table_name = f"ds_{uuid.uuid4().hex[:12]}"
    column_info = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        sample = df[col].dropna().head(5).tolist()
        column_info.append({"name": col, "type": dtype, "sample_values": sample})

    cols_def = []
    for col, dtype in df.dtypes.items():
        safe_col = col.replace('"', '""')
        if "int" in str(dtype):
            sql_type = "BIGINT"
        elif "float" in str(dtype):
            sql_type = "DOUBLE PRECISION"
        else:
            sql_type = "TEXT"
        cols_def.append(f'"{safe_col}" {sql_type}')

    create_sql = f'CREATE TABLE "{table_name}" ({", ".join(cols_def)})'
    logger.info("Creating table: %s", create_sql)

    async with async_session_factory() as session:
        await session.execute(sa_text(create_sql))
        for _, row in df.iterrows():
            vals = []
            for col in df.columns:
                v = row[col]
                if pd.isna(v):
                    vals.append("NULL")
                elif isinstance(v, (int, float)):
                    vals.append(str(v))
                else:
                    safe = str(v).replace("'", "''")
                    vals.append(f"'{safe}'")
            safe_cols = ','.join(f'"{c.replace(chr(34), chr(34)+chr(34))}"' for c in df.columns)
            insert_sql = f'INSERT INTO "{table_name}" ({safe_cols}) VALUES ({", ".join(vals)})'
            await session.execute(sa_text(insert_sql))
        await session.commit()

    rec = await DatasetRepo.create(
        name=file.filename or "unnamed", filename=file.filename or "unnamed",
        table_name=table_name, row_count=len(df), column_info=column_info,
    )
    return DatasetResponse(
        id=str(rec.id), name=rec.name, filename=rec.filename,
        table_name=rec.table_name, row_count=rec.row_count,
        column_info=column_info, created_at=str(rec.created_at),
    )


@router.get("/datasets")
async def list_datasets() -> list[DatasetResponse]:
    recs = await DatasetRepo.list_all()
    return [
        DatasetResponse(
            id=str(r.id), name=r.name, filename=r.filename,
            table_name=r.table_name, row_count=r.row_count,
            column_info=json.loads(r.column_info or "[]"),
            created_at=str(r.created_at),
        )
        for r in recs
    ]


@router.post("/sql/validate")
async def validate_sql_endpoint(body: SqlValidateRequest) -> SqlValidateResponse:
    err = validate_sql(body.sql)
    return SqlValidateResponse(valid=err is None, error=err)


@router.get("/history")
async def query_history(limit: int = 20) -> list[QueryHistoryItem]:
    recs = await QueryRepo.list_all(limit=limit)
    return [
        QueryHistoryItem(
            id=str(r.id), question=r.question, generated_sql=r.generated_sql,
            insights=r.insight_text, created_at=str(r.created_at),
        )
        for r in recs
    ]
