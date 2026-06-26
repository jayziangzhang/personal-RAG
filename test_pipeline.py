"""
Temporary end-to-end test script.
Run from project root: python test_pipeline.py
Delete after confirming the pipeline works.
"""

from backend.advanced.query_rewriter import rewrite
from backend.advanced.hyde import generate_hypothetical_document
from backend.retrieval import vector_store, hybrid
from backend.advanced.reranker import rerank
from backend.generation.generator import generate

QUERY = "What is your hobby?"

print("=" * 60)
print(f"Original query: {QUERY}")
print("=" * 60)

# Step 1: Query Rewriting
rewritten = rewrite(QUERY)

# Step 2: HyDE — generate hypothetical doc, use it as extra retrieval probe
hypothetical = generate_hypothetical_document(rewritten)

# Step 3: Hybrid Search on both rewritten query and hypothetical doc
print("\n[Pipeline] Running hybrid search on rewritten query...")
results_main = hybrid.search(rewritten, top_k=10)

print("[Pipeline] Running vector search on hypothetical document...")
results_hyde = vector_store.search(hypothetical, top_k=5)

# Merge: deduplicate by chunk_id, union of both result sets
seen = set()
candidates = []
for doc in results_main + results_hyde:
    cid = doc.metadata.get("chunk_id")
    if cid not in seen:
        seen.add(cid)
        candidates.append(doc)

print(f"[Pipeline] Total unique candidates: {len(candidates)}")

# Step 4: Re-rank with CrossEncoder (score against original query)
top_chunks = rerank(QUERY, candidates, top_k=3)

# Step 5: Generate answer
print("\n[Pipeline] Generating answer...")
result = generate(QUERY, top_chunks)

print("\n" + "=" * 60)
print("ANSWER")
print("=" * 60)
print(result.answer)
print(f"\nSources: {result.sources}")
