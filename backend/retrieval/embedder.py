"""
embedder.py — Thin wrapper around OpenAI's embedding API.

Why a wrapper instead of calling OpenAI directly everywhere?
  - Single place to swap the model (config.py → EMBEDDING_MODEL).
  - Batching: OpenAI allows up to 2048 texts per request; we chunk the list
    to stay safe and avoid hitting token-count limits per batch.
  - Keeps the rest of the codebase model-agnostic.
"""

from typing import List
from openai import OpenAI

from backend.config import OPENAI_API_KEY, EMBEDDING_MODEL

_client = OpenAI(api_key=OPENAI_API_KEY)

_BATCH_SIZE = 100  # texts per API call


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Return a list of embedding vectors for a list of input strings."""
    all_vectors: List[List[float]] = []

    for i in range(0, len(texts), _BATCH_SIZE):
        batch = texts[i : i + _BATCH_SIZE]
        response = _client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch,
        )
        # Response items are ordered to match the input batch
        vectors = [item.embedding for item in response.data]
        all_vectors.extend(vectors)

    return all_vectors


def embed_query(text: str) -> List[float]:
    """Return a single embedding vector for a query string."""
    return embed_texts([text])[0]
