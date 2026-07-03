"""
routes.py — FastAPI route definitions.

Two endpoints:

  POST /query
    The main RAG pipeline. Accepts a question, runs the full
    Advanced RAG flow, and returns the answer + sources.

  POST /ingest
    Re-indexes the knowledge base. Call this whenever you add or
    update files in knowledge_base/. Returns a summary of what was indexed.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from backend.advanced.query_rewriter import rewrite
from backend.advanced.hyde import generate_hypothetical_document
from backend.advanced.reranker import rerank
from backend.retrieval import vector_store, hybrid
from backend.generation.generator import generate
from backend.ingestion.run import run_ingestion
from backend.notifications.mailer import notify_async

router = APIRouter()


# ── Request / Response schemas ────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    use_hyde: bool = Field(default=True, description="Enable HyDE for extra retrieval coverage")
    use_rewrite: bool = Field(default=True, description="Enable query rewriting")

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    rewritten_query: Optional[str] = None

class IngestResponse(BaseModel):
    status: str
    message: str


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    """Run the full Advanced RAG pipeline for a question."""
    try:
        original = request.question

        # Step 1: Query Rewriting (optional)
        search_query = rewrite(original) if request.use_rewrite else original

        # Step 2: Hybrid Search on the (rewritten) query
        candidates = hybrid.search(search_query, top_k=10)

        # Step 3: HyDE — add extra candidates from a hypothetical document (optional)
        if request.use_hyde:
            hypothetical = generate_hypothetical_document(search_query)
            hyde_results = vector_store.search(hypothetical, top_k=5)

            seen = {doc.metadata.get("chunk_id") for doc in candidates}
            for doc in hyde_results:
                if doc.metadata.get("chunk_id") not in seen:
                    candidates.append(doc)
                    seen.add(doc.metadata.get("chunk_id"))

        # Step 4: Re-rank
        top_chunks = rerank(original, candidates, top_k=3)

        # Step 5: Generate
        result = generate(original, top_chunks)

        notify_async(original, result.answer, result.sources)

        return QueryResponse(
            answer=result.answer,
            sources=result.sources,
            rewritten_query=search_query if request.use_rewrite else None,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest", response_model=IngestResponse)
async def ingest() -> IngestResponse:
    """Re-index the knowledge base (run after adding/updating documents)."""
    try:
        run_ingestion()
        return IngestResponse(
            status="success",
            message="Knowledge base re-indexed successfully.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
