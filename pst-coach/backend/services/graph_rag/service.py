"""
Graph RAG Service - Fast GPU-accelerated implementation.

Optimized for speed:
- GPU-accelerated embeddings
- No LLM calls during graph building (NER only)
- Batched processing
- Configurable document limits
"""

import os
import json
import pickle
import time
import threading
from typing import Dict, Optional, Any, List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.runnables import RunnableSerializable
from langchain_core.runnables.config import RunnableConfig
from loguru import logger

from core.config import settings


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, max_rpm: int = 15, max_retries: int = 3, base_delay: float = 1.0):
        self.max_rpm = max_rpm
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.request_times: List[float] = []
        self._lock = threading.Lock()

    def wait_for_rate_limit(self):
        """Wait if rate limit reached."""
        with self._lock:
            now = time.time()
            self.request_times = [t for t in self.request_times if now - t < 60]
            if len(self.request_times) >= self.max_rpm:
                wait_time = 60 - (now - self.request_times[0]) + 0.1
                if wait_time > 0:
                    logger.debug(f"Rate limit, waiting {wait_time:.1f}s")
                    time.sleep(wait_time)
                    self.request_times = self.request_times[1:]
            self.request_times.append(time.time())

    def execute_with_retry(self, func, *args, **kwargs):
        """Execute with retry on rate limit errors."""
        for attempt in range(self.max_retries):
            try:
                self.wait_for_rate_limit()
                return func(*args, **kwargs)
            except Exception as e:
                if "rate" in str(e).lower() or "429" in str(e):
                    wait = self.base_delay * (2 ** attempt)
                    logger.warning(f"Rate limit error, waiting {wait}s")
                    time.sleep(wait)
                elif attempt == self.max_retries - 1:
                    raise
                else:
                    time.sleep(self.base_delay)
        raise Exception("Max retries exceeded")


class RateLimitedLLM(RunnableSerializable):
    """Rate-limited LLM wrapper."""

    llm: Any
    rate_limiter: Any

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, llm: Any, max_rpm: int = 15, **kwargs):
        super().__init__(
            llm=llm,
            rate_limiter=RateLimiter(max_rpm=max_rpm),
            **kwargs
        )

    @property
    def max_rpm(self):
        return self.rate_limiter.max_rpm

    def invoke(self, input: Any, config: Optional[RunnableConfig] = None, **kwargs) -> Any:
        return self.rate_limiter.execute_with_retry(self.llm.invoke, input, config=config, **kwargs)

    def with_structured_output(self, schema, **kwargs):
        structured = self.llm.with_structured_output(schema, **kwargs)
        return RateLimitedStructuredLLM(structured=structured, rate_limiter=self.rate_limiter)


class RateLimitedStructuredLLM(RunnableSerializable):
    """Rate-limited structured output LLM."""

    structured: Any
    rate_limiter: Any

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, structured: Any, rate_limiter: RateLimiter, **kwargs):
        super().__init__(structured=structured, rate_limiter=rate_limiter, **kwargs)

    def invoke(self, input: Any, config: Optional[RunnableConfig] = None, **kwargs) -> Any:
        return self.rate_limiter.execute_with_retry(self.structured.invoke, input, config=config, **kwargs)


from .knowledge_graph import KnowledgeGraph
from .query_engine import GraphQueryEngine
from .models import GraphQueryResult, GraphBuildStatus, GraphVisualizationData


# Global cache
_graph_cache: Dict[str, "GraphRAGService"] = {}
_build_status: Dict[str, GraphBuildStatus] = {}

# Configuration - Process ALL emails by default for complete understanding
MAX_EMAILS_DEFAULT = 0  # 0 = no limit, process all emails
MAX_CHUNKS_DEFAULT = 0  # 0 = no limit, process all chunks


