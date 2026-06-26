"""
loader.py — Load raw documents from the knowledge base directory.

Each document is returned as a LangChain Document object with:
  - page_content: raw text
  - metadata: { source, file_type }
"""

from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader

from backend.config import KNOWLEDGE_BASE_DIR


def load_documents() -> List[Document]:
    """Load all .md and .pdf files from the knowledge base."""
    docs: List[Document] = []

    for path in sorted(KNOWLEDGE_BASE_DIR.iterdir()):
        if path.suffix == ".md":
            docs.extend(_load_markdown(path))

    print(f"[Loader] Loaded {len(docs)} document(s) from {KNOWLEDGE_BASE_DIR}")
    return docs


def _load_markdown(path: Path) -> List[Document]:
    loader = TextLoader(str(path), encoding="utf-8")
    docs = loader.load()
    for doc in docs:
        doc.metadata["source"] = path.name
        doc.metadata["file_type"] = "markdown"
    return docs
