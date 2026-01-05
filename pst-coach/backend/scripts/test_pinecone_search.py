"""
Test Pinecone Search for Dina Cartagena

This script verifies that the rebuilt index can find emails related to Dina Cartagena.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone

from core.config import settings


def test_search(query: str, k: int = 5):
    """Test searching for a query in Pinecone."""
    
    print(f"\n🔍 Searching for: {query}")
    print("-" * 50)
    
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
    
    # Connect to Pinecone
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    index = pc.Index(settings.PINECONE_INDEX_NAME)
    
    # Generate query embedding
    query_embedding = embeddings.embed_query(query)
    
    # Search
    results = index.query(
        vector=query_embedding,
        top_k=k,
        include_metadata=True
    )
    
    print(f"Found {len(results.matches)} results:\n")
    
    for i, match in enumerate(results.matches, 1):
        print(f"Result {i} (score: {match.score:.4f}):")
        meta = match.metadata
        print(f"  From: {meta.get('sender', 'N/A')}")
        print(f"  To: {meta.get('to', 'N/A')[:80]}")
        print(f"  Subject: {meta.get('subject', 'N/A')[:60]}")
        print(f"  Date: {meta.get('date', 'N/A')}")
        print(f"  Text preview: {meta.get('text', 'N/A')[:200]}...")
        print()


def main():
    print("=" * 60)
    print("PINECONE SEARCH TEST")
    print("=" * 60)
    
    # Get index stats
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    index = pc.Index(settings.PINECONE_INDEX_NAME)
    stats = index.describe_index_stats()
    
    print(f"\n📊 Index Stats:")
    print(f"   Total vectors: {stats.total_vector_count}")
    print(f"   Dimension: {stats.dimension}")
    
    # Test searches
    test_search("Dina Cartagena software engineer career fair")
    test_search("Hi Dina excited about the position")
    test_search("Clemson career fair job opportunity")
    test_search("emails from Dina")
    test_search("follow up after career fair")


if __name__ == "__main__":
    main()