class GraphRAGService:
    """
    Fast Graph RAG service with GPU acceleration.

    Key optimizations:
    - Limits document count for reasonable processing time
    - GPU-accelerated embeddings when available
    - No LLM calls during graph building (NER only)
    - Batched operations
    """

    @staticmethod
    def normalize_upload_id(upload_id: str) -> str:
        """Normalize upload_id by removing common suffixes like -manual."""
        # Remove -manual suffix if present
        if upload_id.endswith('-manual'):
            return upload_id[:-7]
        return upload_id

    def __init__(self, upload_id: str, max_emails: int = MAX_EMAILS_DEFAULT, max_chunks: int = MAX_CHUNKS_DEFAULT):
        # Normalize the upload_id for consistent graph file naming
        self.upload_id = self.normalize_upload_id(upload_id)
        self.original_upload_id = upload_id  # Keep original for document loading
        self.max_emails = max_emails
        self.max_chunks = max_chunks
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

    def _init_llm(self) -> Any:
        """Initialize LLM with rate limiting."""
        if settings.LLM_PROVIDER == "google":
            logger.info(f"Using Gemini: {settings.LLM_MODEL}")
            base_llm = ChatGoogleGenerativeAI(
                model=settings.LLM_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0,
                convert_system_message_to_human=True,
                max_output_tokens=4000,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
        else:
            logger.info(f"Using Anthropic: {settings.LLM_MODEL}")
            base_llm = ChatAnthropic(
                model=settings.LLM_MODEL,
                anthropic_api_key=settings.ANTHROPIC_API_KEY,
                temperature=0,
                max_tokens=4000
            )

        return RateLimitedLLM(base_llm, max_rpm=getattr(settings, 'LLM_MAX_RPM', 15))

    def _init_embeddings(self) -> HuggingFaceEmbeddings:
        """Initialize GPU-accelerated embeddings."""
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Embeddings device: {device}")

        model_kwargs = {'device': device, 'trust_remote_code': True}
        encode_kwargs = {
            'batch_size': 64 if device == "cuda" else 32,
            'normalize_embeddings': True
        }

        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )

    def _load_documents(self) -> List[Document]:
        """Load documents with configurable limit."""
        # Try multiple variations of upload_id for file matching
        possible_ids = [self.upload_id, self.original_upload_id, f"{self.upload_id}-manual"]
        input_file = None

        for uid in possible_ids:
            candidate = os.path.join(settings.EXTRACTED_DIR, f"{uid}.json")
            if os.path.exists(candidate):
                input_file = candidate
                logger.info(f"Found file: {candidate}")
                break

        # Fuzzy match if exact file not found
        if not input_file:
            for filename in os.listdir(settings.EXTRACTED_DIR):
                if filename.startswith(self.upload_id) and filename.endswith('.json') and not filename.endswith('_analysis.json'):
                    input_file = os.path.join(settings.EXTRACTED_DIR, filename)
                    logger.info(f"Matched file: {filename}")
                    break
            else:
                logger.error(f"No file found for {self.upload_id}")
                return []

        try:
            with open(input_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict):
                data = [data]

            # Limit emails if specified (0 = no limit)
            if self.max_emails > 0:
                data = data[:self.max_emails]
                logger.info(f"Processing {len(data)} emails (limited)")
            else:
                logger.info(f"Processing ALL {len(data)} emails")

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

            return documents

        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            return []

    def _get_graph_path(self) -> str:
        graph_dir = os.path.join(settings.DATA_DIR, "graphs")
        os.makedirs(graph_dir, exist_ok=True)
        return os.path.join(graph_dir, f"{self.upload_id}_graph.pkl")

    def _get_vector_store_path(self) -> str:
        graph_dir = os.path.join(settings.DATA_DIR, "graphs")
        os.makedirs(graph_dir, exist_ok=True)
        return os.path.join(graph_dir, f"{self.upload_id}_vectors")

    def is_built(self) -> bool:
        return os.path.exists(self._get_graph_path())

    def build(self, progress_callback: Optional[callable] = None) -> bool:
        """Build knowledge graph - FAST version with no LLM calls."""
        logger.info(f"Building graph for {self.upload_id} (original: {self.original_upload_id}, max {self.max_emails} emails, {self.max_chunks} chunks)")
        start_time = time.time()

        # Use normalized upload_id for status tracking
        _build_status[self.upload_id] = GraphBuildStatus(
            upload_id=self.original_upload_id,  # Return original ID to frontend
            status="building",
            progress=0.0
        )

        try:
            # Step 1: Load limited documents
            documents = self._load_documents()
            if not documents:
                raise ValueError("No documents found")

            if progress_callback:
                progress_callback(0.1, f"Loaded {len(documents)} emails")
            _build_status[self.upload_id].progress = 0.1

            # Step 2: Split documents
            self.splits = self.text_splitter.split_documents(documents)

            # Limit chunks if specified (0 = no limit)
            if self.max_chunks > 0 and len(self.splits) > self.max_chunks:
                logger.warning(f"Limiting chunks from {len(self.splits)} to {self.max_chunks}")
                self.splits = self.splits[:self.max_chunks]

            logger.info(f"Created {len(self.splits)} chunks for complete email understanding")

            if progress_callback:
                progress_callback(0.2, f"Created {len(self.splits)} chunks")
            _build_status[self.upload_id].progress = 0.2

            # Step 3: Create vector store (GPU accelerated)
            logger.info("Creating vector store...")
            self.vector_store = FAISS.from_documents(self.splits, self.embedding_model)

            if progress_callback:
                progress_callback(0.4, "Vector store created")
            _build_status[self.upload_id].progress = 0.4

            # Step 4: Build knowledge graph - NO LLM CALLS, top-k neighbors for speed
            self.knowledge_graph = KnowledgeGraph(
                edges_threshold=0.75,  # Slightly lower for better connectivity
                alpha=0.7,
                beta=0.3,
                use_llm_concepts=False,  # No LLM for concepts
                top_k_neighbors=15  # Each node connects to top 15 similar nodes
            )

            def kg_progress(prog, msg):
                total_progress = 0.4 + (prog * 0.5)
                if progress_callback:
                    progress_callback(total_progress, msg)
                _build_status[self.upload_id].progress = total_progress

            self.knowledge_graph.build_graph(
                self.splits,
                self.llm,
                self.embedding_model,
                max_workers=1,  # Sequential for stability
                progress_callback=kg_progress
            )

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

            # Step 6: Persist
            self._persist()

            if progress_callback:
                progress_callback(1.0, "Build complete")

            _build_status[self.upload_id].status = "ready"
            _build_status[self.upload_id].progress = 1.0

            _graph_cache[self.upload_id] = self

            elapsed = time.time() - start_time
            logger.info(f"Graph built in {elapsed:.1f}s: {len(self.knowledge_graph.graph.nodes)} nodes, "
                       f"{len(self.knowledge_graph.graph.edges)} edges")
            return True

        except Exception as e:
            logger.exception(f"Graph build failed: {e}")
            _build_status[self.upload_id].status = "error"
            _build_status[self.upload_id].error = str(e)
            return False

    def _persist(self) -> None:
        """Persist graph to disk."""
        try:
            graph_data = {
                "graph": self.knowledge_graph.graph,
                "concept_cache": self.knowledge_graph.concept_cache,
                "edges_threshold": self.knowledge_graph.edges_threshold,
                "alpha": self.knowledge_graph.alpha,
                "beta": self.knowledge_graph.beta
            }
            with open(self._get_graph_path(), "wb") as f:
                pickle.dump(graph_data, f)

            self.vector_store.save_local(self._get_vector_store_path())
            logger.info(f"Graph persisted for {self.upload_id}")

        except Exception as e:
            logger.error(f"Failed to persist graph: {e}")

    def load(self) -> bool:
        """Load persisted graph."""
        try:
            graph_path = self._get_graph_path()
            vector_path = self._get_vector_store_path()

            if not os.path.exists(graph_path):
                return False

            with open(graph_path, "rb") as f:
                graph_data = pickle.load(f)

            self.knowledge_graph = KnowledgeGraph(
                edges_threshold=graph_data.get("edges_threshold", 0.8),
                alpha=graph_data.get("alpha", 0.7),
                beta=graph_data.get("beta", 0.3)
            )
            self.knowledge_graph.graph = graph_data["graph"]
            self.knowledge_graph.concept_cache = graph_data.get("concept_cache", {})

            self.vector_store = FAISS.load_local(
                vector_path,
                self.embedding_model,
                allow_dangerous_deserialization=True
            )

            self.query_engine = GraphQueryEngine(
                vector_store=self.vector_store,
                knowledge_graph=self.knowledge_graph,
                llm=self.llm,
                max_context_length=4000,
                max_traversal_steps=10
            )

            logger.info(f"Loaded graph: {len(self.knowledge_graph.graph.nodes)} nodes, "
                       f"{len(self.knowledge_graph.graph.edges)} edges")
            return True

        except Exception as e:
            logger.error(f"Failed to load graph: {e}")
            return False

    def query(self, query: str) -> GraphQueryResult:
        """Query the knowledge graph."""
        if not self.query_engine:
            if not self.load():
                return GraphQueryResult(
                    answer="Graph not built. Please build the graph first.",
                    traversal_path=[],
                    traversal_steps=[],
                    filtered_content={},
                    sources=[]
                )

        return self.query_engine.query(query)

    def get_visualization_data(self, traversal_path: Optional[List[int]] = None) -> Dict[str, Any]:
        """Get graph visualization data."""
        if not self.knowledge_graph:
            if not self.load():
                return {"nodes": [], "edges": [], "traversal_path": []}

        return self.knowledge_graph.to_visualization_data(traversal_path)


