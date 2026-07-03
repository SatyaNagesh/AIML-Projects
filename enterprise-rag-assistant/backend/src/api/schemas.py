from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str
    k: int = 5


class QueryResponse(BaseModel):
    answer: str
    sources: list[str] = []
    context: list[dict] = []


class IngestResponse(BaseModel):
    filename: str
    chunks_created: int
    pages_loaded: int


class DocumentInfo(BaseModel):
    id: str
    filename: str
    chunk_count: int
    uploaded_at: str


class SummaryResponse(BaseModel):
    summary: str


class CollectionStats(BaseModel):
    collection: str
    document_count: int
    chunk_count: int
