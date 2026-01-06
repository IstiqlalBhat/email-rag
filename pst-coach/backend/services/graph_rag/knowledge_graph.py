"""
Knowledge Graph builder for Graph RAG.

Builds a knowledge graph from document chunks with:
- Node creation from document chunks
- Concept extraction using LLM and NER
- Edge creation based on semantic similarity and shared concepts
"""

import networkx as nx
import numpy as np
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from sklearn.metrics.pairwise import cosine_similarity
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from loguru import logger

try:
    import spacy
    from spacy.cli import download as spacy_download
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not available - using simplified concept extraction")

try:
    from nltk.stem import WordNetLemmatizer
    import nltk
    nltk.download('wordnet', quiet=True)
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logger.warning("NLTK not available - using simplified lemmatization")

from .models import Concepts


class KnowledgeGraph:
    """
    Builds and manages a knowledge graph from document chunks.

    The graph connects document chunks based on:
    - Semantic similarity (via embeddings)
    - Shared concepts (extracted via LLM + NER)
    """

    def __init__(self, edges_threshold: float = 0.7, alpha: float = 0.7, beta: float = 0.3):
        """
        Initialize the knowledge graph.

        Args:
            edges_threshold: Minimum similarity score to create an edge (default 0.7)
            alpha: Weight for semantic similarity in edge weight calculation
            beta: Weight for concept overlap in edge weight calculation
        """
        self.graph = nx.Graph()
        self.concept_cache: Dict[str, List[str]] = {}
        self.edges_threshold = edges_threshold
        self.alpha = alpha
        self.beta = beta

        # Initialize lemmatizer
        if NLTK_AVAILABLE:
            self.lemmatizer = WordNetLemmatizer()
        else:
            self.lemmatizer = None

        # Initialize spaCy NLP
        self.nlp = self._load_spacy_model() if SPACY_AVAILABLE else None

    def _load_spacy_model(self) -> Optional[Any]:
        """Load spaCy model for NER."""
        if not SPACY_AVAILABLE:
            return None
        try:
            return spacy.load("en_core_web_sm")
        except OSError:
            logger.info("Downloading spaCy model...")
            try:
                spacy_download("en_core_web_sm")
                return spacy.load("en_core_web_sm")
            except Exception as e:
                logger.error(f"Failed to download spaCy model: {e}")
                return None

    def build_graph(
        self,
        splits: List[Document],
        llm: Any,
        embedding_model: Any,
        max_workers: int = 4,
        progress_callback: Optional[callable] = None
    ) -> None:
        """
        Build the knowledge graph from document splits.

        Args:
            splits: List of document chunks
            llm: Language model for concept extraction
            embedding_model: Embedding model for similarity computation
            max_workers: Number of parallel workers for concept extraction
            progress_callback: Optional callback for progress updates
        """
        logger.info(f"Building knowledge graph from {len(splits)} chunks")

        # Step 1: Add nodes
        self._add_nodes(splits)
        if progress_callback:
            progress_callback(0.2, "Added nodes")

        # Step 2: Create embeddings
        embeddings = self._create_embeddings(splits, embedding_model)
        if progress_callback:
            progress_callback(0.4, "Created embeddings")

        # Step 3: Extract concepts
        self._extract_concepts(splits, llm, max_workers)
        if progress_callback:
            progress_callback(0.7, "Extracted concepts")

        # Step 4: Add edges
        self._add_edges(embeddings)
        if progress_callback:
            progress_callback(1.0, "Added edges")

        logger.info(f"Graph built: {len(self.graph.nodes)} nodes, {len(self.graph.edges)} edges")

    def _add_nodes(self, splits: List[Document]) -> None:
        """Add document chunks as nodes."""
        for i, split in enumerate(splits):
            metadata = split.metadata if hasattr(split, 'metadata') else {}
            self.graph.add_node(
                i,
                content=split.page_content,
                metadata=metadata,
                concepts=[]
            )

    def _create_embeddings(self, splits: List[Document], embedding_model: Any) -> np.ndarray:
        """Create embeddings for all document chunks."""
        texts = [split.page_content for split in splits]
        logger.info(f"Creating embeddings for {len(texts)} chunks...")
        embeddings = embedding_model.embed_documents(texts)
        return np.array(embeddings)

    def _extract_concepts_for_node(self, content: str, llm: Any) -> List[str]:
        """Extract concepts from a single node's content."""
        if content in self.concept_cache:
            return self.concept_cache[content]

        concepts = []

        # Extract named entities using spaCy
        if self.nlp:
            try:
                doc = self.nlp(content[:5000])  # Limit content length for NER
                named_entities = [
                    ent.text for ent in doc.ents
                    if ent.label_ in ["PERSON", "ORG", "GPE", "WORK_OF_ART", "EVENT", "DATE"]
                ]
                concepts.extend(named_entities)
            except Exception as e:
                logger.debug(f"NER extraction error: {e}")

        # Extract general concepts using LLM
        try:
            concept_extraction_prompt = PromptTemplate(
                input_variables=["text"],
                template="""Extract 3-5 key concepts from this text. Focus on main topics, themes, and important entities.

Text:
{text}

Return only the concepts as a list."""
            )
            concept_chain = concept_extraction_prompt | llm.with_structured_output(Concepts)
            result = concept_chain.invoke({"text": content[:2000]})
            if result and result.concepts_list:
                concepts.extend(result.concepts_list)
        except Exception as e:
            logger.debug(f"LLM concept extraction error: {e}")

        # Deduplicate and limit
        unique_concepts = list(set(concepts))[:10]
        self.concept_cache[content] = unique_concepts
        return unique_concepts

    def _extract_concepts(self, splits: List[Document], llm: Any, max_workers: int = 4) -> None:
        """Extract concepts for all nodes in parallel."""
        logger.info(f"Extracting concepts with {max_workers} workers...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_node = {
                executor.submit(self._extract_concepts_for_node, split.page_content, llm): i
                for i, split in enumerate(splits)
            }

            completed = 0
            for future in as_completed(future_to_node):
                node = future_to_node[future]
                try:
                    concepts = future.result(timeout=30)
                    self.graph.nodes[node]['concepts'] = concepts
                except Exception as e:
                    logger.debug(f"Concept extraction failed for node {node}: {e}")
                    self.graph.nodes[node]['concepts'] = []

                completed += 1
                if completed % 50 == 0:
                    logger.info(f"Extracted concepts for {completed}/{len(splits)} nodes")

    def _compute_similarity_matrix(self, embeddings: np.ndarray) -> np.ndarray:
        """Compute pairwise cosine similarity."""
        return cosine_similarity(embeddings)

    def _calculate_edge_weight(
        self,
        node1: int,
        node2: int,
        similarity_score: float,
        shared_concepts: set
    ) -> float:
        """Calculate edge weight combining similarity and concept overlap."""
        node1_concepts = self.graph.nodes[node1].get('concepts', [])
        node2_concepts = self.graph.nodes[node2].get('concepts', [])

        max_possible_shared = min(len(node1_concepts), len(node2_concepts))
        if max_possible_shared > 0:
            normalized_shared = len(shared_concepts) / max_possible_shared
        else:
            normalized_shared = 0

        return self.alpha * similarity_score + self.beta * normalized_shared

    def _add_edges(self, embeddings: np.ndarray) -> None:
        """Add edges based on similarity and shared concepts."""
        logger.info("Computing similarity matrix and adding edges...")
        similarity_matrix = self._compute_similarity_matrix(embeddings)
        num_nodes = len(self.graph.nodes)
        edges_added = 0

        for node1 in range(num_nodes):
            node1_concepts = set(
                self._lemmatize_concept(c)
                for c in self.graph.nodes[node1].get('concepts', [])
            )

            for node2 in range(node1 + 1, num_nodes):
                similarity_score = similarity_matrix[node1][node2]

                if similarity_score > self.edges_threshold:
                    node2_concepts = set(
                        self._lemmatize_concept(c)
                        for c in self.graph.nodes[node2].get('concepts', [])
                    )
                    shared_concepts = node1_concepts & node2_concepts

                    edge_weight = self._calculate_edge_weight(
                        node1, node2, similarity_score, shared_concepts
                    )

                    self.graph.add_edge(
                        node1, node2,
                        weight=edge_weight,
                        similarity=similarity_score,
                        shared_concepts=list(shared_concepts)
                    )
                    edges_added += 1

        logger.info(f"Added {edges_added} edges")

    def _lemmatize_concept(self, concept: str) -> str:
        """Lemmatize a concept for better matching."""
        if self.lemmatizer:
            return ' '.join([
                self.lemmatizer.lemmatize(word.lower())
                for word in concept.split()
            ])
        return concept.lower()

    def get_node_content(self, node_id: int) -> str:
        """Get content for a specific node."""
        return self.graph.nodes[node_id].get('content', '')

    def get_node_concepts(self, node_id: int) -> List[str]:
        """Get concepts for a specific node."""
        return self.graph.nodes[node_id].get('concepts', [])

    def get_neighbors(self, node_id: int) -> List[int]:
        """Get neighboring nodes."""
        return list(self.graph.neighbors(node_id))

    def get_edge_data(self, node1: int, node2: int) -> Dict[str, Any]:
        """Get edge data between two nodes."""
        return dict(self.graph[node1][node2])

    def to_visualization_data(self, traversal_path: Optional[List[int]] = None) -> Dict[str, Any]:
        """Convert graph to visualization-friendly format."""
        nodes = []
        for node_id in self.graph.nodes:
            node_data = self.graph.nodes[node_id]
            concepts = node_data.get('concepts', [])
            nodes.append({
                "id": node_id,
                "label": concepts[0] if concepts else f"Node {node_id}",
                "concepts": concepts,
                "in_traversal": traversal_path and node_id in traversal_path,
                "traversal_order": traversal_path.index(node_id) if traversal_path and node_id in traversal_path else -1
            })

        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "weight": data.get('weight', 0.5),
                "similarity": data.get('similarity', 0),
                "shared_concepts": data.get('shared_concepts', [])
            })

        return {
            "nodes": nodes,
            "edges": edges,
            "traversal_path": traversal_path or []
        }
