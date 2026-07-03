import logging
import os

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from src.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, collection_name: str = "enterprise_docs") -> None:
        os.makedirs(settings.chroma_persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self.embeddings = OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            api_key=settings.openai_api_key,
        )
        self.collection_name = collection_name
        self.store = Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embeddings,
        )

    def add_documents(self, docs: list[Document]) -> int:
        ids = self.store.add_documents(docs)
        logger.info("Added %d chunks to ChromaDB collection '%s'", len(ids), self.collection_name)
        return len(ids)

    def similarity_search(self, query: str, k: int = 5) -> list[Document]:
        return self.store.similarity_search(query, k=k)

    def similarity_search_with_score(self, query: str, k: int = 5) -> list[tuple[Document, float]]:
        return self.store.similarity_search_with_relevance_scores(query, k=k)

    def delete_collection(self) -> None:
        try:
            self.client.delete_collection(self.collection_name)
            logger.info("Deleted collection '%s'", self.collection_name)
        except Exception:
            pass

    def get_collection_stats(self) -> dict:
        try:
            col = self.client.get_collection(self.collection_name)
            return {"name": self.collection_name, "count": col.count()}
        except Exception:
            return {"name": self.collection_name, "count": 0}
