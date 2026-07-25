# Ask Me Anything — Personal Interactive Resume (Advanced RAG Technical Deep Dive)

## Project Overview

I built this project — "Ask Me Anything" — as my personal interactive resume and AI portfolio. Instead of a static resume, anyone can ask me questions directly and get grounded, accurate answers about my background, experience, and projects.

Under the hood, it's a self-hosted **Advanced RAG (Retrieval-Augmented Generation)** system built on **FastAPI, ChromaDB, OpenAI Embeddings, BM25, Hybrid Retrieval, HyDE, Query Rewriting, and CrossEncoder Re-ranking**, deployed on Railway via Docker with a GitHub Pages frontend.

The core challenge I wanted to solve: how do you make an AI assistant that answers questions about a real person accurately, without hallucinating details?

---

## Why Advanced RAG — Not Naive RAG

A naive RAG pipeline looks like this:

```
User Query → Embedding → Vector Search → Top-K Chunks → LLM Answer
```

This works, but it breaks down in practice:
- Vague queries miss relevant documents
- Vector search alone struggles with exact names, acronyms, and technical terms
- The top-K chunks passed to the LLM are often noisy or only partially relevant
- The LLM fills in gaps by hallucinating

For example, if someone asks **"What did Jay do at Manulife?"**, the document might contain **"Built an internal HR GenAI assistant during the Manulife practicum"** — a simple vector search might miss this because the surface-level wording doesn't match.

I solved this with a three-stage Advanced RAG pipeline: Pre-Retrieval → Retrieval → Post-Retrieval.

---

## Full Pipeline

```
User Query
      ↓
Query Rewriting          ← Pre-Retrieval
      ↓
HyDE                     ← Pre-Retrieval
      ↓
Vector Search + BM25     ← Retrieval (Hybrid)
      ↓
RRF Fusion               ← Retrieval
      ↓
CrossEncoder Re-ranking  ← Post-Retrieval
      ↓
Top-3 Context Chunks
      ↓
GPT-4o-mini
      ↓
Grounded First-Person Answer
```

---

## Technology Stack

| Component | Technology |
|---|---|
| Backend | FastAPI |
| Deployment | Docker + Railway |
| Frontend | GitHub Pages (HTML/CSS/JS) |
| Document Loading | LangChain TextLoader |
| Chunking | LangChain RecursiveCharacterTextSplitter |
| Embedding | OpenAI text-embedding-3-small |
| Vector Database | ChromaDB (local) |
| Sparse Retrieval | BM25 (rank-bm25) |
| Hybrid Fusion | Reciprocal Rank Fusion (RRF, k=60) |
| Query Optimization | Query Rewriting + HyDE (GPT-4o-mini) |
| Re-ranking | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| Answer Generation | GPT-4o-mini |
| Notifications | Resend API (email on each query) |

---

## Ingestion Pipeline

Before queries can be answered, my knowledge base is indexed at container startup:

```
Markdown Documents
      ↓
LangChain TextLoader
      ↓
RecursiveCharacterTextSplitter (chunk_size=500, overlap=50)
      ↓
OpenAI text-embedding-3-small
      ↓
ChromaDB (dense vector index)
      ↓
BM25 Index (saved as .pkl)
```

Each chunk carries metadata: source filename and chunk ID. Currently the knowledge base has ~21 markdown files producing ~60+ chunks.

---

## Embeddings — text-embedding-3-small

I embed each chunk into a dense vector using OpenAI's `text-embedding-3-small`. This converts text into a high-dimensional vector where semantic similarity becomes geometric distance. I chose this model for its balance of cost, speed, and semantic quality — it outperforms the older ada-002 at lower cost.

---

## Hybrid Retrieval — Vector Search + BM25

I run two retrieval methods in parallel on every query:

**ChromaDB (Dense Retrieval)**
- Understands semantic similarity
- Finds conceptually related content even with different wording
- Weakness: struggles with exact keywords, acronyms, proper nouns

**BM25 (Sparse Retrieval)**
- Ranks by TF-IDF with document length normalization
- Excellent for exact keyword matching, names, technical terms
- Weakness: no semantic understanding

Each method fetches top-20 candidates (top_k × 2), then I fuse them with RRF.

---

## Reciprocal Rank Fusion (RRF)

