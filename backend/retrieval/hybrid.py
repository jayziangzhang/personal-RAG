"""
hybrid.py — Reciprocal Rank Fusion (RRF) over vector + BM25 results.

RRF formula for a single document d:
    RRF_score(d) = Σ 1 / (k + rank_i(d))

Where:
  - rank_i(d) is the rank of document d in retrieval list i (1-indexed)
  - k is a constant (default 60) that dampens the impact of top ranks
  - Σ sums across all retrieval lists (vector + BM25 in our case)

Why RRF instead of score normalisation?
  Vector distances and BM25 scores live on completely different scales —
  normalising them requires tuning weights. RRF only cares about rank order,
  which is scale-free and requires zero tuning.

Example:
  Vector results:  [chunk_A(rank1), chunk_B(rank2), chunk_C(rank3)]
  BM25 results:    [chunk_C(rank1), chunk_A(rank2), chunk_D(rank3)]

  chunk_A: 1/(60+1) + 1/(60+2) = 0.01639 + 0.01613 = 0.03252
  chunk_C: 1/(60+3) + 1/(60+1) = 0.01587 + 0.01639 = 0.03226
  chunk_B: 1/(60+2)             = 0.01613
  chunk_D: 1/(60+3)             = 0.01587

  Final order: chunk_A > chunk_C > chunk_B > chunk_D
"""

from typing import List, Dict
from langchain_core.documents import Document

from backend.retrieval import vector_store, bm25_store
from backend.config import TOP_K_RETRIEVAL

_RRF_K = 60  # standard constant, rarely needs tuning


def search(query: str, top_k: int = TOP_K_RETRIEVAL) -> List[Document]:
    """
    Run vector search + BM25 search in parallel, fuse with RRF, return top_k.
    """
    # Fetch more candidates from each source before fusion
    fetch_k = top_k * 2

    vector_results = vector_store.search(query, top_k=fetch_k)
    bm25_results = bm25_store.search(query, top_k=fetch_k)

    fused = _rrf_merge(
        lists=[vector_results, bm25_results],
        top_k=top_k,
    )
    return fused


def _rrf_merge(
    lists: List[List[Document]],
    top_k: int,
) -> List[Document]:
    """Merge multiple ranked lists using RRF and return top_k documents."""
    # Map chunk_id → (accumulated RRF score, Document object)
    scores: Dict[str, float] = {}
    doc_map: Dict[str, Document] = {}

    for ranked_list in lists:
        for rank, doc in enumerate(ranked_list, start=1):
            chunk_id = doc.metadata.get("chunk_id", doc.page_content[:60])
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (_RRF_K + rank)
            doc_map[chunk_id] = doc

    # Sort by fused score descending
    sorted_ids = sorted(scores, key=lambda cid: scores[cid], reverse=True)

    results: List[Document] = []
    for cid in sorted_ids[:top_k]:
        doc = doc_map[cid]
        doc.metadata["rrf_score"] = round(scores[cid], 6)
        results.append(doc)

    return results
