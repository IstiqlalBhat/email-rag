"""Test Graph RAG with ALL emails for complete understanding."""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.graph_rag.service import GraphRAGService, build_graph
from core.config import settings

def test_full_build():
    """Test building graph with ALL emails."""
    print("=" * 70)
    print("COMPLETE Graph RAG - Processing ALL Emails")
    print("=" * 70)

    # Find upload
    extracted_dir = settings.EXTRACTED_DIR
    json_files = [f for f in os.listdir(extracted_dir) if f.endswith('.json') and not f.endswith('_analysis.json')]

    if not json_files:
        print("No data found")
        return

    upload_id = json_files[0].replace('.json', '').replace('-manual', '')
    print(f"Upload: {upload_id}")
    print(f"Processing: ALL emails (no limit)")
    print()

    # Build graph with no limits
    print("Building complete knowledge graph...")
    print("(This will take a few minutes but will understand EVERYTHING)")
    print()
    start = time.time()

    def progress(p, msg):
        elapsed = time.time() - start
        print(f"  [{p*100:5.1f}%] {msg} ({elapsed:.0f}s)")

    success = build_graph(upload_id, progress_callback=progress, max_emails=0, max_chunks=0)

    build_time = time.time() - start
    print()
    print(f"Build time: {build_time:.1f} seconds ({build_time/60:.1f} minutes)")
    print(f"Build success: {success}")

    if not success:
        return

    # Test queries
    print()
    print("=" * 70)
    print("Testing Intelligent Email Queries")
    print("=" * 70)

    from services.graph_rag.service import get_graph_service
    service = get_graph_service(upload_id)

    queries = [
        "What are the main topics discussed in my emails?",
        "Who are the most important people I communicate with?",
        "What deadlines or important dates are mentioned?",
        "Summarize any academic or research discussions",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n--- Query {i}: {query} ---")
        start = time.time()
        result = service.query(query)
        query_time = time.time() - start
        print(f"Time: {query_time:.1f}s | Nodes: {len(result.traversal_path)}")
        print(f"Answer: {result.answer[:500]}...")

if __name__ == "__main__":
    test_full_build()
