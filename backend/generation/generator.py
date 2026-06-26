"""
generator.py — Final answer generation using retrieved context.

This is the "G" in RAG. By this point the pipeline has already done the hard
work: the 3 chunks passed in here are the most relevant passages from the
entire knowledge base, selected and re-ranked by the retrieval layer.

The generator's job is simple:
  1. Format the chunks into a readable context block
  2. Send [system prompt + context + user question] to the LLM
  3. Return the answer + the source files it came from

Prompt design choices:
  - We instruct the model to answer ONLY from the provided context.
    This prevents hallucination — if the answer isn't in the chunks,
    the model should say so rather than make something up.
  - We include source filenames so the model can cite them, and we
    also return them separately so the API response can surface them.
  - Temperature = 0 for factual, deterministic answers about a real person.
"""

from typing import List
from dataclasses import dataclass

from openai import OpenAI
from langchain_core.documents import Document

from backend.config import OPENAI_API_KEY, CHAT_MODEL

_client = OpenAI(api_key=OPENAI_API_KEY)

_SYSTEM_PROMPT = """You are Ziang (Jay) Zhang. Answer all questions in first person ("I", "my", "me")
as if you are Jay speaking directly, using ONLY the context passages provided below.

Rules:
- Always speak in first person — never say "Jay did X", say "I did X"
- Be specific and concrete — use names, numbers, and technical terms from the context
- If the context does not contain enough information to answer, say so in first person ("I don't have details on that")
- Do not invent details that are not in the context
- Keep answers concise: 3-6 sentences unless a longer answer is clearly needed"""


@dataclass
class GenerationResult:
    answer: str
    sources: List[str]      # list of source filenames
    context_used: List[str] # the actual chunk texts sent to LLM


def generate(query: str, chunks: List[Document]) -> GenerationResult:
    """
    Generate an answer from the query and the retrieved chunks.

    Args:
        query:  the original user question
        chunks: Top-K re-ranked documents from the retrieval pipeline
    """
    # ── Build context block ───────────────────────────────────────────────────
    context_parts = []
    sources = []

    for i, chunk in enumerate(chunks, start=1):
        source = chunk.metadata.get("source", "unknown")
        context_parts.append(f"[{i}] (source: {source})\n{chunk.page_content}")
        if source not in sources:
            sources.append(source)

    context_block = "\n\n---\n\n".join(context_parts)

    # ── Call LLM ──────────────────────────────────────────────────────────────
    user_message = f"""Context:
{context_block}

---

Question: {query}"""

    response = _client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0,
        max_tokens=512,
    )

    answer = response.choices[0].message.content.strip()

    return GenerationResult(
        answer=answer,
        sources=sources,
        context_used=[chunk.page_content for chunk in chunks],
    )
