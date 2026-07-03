# Personal Advanced RAG System -- Technical Deep Dive

## 1. Project Overview

### One-Sentence Summary

This project is called "Ask Me Anything","Interactive AI Portfolio", "Interactive Resume"
I built a self-hosted **Advanced Retrieval-Augmented Generation (RAG)**
system over my personal knowledge base using **FastAPI, ChromaDB, OpenAI
Embeddings, BM25, Hybrid Retrieval, HyDE, Query Rewriting, and
CrossEncoder Re-ranking**.

The goal was to build an AI assistant capable of answering questions
based on my own documents---including project notes, resumes, technical
documentation, PDFs, and learning materials---while minimizing
hallucinations through high-quality retrieval.

------------------------------------------------------------------------

# 2. What is RAG?

RAG (Retrieval-Augmented Generation) combines information retrieval with
Large Language Models.

Instead of relying solely on the LLM's pretrained knowledge, the system
first retrieves relevant documents from an external knowledge base
before generating an answer.

Pipeline:

``` text
User Question
      ↓
Retrieve Relevant Documents
      ↓
Question + Retrieved Context
      ↓
LLM
      ↓
Grounded Answer
```

This enables the model to answer questions using private, up-to-date
knowledge instead of memorized information.

------------------------------------------------------------------------

# 3. Problems with Naive RAG

A traditional RAG pipeline usually looks like this:

``` text
User Query
      ↓
Embedding
      ↓
Vector Search
      ↓
Top-K Chunks
      ↓
LLM Answer
```

Although simple, this approach often suffers from:

-   Vague user queries
-   Low retrieval recall
-   Noisy retrieved chunks
-   Weak semantic matching
-   Hallucinations caused by poor context

For example:

**User Query**

> What did Jay do at Manulife?

The document may actually contain:

> Built an internal HR GenAI assistant during the Manulife practicum...

A simple vector search may miss this information because the query lacks
important keywords.

------------------------------------------------------------------------

# 4. Advanced RAG Architecture

The system improves retrieval quality across three stages.

``` text
Pre-Retrieval
    ↓
Retrieval
    ↓
Post-Retrieval
```

Complete pipeline:

``` text
User Query
      ↓
Query Rewriting
      ↓
HyDE
      ↓
Hybrid Retrieval
      ↓
RRF Fusion
      ↓
CrossEncoder Re-ranking
      ↓
Context Selection
      ↓
LLM Generation
```

------------------------------------------------------------------------

# 5. Technology Stack

  Component            Technology
  -------------------- --------------------------------------
  Backend              FastAPI
  Document Loading     LangChain Loaders
  Chunking             LangChain Text Splitters
  Embedding            OpenAI text-embedding-3-small
  Vector Database      ChromaDB
  Sparse Retrieval     BM25
  Hybrid Retrieval     RRF Fusion
  Query Optimization   Query Rewriting + HyDE
  Re-ranking           cross-encoder/ms-marco-MiniLM-L-6-v2
  LLM                  GPT / Claude

------------------------------------------------------------------------

# 6. System Architecture

``` text
knowledge_base/
backend/
    ingestion/
    retrieval/
    advanced/
    generation/
    api/
```

## knowledge_base

Stores original Markdown and PDF documents.

## ingestion

Responsible for:

-   Loading documents
-   Chunking documents
-   Building embeddings
-   Creating indexes

## retrieval

Contains:

-   Embedding generation
-   ChromaDB vector search
-   BM25 search
-   Hybrid retrieval

## advanced

Implements:

-   Query Rewriting
-   HyDE
-   CrossEncoder Re-ranking

## generation

Generates the final answer using retrieved context.

## api

Exposes REST endpoints through FastAPI.

------------------------------------------------------------------------

# 7. Ingestion Pipeline

Before users can ask questions, documents must be indexed.

Pipeline:

``` text
Documents
     ↓
Loader
     ↓
Chunking
     ↓
Embedding
     ↓
ChromaDB
     ↓
BM25 Index
```

## Document Loading

LangChain loaders parse:

-   Markdown
-   PDF

Each document contains:

-   page_content
-   metadata