Vector similarity scores and BM25 scores live on completely different scales — normalizing them requires tuning weights. Instead, I use RRF which only cares about rank order:

```
RRF_score(doc) = Σ 1 / (k + rank_i)    where k = 60
```

A document appearing at rank 1 in both lists scores higher than one appearing at rank 1 in only one list. This is parameter-free, robust, and requires no score normalization. The fused list is trimmed to top-10 candidates before re-ranking.

---

## Pre-Retrieval — Query Rewriting

Before searching, I rewrite the user's query using GPT-4o-mini to expand keywords and remove ambiguity.

Example:
- Original: `"What did Jay do at Manulife?"`
- Rewritten: `"Manulife GenAI project HR assistant internship technical implementation business impact"`

This improves retrieval recall by ensuring the search terms better match how the knowledge base is written.

---

## Pre-Retrieval — HyDE (Hypothetical Document Embeddings)

HyDE is a technique where instead of embedding the query directly, I ask GPT-4o-mini to generate a hypothetical answer first, then embed that answer as an additional retrieval probe.

Example hypothetical: `"Jay built an internal HR GenAI assistant at Manulife using RAG over internal policy documents..."`

This hypothetical is never shown to the user — it only serves as a richer semantic search vector. Combined with the rewritten query, it significantly improves recall for vague or open-ended questions.

---

## Post-Retrieval — CrossEncoder Re-ranking

Hybrid retrieval maximizes recall but the top-10 candidates still contain noise. I apply a CrossEncoder as a second-stage precision filter:

**Model:** `cross-encoder/ms-marco-MiniLM-L-6-v2` (22M params, trained on MS MARCO)

Unlike bi-encoders (which embed query and document independently), a CrossEncoder takes the `(query, document)` pair jointly and runs full attention across both. This gives it a much stronger understanding of query-document relevance, at the cost of speed.

```
Bi-encoder:  embed(query) vs embed(doc)  → fast, approximate
CrossEncoder: encode(query + doc)        → slower, precise
```

The CrossEncoder scores all 10 candidates and returns the top-3 to the LLM. Running it on 10 documents (not the full corpus) keeps latency under 200ms on CPU.

---

## Answer Generation

The top-3 re-ranked chunks are passed to GPT-4o-mini with a system prompt instructing it to:
- Answer in first person as Jay
- Use only the provided context
- Be specific and concrete
- If the context doesn't contain enough information, respond warmly and invite further conversation

Temperature is set to 0 for deterministic, factual answers.

---

## Why Each Design Decision

**ChromaDB** — local-first, no infrastructure cost, zero-config deployment inside Docker. Perfect for a personal project.

**BM25** — vector search alone misses names, acronyms, and exact technical terms. BM25 covers the gaps.

**RRF over score normalization** — avoids the need to tune mixing weights between two incompatible score distributions.

**CrossEncoder over larger re-ranker** — at ~60 chunks, MiniLM-L-6 is more than sufficient. Larger models would add latency with no meaningful quality gain.

**GPT-4o-mini over GPT-4o** — fast, cheap, and accurate enough for grounded Q&A where the heavy lifting is done by retrieval. The model's job here is language generation, not knowledge recall.

**FastAPI** — lightweight, async, auto-generates Swagger docs, straightforward Docker deployment.

---

## Architecture

```
knowledge_base/       ← Markdown source files
backend/
    ingestion/        ← Loader, chunker, vector + BM25 indexing
    retrieval/        ← ChromaDB search, BM25 search, hybrid RRF fusion
    advanced/         ← Query rewriting, HyDE, CrossEncoder re-ranking
    generation/       ← GPT-4o-mini answer generation
    notifications/    ← Resend email notification per query
    api/              ← FastAPI routes (/query, /ingest, /health)
Dockerfile            ← Runs ingestion at startup, then serves API
```

---

## What Makes This "Advanced" RAG

| Feature | Naive RAG | This System |
|---|---|---|
| Query optimization | ❌ | ✅ Query Rewriting + HyDE |
| Retrieval method | Vector only | ✅ Hybrid (Vector + BM25) |
| Result fusion | N/A | ✅ Reciprocal Rank Fusion |
| Re-ranking | ❌ | ✅ CrossEncoder |
| Hallucination control | Prompt only | ✅ Grounded context + prompt |
