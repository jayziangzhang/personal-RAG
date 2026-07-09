# Manulife — HR Policy RAG (Proof of Concept)

## Overview

The HR Policy RAG project was a proof-of-concept technical validation at Manulife: an evaluation of whether Large Language Models could automatically answer employee questions grounded in internal HR policy documents. It is a distinct product from the later HR Policy Writer project (documented separately), which went to production.

## Project Background

Manulife HR received a large volume of repetitive employee inquiries regarding internal policies such as vacation policy, benefits, remote work, parental leave, and sick leave. Most questions arrived through email or phone, forcing HR specialists to repeatedly answer identical questions.

The goal was to investigate whether LLMs could automatically answer employee questions based on internal HR policy documents.

## Pain Points

HR employees spent significant time answering repetitive questions. Manually searching hundreds of policy documents was inefficient. The company wanted to evaluate whether Retrieval-Augmented Generation (RAG) could reduce HR workload while maintaining answer accuracy.

## POC Scope

The project was intentionally a proof of concept rather than a production system. In 2023, Advanced RAG techniques were not yet mature. Known limitations of the era included hallucination, unreliable retrieval accuracy, chunk-boundary issues, and the absence of reranking, metadata filtering, and query rewriting. The system did not enter production because the technology maturity at that time was insufficient for enterprise deployment — a statement about the ecosystem's maturity, not about model quality.

## Architecture

Basic RAG pipeline (left to right):

```
Employee Question → Chunking (with overlap) → Embedding → FAISS
  → Top-K Retrieval → Prompt (context injection) → ChatGPT → Answer
```

The implementation was deliberately a baseline RAG: chunking with overlap, embedding, FAISS vector index, Top-K retrieval, context injection into the prompt, and GPT generation. No Advanced RAG components (reranking, metadata filtering, query rewriting) were included.

## Outcome

The POC validated the approach and surfaced the limitations listed above. Those limitations motivated the second Manulife project, the HR Policy Writer, which took a generation-centric (non-RAG) approach and was deployed to production.
