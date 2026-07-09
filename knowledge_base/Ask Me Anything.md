# Personal Advanced RAG System

## Overview

The Personal Advanced RAG System is a self-hosted Retrieval-Augmented Generation platform built over a personal knowledge base containing project notes, resume details, learning materials, and PDF documents. It exposes the knowledge base as a natural-language question-answering service.

The system was built with FastAPI, ChromaDB, BM25, OpenAI embeddings, LLM-based query rewriting, HyDE, hybrid retrieval, and cross-encoder re-ranking. The design goal is to improve retrieval quality and generate grounded answers from private documents, rather than sending documents directly to a large language model.

## RAG Concept

Retrieval-Augmented Generation (RAG) addresses the limitation that a standalone LLM only knows its training data and has no access to private documents, company projects, or recent material. Instead of answering directly, a RAG system first retrieves relevant content from a knowledge base and injects it into the LLM prompt as context.

Pipeline: User Question → Retrieve relevant documents → Send question + retrieved context to LLM → Generate grounded answer.

## Limitations of Naive RAG

A naive RAG pipeline performs a single pass: User Query → Embedding → Vector Search → Top-K Chunks → LLM Answer.

Known failure modes of naive RAG include: short user queries carrying insufficient information, ambiguous phrasing, vector search returning semantically similar but incorrect chunks, keyword search (BM25) missing synonyms, noise contaminating the Top-K results, and the LLM hallucinating when given weak context.

Advanced RAG addresses these failure modes by optimizing before retrieval, during retrieval, and after retrieval, instead of relying on a single vector search.

## Three-Stage Architecture

The system is organized into three stages:

- Pre-Retrieval: makes the user query more retrievable. Components: Query Rewriting, HyDE.
- Retrieval: finds candidate material from the knowledge base. Components: Vector Search, BM25 Search, Hybrid Search, RRF Fusion.
- Post-Retrieval: re-orders, filters, and compresses the retrieved material. Components: CrossEncoder Re-ranking, Context Compression, Answer Generation.

Full pipeline (left to right): User Query → Query Rewriting → HyDE → Hybrid Retrieval (Vector + BM25) → RRF Fusion → CrossEncoder Re-ranking → Context Selection / Compression → Final Answer Generation.

## Technology Stack

Backend: FastAPI. Document loading: LangChain loaders. Chunking: LangChain text splitters. Embedding: OpenAI text-embedding-3-small. Vector database: ChromaDB. Keyword search: rank_bm25. Hybrid retrieval: Vector Search + BM25 fused with Reciprocal Rank Fusion (RRF). Query optimization: LLM-based query rewriting and HyDE. Re-ranking: CrossEncoder ms-marco-MiniLM-L-6-v2. Generation: GPT / Claude.

## Project Structure

The backend follows a modular design:

```
personal-rag/
├── knowledge_base/      # source documents (md, pdf, notes, resume material)
├── backend/
│   ├── main.py          # FastAPI entry point (uvicorn backend.main:app)
│   ├── config.py        # centralized configuration
│   ├── ingestion/       # loader.py, chunker.py
│   ├── retrieval/       # embedder.py, vector_store.py, bm25_store.py, hybrid.py
│   ├── advanced/        # query_rewriter.py, hyde.py, reranker.py
│   ├── generation/      # LLM answer generation
│   └── api/             # routes.py: POST /ingest, POST /query, GET /health
└── requirements.txt
```

- knowledge_base/ holds the raw source-of-truth documents and is never modified directly.
- config.py centralizes tunable parameters: embedding model name, LLM model name, chunk size, chunk overlap, top_k, ChromaDB path, BM25 parameters, and reranker model name. Centralizing configuration avoids hard-coded parameters and simplifies tuning.
- ingestion/ converts raw documents into retrievable chunks; retrieval/ implements dense, sparse, and hybrid search; advanced/ contains the Advanced RAG enhancement modules; generation/ calls the LLM; api/ defines the HTTP endpoints.

## Ingestion Pipeline

Indexing precedes question answering. Ingestion flow: Documents → Load → Split into chunks → Generate embeddings → Store in ChromaDB → Build BM25 index.

### Document Loading

LangChain loaders parse Markdown and PDF files into a unified Document format. Markdown is plain text and simple to load. PDF is more complex because of body text, headings, tables, page numbers, line-break artifacts, and scanned images. Each Document contains page_content and metadata. Metadata fields include source file name, page number, section title, creation time, and chunk id. Metadata enables source citation in generated answers.

