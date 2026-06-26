FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY knowledge_base/ ./knowledge_base/

EXPOSE 8000

# Run ingestion first, then start the server
CMD ["sh", "-c", "python -m backend.ingestion.run && uvicorn backend.main:app --host 0.0.0.0 --port 8000"]
