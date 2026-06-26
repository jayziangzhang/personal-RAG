# Manulife — GenAI Practicum (RAG HR Assistant & HR Policy Writer)

## Overview — Two Distinct Projects
During my GenAI practicum at Manulife (2024), I delivered two related but distinct projects, which I always present separately: (1) a **RAG HR Assistant** — a proof-of-concept validating retrieval-augmented Q&A over internal HR policies; and (2) an **HR Policy Writer** — a production application that helped HR teams draft, rewrite, and standardize policy documents with a multi-stage GenAI workflow. The Policy Writer was the more substantial deliverable and the one I lead-developed.

## RAG HR Assistant (PoC) — Context
Manulife's HR team received a high volume of repetitive employee inquiries—"How many vacation days do I have?", "What's next year's holiday policy?", "What benefits am I eligible for?", "What's the parental-leave policy?" Most answers already existed in HR policy documents, yet employees still emailed or filed tickets, increasing HR workload, slowing response times, and consuming a lot of time on repetitive questions. The team wanted to explore whether Generative AI and RAG could power an internal HR Assistant.

## RAG HR Assistant — Architecture & Retrieval Flow
This was a proof-of-concept. The pipeline:

```
HR Policy Documents → Document Processing → Chunking → Embedding
→ FAISS Vector Store → Top-K Retrieval → LLM → Grounded Answer
```

The knowledge base drew from vacation, holiday, and benefits policies, the employee handbook, and internal HR guidelines, mostly in PDF and Word format. Long documents were chunked into ~500–1000-token segments to preserve semantic completeness; each chunk was embedded and stored in FAISS (Facebook AI Similarity Search). At query time (e.g., "How many vacation days does a Level 4 employee receive?"), the system performed vector retrieval, selected the top-K (e.g., top-3) chunks, and passed them to the LLM to generate an answer.

## RAG HR Assistant — Reducing Hallucination & Outcome
The key principle was that the LLM could not answer from its own knowledge—it had to answer strictly from retrieved context. The prompt explicitly instructed it to "answer only based on the provided context," and to respond "I don't have enough information" rather than fabricate when no relevant content was found. The PoC successfully demonstrated that for typical HR-policy queries—vacation entitlement, holiday policy, and similar—the system retrieved the right policy content and produced accurate, grounded answers, proving RAG was viable for enterprise internal-knowledge lookup.

## HR Policy Writer (Production) — Context & Goal
The HR team faced two burdens. First, they frequently published new policies, company notices, benefits updates, and employee communications, each of which had to follow corporate writing standards, brand language, and fixed formatting—slow and labor-intensive. Second, a large backlog of historical policies (e.g., Diversity & Inclusion, Employee Benefits, Workplace Conduct) needed updating and rewriting. The goal was to use GenAI to help HR draft, rewrite, improve, and standardize policy documents.

## HR Policy Writer — Workflow
```
HR Input → Prompt Templates → LLM Generation → HTML Output
→ LLM Validation → Quality Scoring → Pass / Regenerate → Final Policy
```

**Enforcing writing standards:** the core method was prompt engineering—instructing the model to use Manulife's HR writing style, employee-friendly language, a professional tone, and company formatting standards. **HTML generation:** because the downstream system publishes HTML directly, the tool offered two output modes—plain text, and an HTML mode that emitted ready-to-publish markup (`<h1>`, `<h2>`, `<table>`, `<ul>`, etc.) so HR could paste straight into internal systems with no re-formatting.

## HR Policy Writer — Agentic Validation & Quality Scoring
The most "agentic" part of the system was a second-pass review. After generation, a second LLM checked the output for: format (valid HTML), structure (correct policy structure), style (compliance with corporate standards), and source fidelity (faithful to the original policy content). If a check failed, the system regenerated. A separate LLM-as-judge then scored the draft on accuracy, structure, style, and employee-friendliness; drafts below a threshold were retried. This multi-stage validation—rather than trusting a single LLM response—was what made the output reliable enough for production.

## HR Policy Writer — Tech Stack
React frontend; FastAPI backend; an AI layer combining LLM APIs, prompt engineering, and the multi-stage validation pipeline; deployed with Docker in a decoupled frontend/backend setup that supported ongoing iteration. HTML export worked by having the LLM emit HTML directly, rendered in the frontend via a rich-text preview (e.g., `dangerouslySetInnerHTML`); HR could copy the HTML source into the internal HR platform and retain all formatting.

## Team & My Contribution
It was a four-person team, and I was the primary developer—I implemented most of the application architecture, including the FastAPI backend, the prompt-engineering workflow, LLM integration, the validation pipeline, the HTML-generation workflow, deployment, and stakeholder demonstrations (roughly 90% of the development). For stakeholder demos I was presenting to HR, not engineers, so I focused on business outcomes rather than implementation: I showed how HR staff could generate compliant policy drafts in minutes instead of manually drafting and formatting documents, emphasizing time saved, ease of use, output quality, and consistency.

## Biggest Challenge & Key Takeaway
The biggest challenge wasn't generating content—it was ensuring consistency and quality: making sure every generated policy followed company writing standards and formatting requirements and stayed faithful to the source material. That's why we introduced a validation-and-scoring pipeline instead of relying on a single LLM response. My key takeaway was that building enterprise GenAI applications isn't just about calling an LLM API—the real work is designing the workflow around the model: retrieval, validation, quality control, and user adoption.