### Chunking

Documents are split into chunks because full documents are too long to embed or to fit into an LLM prompt. A 20-page PDF may become roughly 200 chunks, each a relatively self-contained semantic unit. Typical parameters: chunk_size of 500–1000 tokens and chunk_overlap of 50–150 tokens. Overlap exists because a hard cut can split a sentence or concept across two chunks, leaving each chunk semantically incomplete; overlapping tokens preserve continuity across chunk boundaries.

## Embedding

An embedding converts text into a high-dimensional numeric vector such that semantically similar texts are close in vector space. For example, "HR chatbot", "employee assistant", and "internal GenAI assistant" use different words but map to nearby vectors. The system uses OpenAI text-embedding-3-small, chosen for low cost, fast inference, and sufficient quality for a personal knowledge base.

## ChromaDB (Dense Retrieval)

ChromaDB is a local vector database storing chunk text, embedding vectors, metadata, and document ids. At query time the query is embedded and ChromaDB performs similarity search over stored vectors. This is dense retrieval (semantic search).

Strength: understands semantic similarity. Weakness: can be unreliable for exact keywords, proper nouns, acronyms, and numbers (for example OINP, PGWP, BM25, Redis, Manulife), where lexical matching is more stable.

## BM25 (Sparse Retrieval)

BM25 is a classical keyword-ranking algorithm based on term frequency (TF), inverse document frequency (IDF), and document length normalization. It ranks chunks by lexical match: a query containing "Manulife" prioritizes chunks containing that token, and rare terms (HyDE, CrossEncoder, OINP) receive high weight.

Strengths: precise keyword matching; robust for proper nouns, identifiers, terminology, and acronyms; requires no embeddings. Weaknesses: no understanding of synonyms or semantics; paraphrased queries can miss relevant content. These complementary properties motivate hybrid search rather than using either method alone.

## Query Rewriting (Pre-Retrieval)

User queries are often short, colloquial, and information-poor, producing a weak retrieval signal. An LLM rewrites the query to add context, normalize phrasing, expand keywords, and remove ambiguity — for example expanding a short question about a person's work at Manulife into "Manulife GenAI RAG project, HR assistant, technical implementation, business impact, internship experience". The purpose is to raise recall: relevant documents must be retrieved in the first stage, because re-ranking cannot recover documents that were never retrieved.

## HyDE (Hypothetical Document Embeddings)

HyDE generates a hypothetical answer to the query with an LLM, embeds that hypothetical answer, and uses the embedding as the search probe instead of (or in addition to) the raw query. The generated passage typically contains richer semantic vocabulary than the original short query — terms like "GenAI", "proof-of-concept", "HR assistant", "RAG", "internal documents" — which improves retrieval recall.

The HyDE output is strictly a retrieval probe. It is never returned to the user as the final answer.

## Combining Query Rewriting and HyDE

The two techniques are complementary because they solve different problems. Query rewriting improves the representation of the user's question (query expansion). HyDE produces an answer-shaped semantic probe (semantic expansion). Together they increase the probability of retrieving relevant chunks before re-ranking.

## Hybrid Search and RRF Fusion

Hybrid search combines dense retrieval (ChromaDB semantic search) with sparse retrieval (rank_bm25 keyword search). Each retriever returns its own ranked candidate list, and the lists are fused.

Fusion uses Reciprocal Rank Fusion (RRF). Vector similarity scores (for example cosine similarity) and BM25 relevance scores live on different scales and cannot be added directly. RRF ignores raw scores and combines rank positions: score(d) = Σ 1 / (k + rank(d)) across retrievers. A document ranked highly by both retrievers accumulates the highest fused score.

RRF properties: no weight tuning required, independent of incomparable raw score scales, robust, simple to implement, and well suited to hybrid retrieval.

## CrossEncoder Re-ranking (Post-Retrieval)

Hybrid search returns a candidate set (for example Top-10) that still contains noise, so a second-stage re-ranker is applied: cross-encoder/ms-marco-MiniLM-L-6-v2.

Bi-Encoder vs CrossEncoder:

- Bi-Encoder (embedding retrieval): query and document are encoded independently into vectors, then compared by similarity. Fast, allows precomputing document embeddings, scales to large corpora; but the query and document never interact deeply, limiting precision.
- CrossEncoder: the query and chunk are concatenated into a single input, and the model outputs a direct relevance score for the pair. More accurate and detail-sensitive, but slow and impossible to precompute, so it is only applied to a small candidate set.

