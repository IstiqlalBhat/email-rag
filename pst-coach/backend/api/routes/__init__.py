"""
API routes package.
Contains routes for:
- uploads: PST file upload and processing
- chat: RAG chat and coaching endpoints
- graph_rag: Knowledge graph enhanced retrieval
"""
from api.routes import uploads, chat, graph_rag

__all__ = ["uploads", "chat", "graph_rag"]
