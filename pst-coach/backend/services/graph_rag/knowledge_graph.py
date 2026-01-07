"""
Knowledge Graph builder - Optimized for LARGE datasets.

Features:
- GPU-accelerated embeddings
- Top-K neighbors for scalable edge construction
- Local NER for concepts (no LLM calls)
- Efficient for 10K+ chunks
"""

import networkx as nx
import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.metrics.pairwise import cosine_similarity
from langchain_core.documents import Document
from loguru import logger

try:
    import spacy
    from spacy.cli import download as spacy_download
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not available")

try:
    from nltk.stem import WordNetLemmatizer
    import nltk
    nltk.download('wordnet', quiet=True)
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False


class KnowledgeGraph:
    """
    Scalable knowledge graph for large email datasets.

    Optimizations:
    - Top-K neighbors instead of threshold (O(n*k) instead of O(n²))
    - Batched similarity computation
    - NER-only concepts (no LLM)
    """

    def __init__(
        self,
        edges_threshold: float = 0.8,
        alpha: float = 0.7,
        beta: float = 0.3,
        use_llm_concepts: bool = False,
        top_k_neighbors: int = 10  # Connect each node to top-k similar nodes
    ):
        self.graph = nx.Graph()
        self.concept_cache: Dict[str, List[str]] = {}
        self.edges_threshold = edges_threshold
        self.alpha = alpha
        self.beta = beta
        self.use_llm_concepts = use_llm_concepts
        self.top_k_neighbors = top_k_neighbors

        self.lemmatizer = WordNetLemmatizer() if NLTK_AVAILABLE else None
        self.nlp = self._load_spacy_model() if SPACY_AVAILABLE else None

    def _load_spacy_model(self) -> Optional[Any]:
        """Load spaCy model."""
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
                logger.error(f"Failed to load spaCy: {e}")
                return None

    def build_graph(
        self,
        splits: List[Document],
        llm: Any,
        embedding_model: Any,
        max_workers: int = 1,
        progress_callback: Optional[callable] = None
    ) -> None:
        """Build knowledge graph - optimized for large datasets."""
        num_chunks = len(splits)
        logger.info(f"Building graph from {num_chunks} chunks (top-{self.top_k_neighbors} neighbors)")

        # Step 1: Add nodes
        self._add_nodes(splits)
        if progress_callback:
            progress_callback(0.1, f"Added {num_chunks} nodes")

        # Step 2: Create embeddings (GPU accelerated)
        embeddings = self._create_embeddings(splits, embedding_model)
        if progress_callback:
            progress_callback(0.4, "Created embeddings")

        # Step 3: Extract concepts using NER
        self._extract_concepts_ner(splits, progress_callback)
        if progress_callback:
            progress_callback(0.7, "Extracted concepts")

        # Step 4: Add edges using top-k neighbors (scalable)
        self._add_edges_topk(embeddings, progress_callback)
        if progress_callback:
            progress_callback(1.0, "Graph complete")

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
        """Create embeddings with batching for large datasets."""
        texts = [split.page_content for split in splits]
        total = len(texts)
        logger.info(f"Creating embeddings for {total} chunks...")

        # Process in batches for large datasets
        if total > 1000:
            batch_size = 500
            all_embeddings = []
            for i in range(0, total, batch_size):
                batch = texts[i:i + batch_size]
                logger.info(f"Embedding batch {i//batch_size + 1}/{(total + batch_size - 1)//batch_size}")
                batch_embeddings = embedding_model.embed_documents(batch)
                all_embeddings.extend(batch_embeddings)
            embeddings = np.array(all_embeddings)
        else:
            embeddings = np.array(embedding_model.embed_documents(texts))

        logger.info("Embeddings created")
        return embeddings

    def _extract_concepts_ner(self, splits: List[Document], progress_callback: Optional[callable] = None) -> None:
        """Extract concepts using NER only - fast and local."""
        logger.info("Extracting concepts with NER...")
        total = len(splits)

        for i, split in enumerate(splits):
            content = split.page_content

            if content in self.concept_cache:
                self.graph.nodes[i]['concepts'] = self.concept_cache[content]
                continue

            concepts = []

            if self.nlp:
                try:
                    # Process limited text for speed
                    doc = self.nlp(content[:3000])
                    entities = [
                        ent.text for ent in doc.ents
                        if ent.label_ in ["PERSON", "ORG", "GPE", "WORK_OF_ART", "EVENT", "DATE", "PRODUCT", "FAC"]
                    ]
                    concepts.extend(entities)
                except Exception:
                    pass

            unique_concepts = list(set(concepts))[:10]
            self.concept_cache[content] = unique_concepts
            self.graph.nodes[i]['concepts'] = unique_concepts

            if (i + 1) % 500 == 0:
                logger.info(f"NER progress: {i + 1}/{total}")
                if progress_callback:
                    prog = 0.4 + (0.3 * (i + 1) / total)
                    progress_callback(prog, f"NER: {i + 1}/{total}")

    def _add_edges_topk(self, embeddings: np.ndarray, progress_callback: Optional[callable] = None) -> None:
        """
        Add edges using TOP-K neighbors - SCALABLE for large datasets.

        Instead of computing full O(n²) similarity matrix,
        we compute similarities in batches and keep only top-k.
        """
        num_nodes = len(self.graph.nodes)
        k = min(self.top_k_neighbors, num_nodes - 1)
        logger.info(f"Computing top-{k} neighbors for {num_nodes} nodes...")

        edges_added = 0

        # Process in batches for memory efficiency
        batch_size = 500
        for batch_start in range(0, num_nodes, batch_size):
            batch_end = min(batch_start + batch_size, num_nodes)
            batch_embeddings = embeddings[batch_start:batch_end]

            # Compute similarity between batch and ALL nodes
            similarities = cosine_similarity(batch_embeddings, embeddings)

            for i, node1 in enumerate(range(batch_start, batch_end)):
                node1_sims = similarities[i]

                # Get top-k indices (excluding self)
                # Use argpartition for efficiency (O(n) instead of O(n log n))
                top_indices = np.argpartition(node1_sims, -k-1)[-k-1:]
                top_indices = top_indices[top_indices != node1][:k]

                node1_concepts = set(
                    self._lemmatize_concept(c)
                    for c in self.graph.nodes[node1].get('concepts', [])
                )

                for node2 in top_indices:
                    sim_score = node1_sims[node2]

                    # Only add edge if above threshold and not already exists
                    if sim_score > self.edges_threshold and not self.graph.has_edge(node1, node2):
                        node2_concepts = set(
                            self._lemmatize_concept(c)
                            for c in self.graph.nodes[node2].get('concepts', [])
                        )
                        shared = node1_concepts & node2_concepts

                        weight = self._calculate_edge_weight(node1, node2, sim_score, shared)
                        self.graph.add_edge(
                            node1, int(node2),
                            weight=weight,
                            similarity=float(sim_score),
                            shared_concepts=list(shared)
                        )
                        edges_added += 1

            if batch_end % 1000 == 0 or batch_end == num_nodes:
                logger.info(f"Edge progress: {batch_end}/{num_nodes} nodes, {edges_added} edges")
                if progress_callback:
                    prog = 0.7 + (0.3 * batch_end / num_nodes)
                    progress_callback(prog, f"Edges: {edges_added}")

        logger.info(f"Added {edges_added} edges (top-{k} neighbors)")

    def _calculate_edge_weight(
        self,
        node1: int,
        node2: int,
        similarity_score: float,
        shared_concepts: set
    ) -> float:
        """Calculate edge weight."""
        node1_concepts = self.graph.nodes[node1].get('concepts', [])
        node2_concepts = self.graph.nodes[node2].get('concepts', [])

        max_shared = min(len(node1_concepts), len(node2_concepts))
        normalized_shared = len(shared_concepts) / max_shared if max_shared > 0 else 0

        return self.alpha * similarity_score + self.beta * normalized_shared

    def _lemmatize_concept(self, concept: str) -> str:
        """Lemmatize a concept."""
        if self.lemmatizer:
            return ' '.join([
                self.lemmatizer.lemmatize(word.lower())
                for word in concept.split()
            ])
        return concept.lower()

    def get_node_content(self, node_id: int) -> str:
        return self.graph.nodes[node_id].get('content', '')

    def get_node_concepts(self, node_id: int) -> List[str]:
        return self.graph.nodes[node_id].get('concepts', [])

    def get_neighbors(self, node_id: int) -> List[int]:
        return list(self.graph.neighbors(node_id))

    def get_edge_data(self, node1: int, node2: int) -> Dict[str, Any]:
        return dict(self.graph[node1][node2])

    def to_visualization_data(self, traversal_path: Optional[List[int]] = None) -> Dict[str, Any]:
        """Convert graph to visualization format."""
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
