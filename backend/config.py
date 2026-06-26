import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).parent.parent
KNOWLEDGE_BASE_DIR = ROOT_DIR / "knowledge_base"
CHROMA_PERSIST_DIR = ROOT_DIR / "chroma_db"
BM25_INDEX_PATH = ROOT_DIR / "bm25_index.pkl"

# ── OpenAI ─────────────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]  # must be set in .env
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"

# ── Chunking ───────────────────────────────────────────────────────────────────
CHUNK_SIZE = 500        # tokens (approximate via characters ÷ 4)
CHUNK_OVERLAP = 50

# ── Retrieval ──────────────────────────────────────────────────────────────────
TOP_K_RETRIEVAL = 10    # candidates from hybrid search
TOP_K_RERANK = 3        # final chunks passed to LLM

# ── ChromaDB ──────────────────────────────────────────────────────────────────
CHROMA_COLLECTION_NAME = "personal_rag"
