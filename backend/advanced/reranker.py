"""
reranker.py — CrossEncoder re-ranking of retrieved chunks.

Problem it solves:
  Bi-encoder retrieval (vector search) is fast but approximate.
  It embeds the query and each document *independently*, then compares vectors.
  This means it cannot model the *interaction* between query and document.

  CrossEncoder solves this: it takes (query, document) as a *pair* and scores
  them jointly using a full attention transformer. It can see exactly which
  words in the document answer which words in the query.

  The trade-off: CrossEncoder is 10-100x slower than bi-encoder, so we only
  run it on the small set of candidates already retrieved (TOP_K_RETRIEVAL=10),
  not the full corpus.

Pipeline position:
  Hybrid Search (10 candidates) → CrossEncoder → Top 3 → LLM

Model: cross-encoder/ms-marco-MiniLM-L-6-v2
  - Trained on MS MARCO passage ranking dataset (real web queries)
  - Very small (22M params), runs fast on CPU
  - Outputs a raw logit score (higher = more relevant), not a probability

Why not use a larger model?
  For a personal RAG with 38 chunks and Top-10 candidates, MiniLM-L-6 is
  more than sufficient and adds <200ms latency on CPU.
"""

from typing import List, Optional
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

from backend.config import TOP_K_RERANK

_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
_encoder: Optional[CrossEncoder] = None  # lazy-loaded on first call


def _get_encoder() -> CrossEncoder:
    global _encoder
    if _encoder is None:
        print(f"[Reranker] Loading CrossEncoder model '{_MODEL_NAME}'...")
        _encoder = CrossEncoder(_MODEL_NAME)
    return _encoder


def rerank(query: str, docs: List[Document], top_k: int = TOP_K_RERANK) -> List[Document]:
    """
    Score each (query, doc) pair with a CrossEncoder and return top_k results.

    Args:
        query: the original user question (NOT the rewritten one —
               we score against what the user actually asked)
        docs:  candidate documents from hybrid search
        top_k: number of documents to return after re-ranking
    """
    if not docs:
        return []

    encoder = _get_encoder()

    # Build (query, passage) pairs for the CrossEncoder
    pairs = [(query, doc.page_content) for doc in docs]
    scores = encoder.predict(pairs)  # returns a numpy array of floats

    # Attach score to each doc and sort
    for doc, score in zip(docs, scores):
        doc.metadata["rerank_score"] = round(float(score), 4)

    reranked = sorted(docs, key=lambda d: d.metadata["rerank_score"], reverse=True)

    print(
        f"[Reranker] {len(docs)} candidates → Top {top_k} | "
        f"scores: {[d.metadata['rerank_score'] for d in reranked[:top_k]]}"
    )
    return reranked[:top_k]