Metadata includes information such as:

-   source filename
-   page number
-   chunk ID

------------------------------------------------------------------------

## Chunking

Entire documents are too large for embeddings.

Documents are split into semantic chunks.

Typical parameters:

-   Chunk Size: 500--1000 tokens
-   Chunk Overlap: 50--150 tokens

Overlap preserves context across chunk boundaries.

------------------------------------------------------------------------

# 8. Embeddings

Embeddings convert text into dense vectors.

Example:

    "Built a GenAI HR assistant"

↓

    [0.23, -0.12, ...]

Semantic similarity becomes geometric distance.

Similar concepts produce similar vectors.

The project uses:

**text-embedding-3-small**

Advantages:

-   Low cost
-   Fast inference
-   Good semantic quality

------------------------------------------------------------------------

# 9. ChromaDB

ChromaDB is a local vector database.

It stores:

-   chunk text
-   embedding vectors
-   metadata

When a user submits a question:

    Question
        ↓
    Embedding
        ↓
    Vector Similarity Search

This is called **Dense Retrieval**.

Advantages:

-   Understands semantic similarity
-   Finds related concepts

Weakness:

Less effective for exact keywords, acronyms, and IDs.

------------------------------------------------------------------------

# 10. BM25

BM25 is a traditional sparse retrieval algorithm.

Instead of semantic similarity, it ranks documents using:

-   TF (Term Frequency)
-   IDF (Inverse Document Frequency)
-   Document length normalization

Advantages:

-   Excellent keyword matching
-   Strong for names, IDs, acronyms, technical terms

Weakness:

-   Cannot understand semantic similarity

------------------------------------------------------------------------

# 11. Query Rewriting

Query Rewriting improves retrieval before searching.

Example:

Original query:

    What did Jay do at Manulife?

Rewritten query:

    Manulife GenAI project, HR assistant, internship, technical implementation, business impact

Benefits:

-   Expands keywords
-   Removes ambiguity
-   Improves retrieval recall
-   Produces cleaner search queries

------------------------------------------------------------------------

# 12. HyDE

HyDE stands for:

**Hypothetical Document Embeddings**

Instead of searching using the original query, the system first asks an
LLM to generate a hypothetical answer.

Example:

    Jay built an internal GenAI HR assistant using retrieval-augmented generation...

The hypothetical answer is embedded and used as an additional retrieval
probe.

Important:

The generated text is **not** shown to the user.

It only improves retrieval quality.

------------------------------------------------------------------------

# 13. Why Use Both Query Rewriting and HyDE?

They solve different problems.

Query Rewriting:

-   Improves the user query

HyDE:

-   Creates a richer semantic retrieval probe

Together they significantly improve recall.

------------------------------------------------------------------------

# 14. Hybrid Search

The system combines:

-   Dense Retrieval (Vector Search)
-   Sparse Retrieval (BM25)

Both retrieval methods return candidate chunks.

These candidates are merged using:

**Reciprocal Rank Fusion (RRF).**

------------------------------------------------------------------------

# 15. Reciprocal Rank Fusion (RRF)

Vector similarity scores and BM25 scores are not directly comparable.

Instead of combining raw scores, RRF combines rankings.

Approximate formula:

    score = Σ 1 / (k + rank)

Advantages:

-   Parameter-free
-   Robust
-   Simple
-   No score normalization required

------------------------------------------------------------------------

# 16. Re-ranking

Hybrid retrieval maximizes recall but still retrieves noisy chunks.

The system therefore applies a second-stage ranking model.

Model:

    cross-encoder/ms-marco-MiniLM-L-6-v2

This CrossEncoder directly scores:

    (Query, Document)
        ↓
    Relevance Score

Only the highest-ranked chunks are kept.

------------------------------------------------------------------------

# 17. Bi-Encoder vs CrossEncoder

## Bi-Encoder

-   Encodes query and document independently
-   Fast
-   Suitable for large-scale retrieval

Weakness:

-   Lower ranking accuracy

------------------------------------------------------------------------

## CrossEncoder

-   Encodes query and document together
-   Higher accuracy
-   Better relevance estimation

Weakness:

-   Slower

