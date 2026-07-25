# Personal RAG — Ask Me Anything

I built this as my personal interactive resume — an AI assistant that answers questions about my background, experience, and projects in first person. Instead of handing someone a static PDF, they can just ask.

Under the hood it's a self-hosted **Advanced RAG** system built with FastAPI, ChromaDB, BM25, OpenAI Embeddings, and CrossEncoder Re-ranking, deployed on Railway via Docker with a GitHub Pages frontend.

---

## Why Advanced RAG — Not Naive RAG

A naive RAG pipeline (`Query → Vector Search → Top-K → LLM`) breaks down in practice: vague queries miss relevant documents, vector search alone struggles with names and acronyms, and noisy top-K chunks cause hallucinations.

I improved retrieval across three stages:

```
Pre-Retrieval       Retrieval            Post-Retrieval
──────────────      ─────────            ──────────────
Query Rewriting  →  Hybrid Search    →   Re-ranking
HyDE             →  Semantic + BM25  →   Context Selection
                    RRF Fusion       →   Answer Generation
```

---

## Module Breakdown

| Module | Technology | Purpose |
|---|---|---|
| **Document Loading** | LangChain TextLoader | Parse `.md` files from the knowledge base |
| **Chunking** | LangChain RecursiveCharacterTextSplitter | Split documents into chunks (size=500, overlap=50) |
| **Embedding** | `text-embedding-3-small` (OpenAI) | Convert chunks into dense vectors |
| **Vector Store** | ChromaDB (local) | Persist and search vectors |
| **BM25 Store** | `rank_bm25` | Keyword-based sparse retrieval |
| **Query Rewriting** | GPT-4o-mini | Expand and clarify user queries before retrieval |
| **HyDE** | GPT-4o-mini | Generate a hypothetical answer as an additional retrieval probe |
| **Hybrid Search** | Vector + BM25 + RRF (k=60) | Fuse semantic and keyword results by rank |
| **Re-ranking** | CrossEncoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) | Re-score top-10 candidates, keep top-3 |
| **Generation** | GPT-4o-mini | Generate grounded first-person answer |
| **API Layer** | FastAPI | `/query`, `/ingest`, `/health` endpoints |
| **Notifications** | Resend API | Email notification on each query |

---

## Data Flow — One Full Query

```
User: "What did Jay do at Manulife?"
        ↓
1. Query Rewriting
   → "Manulife GenAI RAG project, technical details, outcomes, HR assistant"
        ↓
2. HyDE
   → LLM generates a hypothetical answer → embedded as extra retrieval probe
        ↓
3. Hybrid Search
   → ChromaDB (top-20) + BM25 (top-20) → RRF fusion → top-10 candidates
        ↓
4. CrossEncoder Re-ranking
   → Score all 10 against the original query → keep top-3
        ↓
5. Answer Generation
   → GPT-4o-mini receives [original query + top-3 chunks] → first-person answer
```

---

## Project Structure

```
personal RAG/
├── knowledge_base/            # Markdown source documents
├── backend/
│   ├── main.py                # FastAPI entry point
│   ├── config.py              # Centralized config
│   ├── ingestion/
│   │   ├── loader.py          # Load .md files
│   │   └── chunker.py         # Chunking with metadata
│   ├── retrieval/
│   │   ├── embedder.py        # OpenAI embedding wrapper
│   │   ├── vector_store.py    # ChromaDB read/write
│   │   ├── bm25_store.py      # BM25 index build and query
│   │   └── hybrid.py          # RRF fusion
│   ├── advanced/
│   │   ├── query_rewriter.py  # Query rewriting
│   │   ├── hyde.py            # HyDE
│   │   └── reranker.py        # CrossEncoder re-ranking
│   ├── generation/
│   │   └── generator.py       # Answer generation
│   ├── notifications/
│   │   └── mailer.py          # Resend email notification
│   └── api/
│       └── routes.py          # FastAPI routes
└── requirements.txt
```

---

## Design Decisions

- **ChromaDB over Pinecone/Weaviate** — local-first, zero infra cost, runs inside Docker with no external dependency.
- **Query Rewriting + HyDE together** — complementary: rewriting improves the query signal; HyDE expands the retrieval surface with a richer semantic probe.
- **RRF over score normalization** — parameter-free and robust; no need to tune mixing weights between vector and BM25 scores.
- **CrossEncoder after hybrid search** — hybrid retrieval maximizes recall; CrossEncoder improves precision. Running it on top-10 candidates (not the full corpus) keeps latency under 200ms on CPU.
- **GPT-4o-mini** — fast and cheap for grounded Q&A where retrieval does the heavy lifting.

---

## Getting Started

```bash
pip install -r requirements.txt
python -m backend.ingestion.run
uvicorn backend.main:app --reload
```
