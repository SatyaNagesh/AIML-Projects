from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str
    dataset_id: str


class QueryResponse(BaseModel):
    id: str
    question: str
    generated_sql: str
    results: list[dict]
    columns: list[str]
    row_count: int
    insights: str
    chart_html: str | None = None
    chart_id: str | None = None


class ChartRequest(BaseModel):
    title: str
    chart_type: str
    dataset_id: str
    sql_query: str | None = None
    config: dict | None = None


class ChartResponse(BaseModel):
    id: str
    title: str
    chart_type: str
    html: str


class DashboardCreate(BaseModel):
    title: str
    chart_ids: list[str]


class DashboardResponse(BaseModel):
    id: str
    title: str
    html: str


class ReportCreate(BaseModel):
    title: str
    query_ids: list[str]


class ReportResponse(BaseModel):
    id: str
    title: str
    html: str


class DatasetResponse(BaseModel):
    id: str
    name: str
    filename: str
    table_name: str
    row_count: int
    column_info: list[dict] | None = None
    created_at: str


class SqlValidateRequest(BaseModel):
    sql: str


class SqlValidateResponse(BaseModel):
    valid: bool
    error: str | None = None


class QueryHistoryItem(BaseModel):
    id: str
    question: str
    generated_sql: str
    insights: str | None = None
    created_at: str