The resulting two-stage retrieval design: a cheap, fast hybrid retriever maximizes recall over the whole corpus (Top-10), then the CrossEncoder maximizes precision by re-scoring that small set, keeping Top-3.

## Context Compression

Context compression reduces the retrieved material to what the LLM actually needs. Long context increases cost; noisy context degrades answers; irrelevant content induces hallucination. The system keeps only the Top-3 re-ranked chunks, removes duplicated content, truncates irrelevant passages, preserves source metadata, and orders chunks by relevance. A heavier variant would use an LLM to summarize chunks; the current implementation performs lightweight selection-based compression after re-ranking.

## Answer Generation

The final step sends the original query, the selected context chunks, a system prompt, and answer instructions to GPT or Claude. A representative system prompt: "You are a grounded assistant. Answer the user's question using only the provided context. If the context does not contain enough information, say you don't know. Cite the source chunks when possible."

Division of responsibility: the retrieval pipeline finds the material; the LLM only organizes an answer from that material. This constraint reduces hallucination.

## End-to-End Query Flow

1. User query enters the FastAPI /query endpoint.
2. The query rewriter expands the query.
3. HyDE generates a hypothetical answer.
4. The system embeds the original query, rewritten query, and HyDE answer.
5. ChromaDB performs semantic search.
6. BM25 performs keyword search.
7. RRF fuses both result lists.
8. The CrossEncoder re-ranks the Top-10 chunks.
9. The system keeps the Top-3 most relevant chunks.
10. The generator sends the original query plus Top-3 chunks to GPT / Claude.
11. The final grounded answer is returned to the user.

Compact pipeline view: User Query → FastAPI /query → Query Rewriting → HyDE → Vector Search + BM25 → RRF Fusion → CrossEncoder Re-ranking → Top Context Chunks → LLM Generation → Grounded Answer.

## FastAPI Layer

FastAPI exposes the pipeline over HTTP. POST /ingest re-indexes the knowledge base; POST /query accepts a JSON body with a question field and returns an answer plus source list; GET /health reports service status. FastAPI was chosen for its light weight, speed, automatic Swagger documentation, fit with Python ML/AI tooling, and ease of deployment.

## Design Rationale

ChromaDB over Pinecone/Weaviate: the project is a local-first personal RAG system. ChromaDB provides zero infrastructure cost, easy local persistence, simple Python integration, and sufficient capacity for a small-to-medium personal knowledge base; a managed cloud vector database is unnecessary at this scale.

Hybrid instead of pure vector search: vector search understands semantics but is unstable for exact keywords and proper nouns (Manulife, Redis, OINP, PGWP, BM25, CrossEncoder), where BM25 is more reliable.

Hybrid instead of pure BM25: BM25 has no semantic understanding. A query phrased as "AI assistant" fails to match a document written as "GenAI HR chatbot" lexically, while vector search bridges the paraphrase. Dense and sparse retrieval are therefore combined.

RRF for fusion: vector and BM25 scores are not directly comparable, so raw-score addition is unreliable; rank-based fusion is robust and parameter-light.

CrossEncoder for the second stage: the first-stage retriever is recall-oriented and admits noise. The CrossEncoder scores each query–chunk pair jointly, giving higher precision. Because it only processes a small Top-K candidate set, latency remains acceptable.

Hallucination mitigation: improve retrieval quality, filter noise via re-ranking, restrict generation to top-relevant context, and instruct the model to answer only from provided context and to admit when the context is insufficient.

Scaling path: migrate from local ChromaDB to a managed vector database (Pinecone, Weaviate, or Qdrant), add asynchronous ingestion and background indexing jobs, cache embeddings and frequent queries, add retrieval observability, and track evaluation metrics such as recall@k, MRR, and answer faithfulness.

Planned improvements: automated RAG evaluation, source citation, user feedback logging, query caching, document-level access control, and an evaluation dashboard comparing naive, hybrid, and re-ranked RAG performance.

## Key Highlights

1. Built a modular self-hosted RAG backend with FastAPI.
2. Implemented an ingestion pipeline for Markdown and PDF documents, including loading, semantic chunking, metadata tracking, embedding generation, and local vector persistence.
3. Used hybrid retrieval combining dense vector search and BM25.
4. Improved retrieval quality with query rewriting, HyDE, and Reciprocal Rank Fusion.
5. Added CrossEncoder re-ranking to reduce noisy context before generation.
6. Designed a modular backend separating ingestion, retrieval, advanced optimization, generation, and API layers for maintainability and future scaling.
