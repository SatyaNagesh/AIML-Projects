import logging
import os
import tempfile
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


async def load_document(file_path: str) -> list[Document]:
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
        docs = await loader.aload()
        logger.info("Loaded PDF: %s (%d pages)", file_path, len(docs))
    elif ext == ".txt":
        loader = TextLoader(file_path, encoding="utf-8")
        docs = await loader.aload()
        logger.info("Loaded text: %s", file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    for d in docs:
        d.metadata["source"] = os.path.basename(file_path)
    return docs


async def load_document_from_bytes(content: bytes, filename: str) -> list[Document]:
    suffix = Path(filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        return await load_document(tmp_path)
    finally:
        os.unlink(tmp_path)
