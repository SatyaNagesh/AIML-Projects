import os

os.environ.setdefault("OPENAI_API_KEY", "sk-test-placeholder")

from langchain_core.documents import Document

from src.api.schemas import IngestResponse, QueryRequest, SummaryResponse
from src.ingestion.chunker import chunk_documents


def test_query_request():
    req = QueryRequest(question="What is RAG?")
    assert req.question == "What is RAG?"
    assert req.k == 5


def test_ingest_response():
    res = IngestResponse(filename="test.pdf", chunks_created=10, pages_loaded=3)
    assert res.filename == "test.pdf"
    assert res.chunks_created == 10


def test_summary_response():
    res = SummaryResponse(summary="This is a summary")
    assert "summary" in res.model_dump()


def test_chunking():
    docs = [Document(page_content="Hello world. " * 100, metadata={"source": "test.txt"})]
    chunks = chunk_documents(docs, chunk_size=200, chunk_overlap=20)
    assert len(chunks) > 1
    assert all(c.metadata.get("chunk_id") is not None for c in chunks)
