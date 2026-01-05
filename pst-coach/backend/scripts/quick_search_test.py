"""
Simplified Pinecone Search Test for Dina Cartagena
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone
from core.config import settings

# Initialize
embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)

# Get index stats
stats = index.describe_index_stats()
print(f"Index Stats: {stats.total_vector_count} vectors")

# Search for Dina Cartagena
query = "Dina Cartagena software engineer career fair"
query_embedding = embeddings.embed_query(query)

results = index.query(
    vector=query_embedding,
    top_k=5,
    include_metadata=True
)

print(f"\nSearch: '{query}'")
print(f"Found {len(results.matches)} results:\n")

for i, match in enumerate(results.matches, 1):
    meta = match.metadata
    print(f"--- Result {i} (score: {match.score:.4f}) ---")
    print(f"From: {meta.get('sender', 'N/A')[:80]}")
    print(f"To: {meta.get('to', 'N/A')[:80]}")
    print(f"Subject: {meta.get('subject', 'N/A')[:60]}")
    print(f"Date: {meta.get('date', 'N/A')}")
    text = meta.get('text', '')[:300]
    print(f"Text: {text}")
    print()
