"""Check what sources look like."""
import sys
sys.path.insert(0, '.')

from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone
from core.config import settings

embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)

query_embedding = embeddings.embed_query("Dina Cartagena")
results = index.query(vector=query_embedding, top_k=3, include_metadata=True)

print("Sample sources that would be returned:")
for m in results.matches:
    meta = m.metadata
    print("---")
    print(f"date: {repr(meta.get('date', ''))}")
    print(f"from/sender: {repr(meta.get('sender', ''))}")
    print(f"to: {repr(meta.get('to', ''))}")
    print(f"subject: {repr(meta.get('subject', ''))}")
