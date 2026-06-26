# Personal RAG System

A self-hosted **Advanced RAG** (Retrieval-Augmented Generation) system built over a personal knowledge base, powered by FastAPI, ChromaDB, and OpenAI.

---

## What is Advanced RAG?

**Naive RAG** pipelines suffer from low retrieval quality — vague queries return noisy chunks, and the LLM hallucinates from weak context. Advanced RAG addresses this across three stages:

```
Pre-Retrieval       Retrieval            Post-Retrieval
──────────────      ─────────            ──────────────
Query Rewriting  →  Hybrid Search    →   Re-ranking
HyDE             →  Semantic + BM25  →   Context Compression
                                     →   Answer Generation
```

---

## Module Breakdown

| Module | Technology | Purpose |
|---|---|---|
| **Document Loading** | LangChain loaders | Parse `.md` and `.pdf` from the knowledge base |
| **Chunking** | LangChain text splitters | Split documents into semantically meaningful chunks |
| **Embedding** | `text-embedding-3-small` (OpenAI) | Convert chunks into dense vectors |
| **Vector Store** | ChromaDB (local) | Persist and search vectors |
| **BM25 Store** | `rank_bm25` | Keyword-based sparse retrieval |
| **Query Rewriting** | LLM prompt | Rewrite user queries to improve retrieval recall |
| **HyDE** | LLM-generated hypothetical answer | Use a fake answer as a retrieval probe to boost recall |
| **Hybrid Search** | Vector + BM25 fusion (RRF) | Combine semantic and keyword search results |
| **Re-ranking** | CrossEncoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) | Re-score and re-order retrieved chunks |
| **Generation** | Claude / GPT | Generate the final grounded answer |
| **API Layer** | FastAPI | Expose query and ingestion endpoints |

---

## Project Structure

```
personal RAG/
├── knowledge_base/            # Source documents (.md, .pdf) — do not modify
├── backend/
│   ├── main.py                # FastAPI entry point
│   ├── config.py              # Centralized config (model names, paths, parameters)
│   ├── ingestion/
│   │   ├── loader.py          # Load .md and .pdf files
│   │   └── chunker.py         # Chunking strategies with metadata
│   ├── retrieval/
│   │   ├── embedder.py        # OpenAI embedding wrapper
│   │   ├── vector_store.py    # ChromaDB read/write
│   │   ├── bm25_store.py      # BM25 index build and query
│   │   └── hybrid.py          # Reciprocal Rank Fusion (RRF) over both stores
│   ├── advanced/
│   │   ├── query_rewriter.py  # LLM-based query rewriting
│   │   ├── hyde.py            # Hypothetical Document Embedding
│   │   └── reranker.py        # CrossEncoder re-ranking
│   ├── generation/
│   │   └── generator.py       # Final answer generation with context
│   └── api/
│       └── routes.py          # FastAPI route definitions
└── requirements.txt
```

---

## Data Flow — One Full Query

```
User: "What did Jay do at Manulife?"
        ↓
1. Query Rewriting
   → "Manulife GenAI RAG project, technical details, outcomes, HR assistant"
        ↓
2. HyDE (Hypothetical Document Embedding)
   → LLM generates a fake answer → used as an additional retrieval probe
        ↓
3. Hybrid Search
   → Semantic search (ChromaDB) + BM25 keyword search → Top-10 candidates
        ↓
4. Re-ranking (CrossEncoder)
   → Score all 10 against the original query → keep Top-3
        ↓
5. Answer Generation
   → LLM receives [original query + Top-3 chunks] → generates grounded answer
        ↓
User sees: a precise, source-grounded response
```

---


## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Run ingestion (index your knowledge base)
python -m backend.ingestion.run

# Start the API server
uvicorn backend.main:app --reload
```

---

## Design Decisions

- **ChromaDB over Pinecone/Weaviate** — local-first, zero infra cost, perfect for a personal system.
- **HyDE + Query Rewriting together** — they are complementary: rewriting improves the query signal; HyDE expands the retrieval surface.
- **RRF fusion** — Reciprocal Rank Fusion is parameter-free and robust; no need to tune score weights between vector and BM25.
- **CrossEncoder re-ranking** — more accurate than bi-encoder similarity alone, runs fast on CPU for small Top-K sets.
