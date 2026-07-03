import uuid

from fastapi import APIRouter, HTTPException, UploadFile

from src.api.schemas import (
    CollectionStats,
    IngestResponse,
    QueryRequest,
    QueryResponse,
    SummaryResponse,
)
from src.db.repository import DocumentRepository
from src.ingestion.embedder import VectorStore
from src.ingestion.pipeline import DocumentIngestionPipeline, generate_summary, process_question

router = APIRouter(prefix="/api/v1", tags=["rag"])


@router.post("/documents/upload", status_code=201)
async def upload_document(file: UploadFile) -> IngestResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    pipeline = DocumentIngestionPipeline()
    result = await pipeline.ingest(content, file.filename)

    repo = DocumentRepository()
    await repo.create(
        doc_id=str(uuid.uuid4()),
        filename=file.filename,
        chunk_count=result["chunks_created"],
    )

    return IngestResponse(**result)


@router.post("/query")
async def query_documents(req: QueryRequest) -> QueryResponse:
    result = await process_question(req.question)
    return QueryResponse(**result)


@router.post("/documents/summarize")
async def summarize_document(file: UploadFile) -> SummaryResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    result = await generate_summary(content, file.filename)
    return SummaryResponse(**result)


@router.post("/documents/search")
async def search_documents(query: str, k: int = 5) -> list[dict]:
    store = VectorStore()
    results = store.similarity_search_with_score(query, k=k)
    return [
        {
            "content": doc.page_content[:500],
            "source": doc.metadata.get("source", "unknown"),
            "relevance": round(score, 3),
        }
        for doc, score in results
    ]


@router.get("/documents")
async def list_documents() -> list[dict]:
    repo = DocumentRepository()
    return await repo.list_all()


@router.get("/stats")
async def get_stats() -> CollectionStats:
    store = VectorStore()
    stats = store.get_collection_stats()
    return CollectionStats(
        collection=stats["name"],
        document_count=0,
        chunk_count=stats["count"],
    )


@router.delete("/documents")
async def clear_documents() -> dict:
    store = VectorStore()
    store.delete_collection()
    repo = DocumentRepository()
    await repo.delete_all()
    return {"status": "cleared"}
