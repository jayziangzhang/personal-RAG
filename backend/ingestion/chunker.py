"""
chunker.py — Split documents into overlapping chunks.

Strategy:
  - RecursiveCharacterTextSplitter respects paragraph/sentence boundaries.
  - CHUNK_SIZE ~500 tokens ≈ 2000 chars (1 token ≈ 4 chars for English).
  - CHUNK_OVERLAP ensures context is not lost at chunk boundaries.
  - Each chunk inherits metadata from its parent document (source, file_type)
    and gets a unique chunk_id for upsert idempotency in ChromaDB.
"""

from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config import CHUNK_SIZE, CHUNK_OVERLAP


def split_documents(docs: List[Document]) -> List[Document]:
    """Split a list of Documents into chunks, preserving and extending metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE * 4,   # convert token estimate → chars
        chunk_overlap=CHUNK_OVERLAP * 4,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: List[Document] = []
    for doc in docs:
        splits = splitter.split_documents([doc])
        for i, chunk in enumerate(splits):
            # Stable ID: source filename + chunk index
            source = chunk.metadata.get("source", "unknown")
            chunk.metadata["chunk_id"] = f"{source}::chunk_{i}"
            chunks.append(chunk)

    print(f"[Chunker] {len(docs)} doc(s) → {len(chunks)} chunk(s)")
    return chunks
