FROM python:3.9-slim

WORKDIR /app

# Install system dependencies needed by some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer cache — only rebuilds when requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY backend/ ./backend/
COPY knowledge_base/ ./knowledge_base/

# OPENAI_API_KEY is needed at build time for ingestion (embedding the knowledge base)
ARG OPENAI_API_KEY
ENV OPENAI_API_KEY=$OPENAI_API_KEY

# Run ingestion at build time so the image ships with a ready index
# (ChromaDB + BM25 index baked in — no cold-start delay)
RUN python -m backend.ingestion.run

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