# Module-level functions
def get_graph_service(upload_id: str) -> GraphRAGService:
    """Get or create GraphRAG service."""
    # Normalize upload_id for consistent cache lookup
    normalized_id = GraphRAGService.normalize_upload_id(upload_id)

    if normalized_id in _graph_cache:
        return _graph_cache[normalized_id]

    service = GraphRAGService(upload_id)
    if service.is_built():
        service.load()
        _graph_cache[normalized_id] = service

    return service


def build_graph(upload_id: str, progress_callback: Optional[callable] = None,
                max_emails: int = MAX_EMAILS_DEFAULT, max_chunks: int = MAX_CHUNKS_DEFAULT) -> bool:
    """Build knowledge graph with configurable limits."""
    service = GraphRAGService(upload_id, max_emails=max_emails, max_chunks=max_chunks)
    success = service.build(progress_callback)
    if success:
        # Cache with normalized id
        _graph_cache[service.upload_id] = service
    return success


def query_graph(upload_id: str, query: str) -> GraphQueryResult:
    """Query an upload's knowledge graph."""
    service = get_graph_service(upload_id)
    return service.query(query)


def get_build_status(upload_id: str) -> GraphBuildStatus:
    """Get build status with caching to avoid repeated graph loading."""
    # Normalize upload_id for consistent lookup
    normalized_id = GraphRAGService.normalize_upload_id(upload_id)

    # Return cached status if available
    if normalized_id in _build_status:
        return _build_status[normalized_id]

    service = GraphRAGService(upload_id)
    if service.is_built():
        # Check if already cached in _graph_cache
        if normalized_id in _graph_cache:
            cached = _graph_cache[normalized_id]
            node_count = len(cached.knowledge_graph.graph.nodes) if cached.knowledge_graph else 0
            edge_count = len(cached.knowledge_graph.graph.edges) if cached.knowledge_graph else 0
        else:
            # Load once and cache
            try:
                service.load()
                _graph_cache[normalized_id] = service
                node_count = len(service.knowledge_graph.graph.nodes) if service.knowledge_graph else 0
                edge_count = len(service.knowledge_graph.graph.edges) if service.knowledge_graph else 0
            except Exception as e:
                logger.error(f"Failed to load graph for status: {e}")
                node_count = 0
                edge_count = 0

        status = GraphBuildStatus(
            upload_id=upload_id,
            status="ready",
            progress=1.0,
            node_count=node_count,
            edge_count=edge_count
        )
        # Cache the status to avoid repeated loading
        _build_status[normalized_id] = status
        return status

    return GraphBuildStatus(upload_id=upload_id, status="pending", progress=0.0)


def get_visualization(upload_id: str, traversal_path: Optional[List[int]] = None) -> Dict[str, Any]:
    """Get visualization data."""
    service = get_graph_service(upload_id)
    return service.get_visualization_data(traversal_path)
