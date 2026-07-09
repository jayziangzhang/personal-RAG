# Manulife — HR Policy Writer (Production)

## Overview

HR Policy Writer is a production system built at Manulife that automatically generates employee-facing HR policy announcements from source policy materials, using a Generator–Evaluator dual-model architecture with structured HTML output for direct use in Workday. It is a distinct product from the earlier HR Policy RAG proof of concept (documented separately).

## Business Background

Whenever a new HR policy was released, HR specialists manually created an employee announcement through a repetitive multi-step process: (1) read the policy documents; (2) rewrite them into employee-friendly language; (3) apply the Manulife writing style — tone, headings, colors, highlights, tables, warning blocks; (4) prepare both English and French versions; (5) open Workday; (6) manually edit HTML or rich text, repeatedly applying bold, tables, colors, bullets, spacing, and hyperlinks. The manual process was highly time-consuming, which motivated building the HR Policy Writer.

## Architecture

Generation pipeline (left to right):

```
Policy Materials → Prompt → GPT-3.5 → Generated Article
  → Output Format (Plain Text | HTML) → Llama 3 Evaluation → Score
  → pass: Publish
  → fail: Regenerate with feedback (max 3 retries)
```

## HTML Output Rationale

HTML output exists because Workday accepts pasted HTML directly. Previously, HR spent about 20 minutes formatting each announcement in Workday's editor; with generated HTML, publishing reduces to copy and paste. The elimination of manual formatting is the system's core business value.

## Prompt Design

The system prompt encodes four categories of constraints:

1. Style — employee-friendly, professional, positive tone.
2. Structure — title, summary, sections, bullet lists, tables.
3. Formatting — HTML-only output, specific brand colors, bold, lists, hyperlinks.
4. Compliance — no hallucination, no invented policy, use only the provided source materials.

## Generator–Evaluator Separation

Content generation and quality evaluation are separated to avoid self-evaluation bias: the generator (GPT-3.5) creates, and an independent evaluator (Llama 3) reviews. Separating the two roles is a canonical pattern in agent design, since LLMs are poor judges of their own outputs, and an independent evaluator provides more objective quality assessment.

Llama 3 was chosen as the evaluator because evaluation does not require the strongest reasoning model; a lightweight open-source model was sufficient for scoring formatting, policy consistency, and writing quality.

## Evaluation Metrics

| Dimension | Meaning |
| --- | --- |
| Accuracy | Consistency with the source policy |
| Relevance | Coverage of the key points |
| Writing Style | Conformance to HR writing standards |
| Employee Friendly | Readability for employees |
| HTML Format | Validity of the generated HTML |
| Structure | Completeness of headings, lists, and tables |

The evaluator produces an overall score from 0 to 10.

## Reflection Loop

The generate–evaluate cycle forms a reflection loop, an early instance of the pattern now standard in agent frameworks:

```
Generate → Evaluate → pass: Finish | fail: Feedback → Regenerate (max 3 retries)
```

The retry cap of 3 balances output quality against inference cost and response latency; repeated failure beyond three attempts indicates the prompt needs optimization rather than further regeneration.

## Not a RAG System

HR Policy Writer is a generation system, not a retrieval system. The policy documents are supplied directly as input; there is no knowledge base, no embedding, and no vector search. The correct characterization is Prompt Engineering + Structured Generation + LLM Evaluation.

## Deployment

The system was deployed with Streamlit + FastAPI + Docker on Azure and delivered to the client for real production use, beyond the practicum demonstration stage. A human-in-the-loop step remains: HR reviews each generated announcement before publishing, satisfying enterprise accuracy and compliance requirements.

## Key Design Highlights

- Generator–Evaluator dual-model architecture instead of single-model one-shot generation.
- Prompt engineering that enforces corporate writing style, HTML formatting, and compliance constraints through a system prompt.
- Structured output: Workday-ready HTML that eliminates manual formatting.
- Reflection loop: automatic regeneration driven by evaluation feedback, capped at 3 retries, improving output stability.
- Human-in-the-loop: final HR review before publication.
- Production deployment on Streamlit + FastAPI + Docker + Azure, delivered to the client for actual use.
