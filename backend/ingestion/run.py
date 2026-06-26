"""
run.py — Ingestion entry point.

Run with:
    python -m backend.ingestion.run

Pipeline:
    load_documents() → split_documents() → ingest_chunks()
"""

from backend.ingestion.loader import load_documents
from backend.ingestion.chunker import split_documents
from backend.retrieval.vector_store import ingest_chunks
from backend.retrieval.bm25_store import build_index


def run_ingestion() -> None:
    docs = load_documents()
    chunks = split_documents(docs)
    ingest_chunks(chunks)   # → ChromaDB (vector search)
    build_index(chunks)     # → BM25 index (keyword search)
    print("[Ingestion] Done.")


if __name__ == "__main__":
    run_ingestion()
