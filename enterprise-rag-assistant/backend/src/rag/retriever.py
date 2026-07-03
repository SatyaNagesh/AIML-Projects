import logging

from src.ingestion.embedder import VectorStore

logger = logging.getLogger(__name__)


def retrieve_context(query: str, k: int = 5) -> list[dict]:
    store = VectorStore()
    results = store.similarity_search_with_score(query, k=k)
    return [
        {
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "chunk_id": doc.metadata.get("chunk_id", 0),
            "relevance": round(score, 3),
        }
        for doc, score in results
    ]
