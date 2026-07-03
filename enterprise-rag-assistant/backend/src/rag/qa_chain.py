import logging

from src.llm.client import LLMClient
from src.rag.retriever import retrieve_context

logger = logging.getLogger(__name__)

QA_SYSTEM = (
    "You are an enterprise knowledge assistant. Answer the user's question "
    "based ONLY on the provided context from company documents. "
    "If the context does not contain enough information, say so.\n\n"
    "Rules:\n"
    "1. Cite sources inline using [Source: filename] notation\n"
    "2. Be concise and accurate\n"
    "3. If the context is insufficient, state what's missing\n"
    "4. Format answers in markdown for readability"
)

SUMMARIZE_SYSTEM = (
    "You are a document summarization expert. Summarize the following "
    "document context concisely while preserving key information, "
    "data points, and conclusions. Include source references."
)


async def ask_question(question: str, k: int = 5) -> dict:
    llm = LLMClient()

    context_chunks = retrieve_context(question, k=k)
    if not context_chunks:
        return {
            "answer": "No relevant documents found. Please upload documents first.",
            "sources": [],
            "context": [],
        }

    context_text = "\n\n".join(
        (
            f"[Source: {c['source']} (chunk {c['chunk_id']}, "
            f"relevance {c['relevance']})]\n{c['content']}"
        )
        for c in context_chunks
    )

    answer = await llm.generate(
        system=QA_SYSTEM,
        user=f"Context:\n{context_text}\n\nQuestion: {question}",
        temperature=0.15,
        max_tokens=2048,
    )

    sources = list({c["source"] for c in context_chunks})

    return {
        "answer": answer,
        "sources": sources,
        "context": context_chunks,
    }


async def summarize_document(document_text: str) -> dict:
    llm = LLMClient()

    summary = await llm.generate(
        system=SUMMARIZE_SYSTEM,
        user=f"Document content:\n\n{document_text[:16000]}",
        temperature=0.2,
        max_tokens=2048,
    )

    return {"summary": summary}
