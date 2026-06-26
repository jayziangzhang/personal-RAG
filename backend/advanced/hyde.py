"""
hyde.py — Hypothetical Document Embedding (HyDE).

Paper: "Precise Zero-Shot Dense Retrieval without Relevance Labels" (Gao et al. 2022)

Problem it solves:
  Embedding a short question and embedding a long answer live in very different
  regions of the vector space. When you embed "What did Jay do at Manulife?"
  and search ChromaDB, you're comparing a question-shaped vector against
  answer-shaped chunk vectors — the geometry is mismatched.

How HyDE fixes this:
  1. Ask an LLM to generate a *hypothetical* answer to the question.
     The answer will be wrong or incomplete — that's fine.
  2. Embed that hypothetical answer instead of (or in addition to) the question.
  3. The hypothetical answer is answer-shaped, so its vector lands much closer
     to real answer chunks in embedding space.

Example:
  Query:       "What did Jay do at Manulife?"
  Hypothetical: "At Manulife, Jay built a RAG-based HR assistant using LangChain
                 and GPT-4, which answered employee HR policy questions..."
  → The hypothetical uses the same vocabulary as the real chunks → better retrieval.

In our pipeline:
  We run HyDE *in addition to* the original rewritten query.
  The hybrid search receives both vectors and we take the union of results.
  This maximises recall without sacrificing the precision of the original query.
"""

from openai import OpenAI
from backend.config import OPENAI_API_KEY, CHAT_MODEL

_client = OpenAI(api_key=OPENAI_API_KEY)

_SYSTEM_PROMPT = """You are Ziang (Jay) Zhang. Given a question, write a short hypothetical
answer (3-5 sentences) in first person ("I", "my") as if you are answering directly.
The answer should sound like a passage from a personal professional bio or resume spoken
by Jay himself. It does not need to be factually accurate — focus on using relevant
technical and professional vocabulary that might appear in the real document.
Return ONLY the hypothetical passage, no preamble."""


def generate_hypothetical_document(query: str) -> str:
    """Generate a hypothetical answer passage to use as an additional retrieval probe."""
    response = _client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
        temperature=0.3,    # slight creativity to expand vocabulary coverage
        max_tokens=150,
    )
    hypothetical = response.choices[0].message.content.strip()
    print(f"[HyDE] Generated hypothetical document ({len(hypothetical)} chars)")
    return hypothetical
