import logging

from src.ingestion.chunker import chunk_documents
from src.ingestion.embedder import VectorStore
from src.ingestion.loader import load_document_from_bytes

logger = logging.getLogger(__name__)


class DocumentIngestionPipeline:
    def __init__(self) -> None:
        self.store = VectorStore()

    async def ingest(self, content: bytes, filename: str) -> dict:
        docs = await load_document_from_bytes(content, filename)
        chunks = chunk_documents(docs)
        count = self.store.add_documents(chunks)
        return {
            "filename": filename,
            "chunks_created": count,
            "pages_loaded": len(docs),
        }


async def process_question(question: str) -> dict:
    from src.rag.qa_chain import ask_question as _ask
    return await _ask(question)


async def generate_summary(content: bytes, filename: str) -> dict:
    from src.rag.qa_chain import summarize_document
    docs = await load_document_from_bytes(content, filename)
    full_text = "\n\n".join(d.page_content for d in docs)
    return await summarize_document(full_text)
