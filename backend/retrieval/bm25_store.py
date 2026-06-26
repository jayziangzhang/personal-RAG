"""
bm25_store.py — Keyword-based retrieval using BM25.

BM25 (Best Match 25) is a classical IR algorithm that scores documents by:
  - Term Frequency (TF): how often the query word appears in a chunk
  - Inverse Document Frequency (IDF): rare words across all chunks score higher
  - Document length normalization: penalizes very long chunks

Why keep BM25 alongside vector search?
  Proper nouns like "Manulife", "RFID", "Linglong", "IDP Plus" may not have
  strong semantic neighbours in embedding space, but BM25 will find them
  exactly. Hybrid search gets the best of both worlds.

The index is built once at ingestion time and saved to disk (pickle).
At query time it is loaded from disk — no re-embedding needed.
"""

import pickle
from pathlib import Path
from typing import List

from rank_bm25 import BM25Okapi
from langchain_core.documents import Document

from backend.config import BM25_INDEX_PATH


# ── Index structure saved to disk ─────────────────────────────────────────────
# { "corpus": List[str], "metadatas": List[dict], "bm25": BM25Okapi }

def build_index(chunks: List[Document]) -> None:
    """Tokenise chunks and persist a BM25 index to disk."""
    corpus = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]

    # Simple whitespace tokenisation — good enough for English/mixed text
    tokenised = [doc.lower().split() for doc in corpus]
    bm25 = BM25Okapi(tokenised)

    payload = {"corpus": corpus, "metadatas": metadatas, "bm25": bm25}
    with open(BM25_INDEX_PATH, "wb") as f:
        pickle.dump(payload, f)

    print(f"[BM25] Index built with {len(corpus)} chunks → {BM25_INDEX_PATH}")


def search(query: str, top_k: int) -> List[Document]:
    """Return top_k chunks scored by BM25 for a query string."""
    if not Path(BM25_INDEX_PATH).exists():
        raise FileNotFoundError(
            f"BM25 index not found at {BM25_INDEX_PATH}. Run ingestion first."
        )

    with open(BM25_INDEX_PATH, "rb") as f:
        payload = pickle.load(f)

    bm25: BM25Okapi = payload["bm25"]
    corpus: List[str] = payload["corpus"]
    metadatas: List[dict] = payload["metadatas"]

    tokenised_query = query.lower().split()
    scores = bm25.get_scores(tokenised_query)

    # Pair each chunk with its score, sort descending, take top_k
    ranked = sorted(
        zip(scores, corpus, metadatas),
        key=lambda x: x[0],
        reverse=True,
    )[:top_k]

    docs: List[Document] = []
    for score, text, metadata in ranked:
        doc = Document(page_content=text, metadata=dict(metadata))
        doc.metadata["bm25_score"] = round(float(score), 4)
        docs.append(doc)

    return docs
