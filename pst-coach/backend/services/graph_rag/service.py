"""
Graph RAG Service - Main orchestration module.

Provides the main interface for:
- Building knowledge graphs from uploaded documents
- Querying using graph-enhanced retrieval
- Managing graph state per upload
"""

import os
import json
import pickle
from typing import Dict, Optional, Any, List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from loguru import logger

from core.config import settings
from .knowledge_graph import KnowledgeGraph
from .query_engine import GraphQueryEngine
from .models import GraphQueryResult, GraphBuildStatus, GraphVisualizationData


# Global cache for built graphs
_graph_cache: Dict[str, "GraphRAGService"] = {}
_build_status: Dict[str, GraphBuildStatus] = {}


class GraphRAGService:
    """
    Main service for Graph RAG operations.

    Handles:
    - Loading documents from extracted emails
    - Building knowledge graphs
    - Processing queries with graph traversal
    - Persisting and loading graph state
    """

    def __init__(self, upload_id: str):
        """
        Initialize GraphRAG service for a specific upload.

        Args:
            upload_id: The upload ID to process
        """
        self.upload_id = upload_id
        self.llm = self._init_llm()
        self.embedding_model = self._init_embeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        self.knowledge_graph: Optional[KnowledgeGraph] = None
        self.vector_store: Optional[FAISS] = None
        self.query_engine: Optional[GraphQueryEngine] = None
        self.splits: List[Document] = []

    def _init_llm(self) -> ChatAnthropic:
        """Initialize the LLM."""
        return ChatAnthropic(
            model=settings.LLM_MODEL,
            anthropic_api_key=settings.ANTHROPIC_API_KEY,
            temperature=0,
            max_tokens=4000
        )

    def _init_embeddings(self) -> HuggingFaceEmbeddings:
        """Initialize the embedding model."""
        return HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL
        )

    def _load_documents(self) -> List[Document]:
        """Load documents from extracted emails."""
        input_file = os.path.join(settings.EXTRACTED_DIR, f"{self.upload_id}.json")

        if not os.path.exists(input_file):
            logger.error(f"Extracted file not found: {input_file}")
            return []

        try:
            with open(input_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict):
                data = [data]

            documents = []
            for email in data:
                content = f"""Date: {email.get('date', 'Unknown')}
From: {email.get('from', 'Unknown')}
To: {email.get('to', 'Unknown')}
Subject: {email.get('subject', 'No Subject')}

{email.get('body', '')}"""

                doc = Document(
                    page_content=content,
                    metadata={
                        "email_id": email.get('email_id', ''),
                        "date": email.get('date', ''),
                        "sender": email.get('from', ''),
                        "recipient": email.get('to', ''),
                        "subject": email.get('subject', '')
                    }
                )
                documents.append(doc)

            logger.info(f"Loaded {len(documents)} documents for upload {self.upload_id}")
            return documents

        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            return []

    def _get_graph_path(self) -> str:
        """Get path for persisted graph."""
        graph_dir = os.path.join(settings.DATA_DIR, "graphs")
        os.makedirs(graph_dir, exist_ok=True)
        return os.path.join(graph_dir, f"{self.upload_id}_graph.pkl")

    def _get_vector_store_path(self) -> str:
        """Get path for persisted vector store."""
        graph_dir = os.path.join(settings.DATA_DIR, "graphs")
        os.makedirs(graph_dir, exist_ok=True)
        return os.path.join(graph_dir, f"{self.upload_id}_vectors")

    def is_built(self) -> bool:
        """Check if graph has been built for this upload."""
        return os.path.exists(self._get_graph_path())

    def build(self, progress_callback: Optional[callable] = None) -> bool:
        """
        Build the knowledge graph from documents.

        Args:
            progress_callback: Optional callback(progress: float, message: str)

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Building graph for upload {self.upload_id}")

        # Update status
        _build_status[self.upload_id] = GraphBuildStatus(
            upload_id=self.upload_id,
            status="building",
            progress=0.0
        )

        try:
            # Step 1: Load documents
            documents = self._load_documents()
            if not documents:
                raise ValueError("No documents found")

            if progress_callback:
                progress_callback(0.1, "Documents loaded")
            _build_status[self.upload_id].progress = 0.1

            # Step 2: Split documents
            self.splits = self.text_splitter.split_documents(documents)
            logger.info(f"Created {len(self.splits)} chunks")

            if progress_callback:
                progress_callback(0.2, "Documents chunked")
            _build_status[self.upload_id].progress = 0.2

            # Step 3: Create vector store
            logger.info("Creating vector store...")
            self.vector_store = FAISS.from_documents(self.splits, self.embedding_model)

            if progress_callback:
                progress_callback(0.3, "Vector store created")
            _build_status[self.upload_id].progress = 0.3

            # Step 4: Build knowledge graph
            self.knowledge_graph = KnowledgeGraph(
                edges_threshold=0.7,
                alpha=0.7,
                beta=0.3
            )

            def kg_progress(prog, msg):
                total_progress = 0.3 + (prog * 0.6)  # Map 0-1 to 0.3-0.9
                if progress_callback:
                    progress_callback(total_progress, msg)
                _build_status[self.upload_id].progress = total_progress

            self.knowledge_graph.build_graph(
                self.splits,
                self.llm,
                self.embedding_model,
                max_workers=4,
                progress_callback=kg_progress
            )

            # Update status
            _build_status[self.upload_id].node_count = len(self.knowledge_graph.graph.nodes)
            _build_status[self.upload_id].edge_count = len(self.knowledge_graph.graph.edges)

            # Step 5: Initialize query engine
            self.query_engine = GraphQueryEngine(
                vector_store=self.vector_store,
                knowledge_graph=self.knowledge_graph,
                llm=self.llm,
                max_context_length=4000,
                max_traversal_steps=10
            )

            # Step 6: Persist graph
            self._persist()

            if progress_callback:
                progress_callback(1.0, "Build complete")

            _build_status[self.upload_id].status = "ready"
            _build_status[self.upload_id].progress = 1.0

            # Cache the service
            _graph_cache[self.upload_id] = self

            logger.info(f"Graph build complete: {len(self.knowledge_graph.graph.nodes)} nodes, "
                       f"{len(self.knowledge_graph.graph.edges)} edges")
            return True

        except Exception as e:
            logger.exception(f"Graph build failed: {e}")
            _build_status[self.upload_id].status = "error"
            _build_status[self.upload_id].error = str(e)
            return False

    def _persist(self) -> None:
        """Persist graph and vector store to disk."""
        try:
            # Save knowledge graph
            graph_data = {
                "graph": self.knowledge_graph.graph,
                "concept_cache": self.knowledge_graph.concept_cache,
                "edges_threshold": self.knowledge_graph.edges_threshold,
                "alpha": self.knowledge_graph.alpha,
                "beta": self.knowledge_graph.beta
            }
            with open(self._get_graph_path(), "wb") as f:
                pickle.dump(graph_data, f)

            # Save vector store
            self.vector_store.save_local(self._get_vector_store_path())

            logger.info(f"Graph persisted for {self.upload_id}")

        except Exception as e:
            logger.error(f"Failed to persist graph: {e}")

    def load(self) -> bool:
        """Load persisted graph from disk."""
        try:
            graph_path = self._get_graph_path()
            vector_path = self._get_vector_store_path()

            if not os.path.exists(graph_path):
                logger.warning(f"No persisted graph found for {self.upload_id}")
                return False

            # Load knowledge graph
            with open(graph_path, "rb") as f:
                graph_data = pickle.load(f)

            self.knowledge_graph = KnowledgeGraph(
                edges_threshold=graph_data.get("edges_threshold", 0.7),
                alpha=graph_data.get("alpha", 0.7),
                beta=graph_data.get("beta", 0.3)
            )
            self.knowledge_graph.graph = graph_data["graph"]
            self.knowledge_graph.concept_cache = graph_data.get("concept_cache", {})

            # Load vector store
            self.vector_store = FAISS.load_local(
                vector_path,
                self.embedding_model,
                allow_dangerous_deserialization=True
            )

            # Initialize query engine
            self.query_engine = GraphQueryEngine(
                vector_store=self.vector_store,
                knowledge_graph=self.knowledge_graph,
                llm=self.llm,
                max_context_length=4000,
                max_traversal_steps=10
            )

            logger.info(f"Loaded graph for {self.upload_id}: "
                       f"{len(self.knowledge_graph.graph.nodes)} nodes, "
                       f"{len(self.knowledge_graph.graph.edges)} edges")
            return True

        except Exception as e:
            logger.error(f"Failed to load graph: {e}")
            return False

    def query(self, query: str) -> GraphQueryResult:
        """
        Query the knowledge graph.

        Args:
            query: User's query string

        Returns:
            GraphQueryResult with answer and traversal info
        """
        if not self.query_engine:
            if not self.load():
                return GraphQueryResult(
                    answer="Graph has not been built yet. Please build the graph first.",
                    traversal_path=[],
                    traversal_steps=[],
                    filtered_content={},
                    sources=[]
                )

        return self.query_engine.query(query)

    def get_visualization_data(self, traversal_path: Optional[List[int]] = None) -> Dict[str, Any]:
        """Get graph data for visualization."""
        if not self.knowledge_graph:
            if not self.load():
                return {"nodes": [], "edges": [], "traversal_path": []}

        return self.knowledge_graph.to_visualization_data(traversal_path)


# ============================================================================
# Module-level functions for external use
# ============================================================================

def get_graph_service(upload_id: str) -> GraphRAGService:
    """Get or create a GraphRAG service for an upload."""
    if upload_id in _graph_cache:
        return _graph_cache[upload_id]

    service = GraphRAGService(upload_id)
    if service.is_built():
        service.load()
        _graph_cache[upload_id] = service

    return service


def build_graph(upload_id: str, progress_callback: Optional[callable] = None) -> bool:
    """Build a knowledge graph for an upload."""
    service = GraphRAGService(upload_id)
    success = service.build(progress_callback)
    if success:
        _graph_cache[upload_id] = service
    return success


def query_graph(upload_id: str, query: str) -> GraphQueryResult:
    """Query an upload's knowledge graph."""
    service = get_graph_service(upload_id)
    return service.query(query)


def get_build_status(upload_id: str) -> GraphBuildStatus:
    """Get the build status for an upload."""
    if upload_id in _build_status:
        return _build_status[upload_id]

    service = GraphRAGService(upload_id)
    if service.is_built():
        return GraphBuildStatus(
            upload_id=upload_id,
            status="ready",
            progress=1.0
        )

    return GraphBuildStatus(
        upload_id=upload_id,
        status="pending",
        progress=0.0
    )


def get_visualization(upload_id: str, traversal_path: Optional[List[int]] = None) -> Dict[str, Any]:
    """Get visualization data for an upload's graph."""
    service = get_graph_service(upload_id)
    return service.get_visualization_data(traversal_path)
