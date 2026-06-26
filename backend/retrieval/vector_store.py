"""
vector_store.py — ChromaDB read/write operations.

ChromaDB concepts you need to know:
  - Collection: equivalent to a table; stores documents + their vectors + metadata.
  - Upsert: insert or update by ID — makes ingestion idempotent (safe to re-run).
  - query(): takes a query_embedding and returns the nearest neighbours by
    cosine distance. We handle the embedding ourselves (via embedder.py) so we
    pass embeddings directly instead of letting Chroma call OpenAI internally.
"""

from typing import List, Dict, Any

import chromadb
from langchain_core.documents import Document

from backend.config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME
from backend.retrieval.embedder import embed_texts, embed_query


def _get_collection() -> chromadb.Collection:
    client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))
    return client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # cosine similarity
    )


def ingest_chunks(chunks: List[Document]) -> None:
    """Embed and upsert a list of chunks into ChromaDB."""
    collection = _get_collection()

    texts = [chunk.page_content for chunk in chunks]
    ids = [chunk.metadata["chunk_id"] for chunk in chunks]
    metadatas: List[Dict[str, Any]] = [chunk.metadata for chunk in chunks]

    print(f"[VectorStore] Embedding {len(texts)} chunks...")
    vectors = embed_texts(texts)

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=vectors,
        metadatas=metadatas,
    )
    print(f"[VectorStore] Upserted {len(ids)} chunks into '{CHROMA_COLLECTION_NAME}'")


def search(query: str, top_k: int) -> List[Document]:
    """Return top_k most similar chunks for a query string."""
    collection = _get_collection()
    query_vector = embed_query(query)

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    # Unpack ChromaDB's nested-list response (one list per query)
    docs: List[Document] = []
    for text, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        doc = Document(page_content=text, metadata=metadata)
        doc.metadata["score"] = round(1 - distance, 4)  # cosine similarity
        docs.append(doc)

    return docs
