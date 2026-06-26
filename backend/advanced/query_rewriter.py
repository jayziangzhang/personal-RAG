"""
query_rewriter.py — Rewrite a user query to improve retrieval recall.

Problem it solves:
  Users ask questions in natural conversational language:
    "what did he do at that insurance company?"
  This is a terrible retrieval query — "insurance company" won't match
  "Manulife", and "he" gives no signal at all.

  The rewriter uses an LLM to expand and clarify the query into a form
  that is richer in retrieval-relevant keywords:
    "Manulife GenAI RAG project, HR assistant, HR Policy Writer,
     LangChain, retrieval-augmented generation, production GenAI"

How it works:
  We send the original query to GPT with a prompt that instructs it to
  produce a single, keyword-dense search query. We deliberately ask for
  ONE rewritten query (not multiple) to keep the pipeline simple and
  deterministic. The result replaces the original query in the retrieval step.

Trade-off:
  The rewriter adds one LLM call (latency ~0.5s). The payoff is significantly
  better recall, especially for vague or pronoun-heavy questions.
"""

from openai import OpenAI
from backend.config import OPENAI_API_KEY, CHAT_MODEL

_client = OpenAI(api_key=OPENAI_API_KEY)

_SYSTEM_PROMPT = """You are a search query optimizer for a personal knowledge base RAG system.
The knowledge base contains information about a person named Ziang (Jay) Zhang:
his education, work experience (Siemens, Manulife, IDP Plus startup), projects, and skills.

Given a user question, rewrite it into a single, keyword-dense search query
that will maximize retrieval recall from the knowledge base.

Rules:
- Return ONLY the rewritten query, no explanation, no punctuation at the end
- Expand abbreviations and resolve pronouns
- Include relevant technical terms, company names, project names
- Keep it under 30 words"""


def rewrite(query: str) -> str:
    """Return a rewritten, retrieval-optimised version of the input query."""
    response = _client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
        temperature=0,      # deterministic — same query always rewrites the same way
        max_tokens=80,
    )
    rewritten = response.choices[0].message.content.strip()
    print(f"[QueryRewriter] '{query}' → '{rewritten}'")
    return rewritten