Therefore:

Stage 1:

Fast Hybrid Retrieval

↓

Stage 2:

CrossEncoder Re-ranking

------------------------------------------------------------------------

# 18. Context Compression

Even after re-ranking, sending every chunk to the LLM is inefficient.

The system therefore:

-   Keeps only Top-3 chunks
-   Removes redundant information
-   Minimizes token usage

Benefits:

-   Lower cost
-   Faster inference
-   Less hallucination

------------------------------------------------------------------------

# 19. Answer Generation

The LLM receives:

-   Original user query
-   Retrieved context
-   System prompt

Example instruction:

    Answer only using the provided context.
    If the answer cannot be found,
    state that you do not know.

The LLM is responsible for reasoning and language generation---not
document retrieval.

------------------------------------------------------------------------

# 20. End-to-End Query Flow

Example:

    User:
    What did Jay do at Manulife?

Pipeline:

``` text
User Query
      ↓
FastAPI Endpoint
      ↓
Query Rewriting
      ↓
HyDE
      ↓
Vector Search + BM25
      ↓
RRF Fusion
      ↓
CrossEncoder Re-ranking
      ↓
Top Context Chunks
      ↓
GPT / Claude
      ↓
Grounded Answer
```

------------------------------------------------------------------------

# 21. Design Decisions

## Why ChromaDB?

-   Local-first
-   No infrastructure cost
-   Easy deployment
-   Perfect for personal projects

------------------------------------------------------------------------

## Why Hybrid Retrieval?

Vector search understands semantics.

BM25 understands keywords.

Together they provide better recall.

------------------------------------------------------------------------

## Why CrossEncoder?

Hybrid retrieval focuses on recall.

CrossEncoder improves precision.

This two-stage retrieval pipeline balances speed and accuracy.

------------------------------------------------------------------------

## Why FastAPI?

FastAPI provides:

-   Lightweight REST APIs
-   High performance
-   Automatic Swagger documentation
-   Easy deployment

------------------------------------------------------------------------

# 22. Project Highlights

-   Built a modular self-hosted Advanced RAG backend.
-   Implemented document ingestion for Markdown and PDF.
-   Combined dense vector retrieval with BM25 keyword retrieval.
-   Improved recall using Query Rewriting and HyDE.
-   Applied CrossEncoder re-ranking to improve precision.
-   Reduced hallucinations through grounded context selection.

------------------------------------------------------------------------

# 23. Common Interview Questions

## Why is this Advanced RAG?

Because retrieval is optimized before, during, and after search through
Query Rewriting, HyDE, Hybrid Retrieval, and CrossEncoder Re-ranking.

------------------------------------------------------------------------

## Why use HyDE?

It generates a hypothetical answer that serves as a richer semantic
retrieval probe, improving recall for vague queries.

------------------------------------------------------------------------

## Why use BM25?

BM25 handles exact keyword matching, acronyms, and technical terms
better than embeddings.

------------------------------------------------------------------------

## Why use RRF?

RRF merges rankings instead of incompatible retrieval scores, making
hybrid retrieval robust and parameter-free.

------------------------------------------------------------------------

## Why use a CrossEncoder?

Hybrid retrieval maximizes recall.

CrossEncoder improves precision by directly evaluating query-document
relevance.

------------------------------------------------------------------------

## How do you reduce hallucinations?

-   Better retrieval quality
-   CrossEncoder re-ranking
-   Context filtering
-   Grounded prompting
-   Restricting answers to retrieved evidence

------------------------------------------------------------------------

# 24. Resume Bullet Points

-   Built a self-hosted Advanced RAG system using FastAPI, ChromaDB,
    BM25, OpenAI Embeddings, and CrossEncoder Re-ranking.
-   Designed a modular ingestion pipeline for Markdown and PDF
    documents.
-   Implemented Query Rewriting, HyDE, Hybrid Retrieval, and Reciprocal
    Rank Fusion to improve retrieval recall.
-   Applied CrossEncoder re-ranking to improve precision before final
    LLM generation.
-   Built a modular backend architecture separating ingestion,
    retrieval, generation, and API layers for maintainability and
    scalability.
