"""
Query Engine for Graph RAG.

Performs intelligent graph traversal to answer queries by:
1. Finding relevant starting nodes via vector similarity
2. Traversing the graph using Dijkstra-like algorithm
3. Accumulating context until a complete answer is found
4. Generating final response using LLM
"""

import heapq
from typing import List, Tuple, Dict, Any, Optional
from langchain_core.prompts import PromptTemplate
from loguru import logger

from .knowledge_graph import KnowledgeGraph
from .models import AnswerCheck, TraversalStep, GraphQueryResult


class GraphQueryEngine:
    """
    Query engine that traverses knowledge graph to find relevant context.

    Uses a modified Dijkstra's algorithm weighted by:
    - Semantic similarity to query
    - Edge weights (similarity + shared concepts)
    - Visited concept coverage
    """

    def __init__(
        self,
        vector_store: Any,
        knowledge_graph: KnowledgeGraph,
        llm: Any,
        max_context_length: int = 4000,
        max_traversal_steps: int = 10
    ):
        """
        Initialize the query engine.

        Args:
            vector_store: Vector store for initial document retrieval
            knowledge_graph: The knowledge graph to traverse
            llm: Language model for answer generation
            max_context_length: Maximum context length to accumulate
            max_traversal_steps: Maximum number of graph nodes to visit
        """
        self.vector_store = vector_store
        self.knowledge_graph = knowledge_graph
        self.llm = llm
        self.max_context_length = max_context_length
        self.max_traversal_steps = max_traversal_steps
        self.answer_check_chain = self._create_answer_check_chain()

    def _create_answer_check_chain(self):
        """Create chain for checking if context provides complete answer."""
        answer_check_prompt = PromptTemplate(
            input_variables=["query", "context"],
            template="""Given the following query and context, determine if the context provides a complete answer.

Query: {query}

Context:
{context}

If the context provides enough information to fully answer the query, set is_complete to true and provide the answer.
If more context is needed, set is_complete to false and provide a partial answer if possible."""
        )
        return answer_check_prompt | self.llm.with_structured_output(AnswerCheck)

    def _check_answer(self, query: str, context: str) -> Tuple[bool, str]:
        """Check if current context provides a complete answer."""
        try:
            response = self.answer_check_chain.invoke({
                "query": query,
                "context": context[:self.max_context_length]
            })
            return response.is_complete, response.answer
        except Exception as e:
            logger.debug(f"Answer check error: {e}")
            return False, ""

    def _find_closest_node(self, doc_content: str) -> Optional[int]:
        """Find the graph node closest to the given document content."""
        # Search for the node that matches this content
        for node_id in self.knowledge_graph.graph.nodes:
            node_content = self.knowledge_graph.get_node_content(node_id)
            # Check if content matches (could be a substring match)
            if doc_content in node_content or node_content in doc_content:
                return node_id

        # Fallback: try vector similarity search within graph
        try:
            results = self.vector_store.similarity_search_with_score(doc_content, k=1)
            if results:
                result_content = results[0][0].page_content
                for node_id in self.knowledge_graph.graph.nodes:
                    if self.knowledge_graph.get_node_content(node_id) == result_content:
                        return node_id
        except Exception as e:
            logger.debug(f"Node matching fallback error: {e}")

        return None

    def _expand_context(
        self,
        query: str,
        relevant_docs: List[Any]
    ) -> Tuple[str, List[int], Dict[int, str], str, List[TraversalStep]]:
        """
        Expand context by traversing the knowledge graph.

        Returns:
            - expanded_context: Accumulated context from traversal
            - traversal_path: List of visited node IDs
            - filtered_content: Dict mapping node ID to content
            - final_answer: Answer found during traversal (or empty)
            - traversal_steps: Detailed traversal information
        """
        expanded_context = ""
        traversal_path: List[int] = []
        visited_concepts: set = set()
        filtered_content: Dict[int, str] = {}
        final_answer = ""
        traversal_steps: List[TraversalStep] = []

        # Priority queue: (priority, node_id)
        priority_queue: List[Tuple[float, int]] = []
        distances: Dict[int, float] = {}

        logger.info(f"Starting graph traversal for query: {query[:100]}...")

        # Initialize with relevant documents
        for doc in relevant_docs:
            closest_node = self._find_closest_node(doc.page_content)
            if closest_node is not None:
                # Lower priority = higher relevance (we use min-heap)
                priority = 1.0  # Start nodes get highest priority
                heapq.heappush(priority_queue, (priority, closest_node))
                distances[closest_node] = priority

        if not priority_queue:
            logger.warning("No starting nodes found for graph traversal")
            return "", [], {}, "", []

        step = 0
        while priority_queue and step < self.max_traversal_steps:
            current_priority, current_node = heapq.heappop(priority_queue)

            # Skip if we've found a better path to this node
            if current_priority > distances.get(current_node, float('inf')):
                continue

            if current_node in traversal_path:
                continue

            step += 1
            traversal_path.append(current_node)

            # Get node data
            node_content = self.knowledge_graph.get_node_content(current_node)
            node_concepts = self.knowledge_graph.get_node_concepts(current_node)

            # Store content
            filtered_content[current_node] = node_content

            # Add to context
            if expanded_context:
                expanded_context += "\n\n---\n\n" + node_content
            else:
                expanded_context = node_content

            # Record traversal step
            traversal_steps.append(TraversalStep(
                step=step,
                node_id=current_node,
                content_preview=node_content[:200] + "..." if len(node_content) > 200 else node_content,
                concepts=node_concepts[:5]
            ))

            logger.debug(f"Step {step}: Node {current_node}, Concepts: {node_concepts[:3]}")

            # Check if we have a complete answer
            if len(expanded_context) >= 500:  # Minimum context before checking
                is_complete, answer = self._check_answer(query, expanded_context)
                if is_complete:
                    final_answer = answer
                    logger.info(f"Complete answer found at step {step}")
                    break

            # Update visited concepts
            node_concepts_lemmatized = set(
                self.knowledge_graph._lemmatize_concept(c)
                for c in node_concepts
            )

            # Only expand if we have new concepts to explore
            if not node_concepts_lemmatized.issubset(visited_concepts):
                visited_concepts.update(node_concepts_lemmatized)

                # Add neighbors to priority queue
                for neighbor in self.knowledge_graph.get_neighbors(current_node):
                    if neighbor not in traversal_path:
                        edge_data = self.knowledge_graph.get_edge_data(current_node, neighbor)
                        edge_weight = edge_data.get('weight', 0.5)

                        # Distance = current distance + inverse edge weight
                        new_distance = current_priority + (1.0 / max(edge_weight, 0.001))

                        if new_distance < distances.get(neighbor, float('inf')):
                            distances[neighbor] = new_distance
                            heapq.heappush(priority_queue, (new_distance, neighbor))

            # Check context length limit
            if len(expanded_context) >= self.max_context_length:
                logger.info("Max context length reached")
                break

        return expanded_context, traversal_path, filtered_content, final_answer, traversal_steps

    def query(self, query: str, k: int = 5) -> GraphQueryResult:
        """
        Query the knowledge graph.

        Args:
            query: The user's query
            k: Number of initial documents to retrieve

        Returns:
            GraphQueryResult with answer and traversal information
        """
        logger.info(f"Processing graph query: {query}")

        # Step 1: Retrieve relevant documents
        relevant_docs = self._retrieve_relevant_documents(query, k)

        if not relevant_docs:
            return GraphQueryResult(
                answer="I couldn't find any relevant information to answer your query.",
                traversal_path=[],
                traversal_steps=[],
                filtered_content={},
                sources=[]
            )

        # Step 2: Expand context via graph traversal
        expanded_context, traversal_path, filtered_content, final_answer, traversal_steps = \
            self._expand_context(query, relevant_docs)

        # Step 3: Generate final answer if not found during traversal
        if not final_answer and expanded_context:
            final_answer = self._generate_answer(query, expanded_context)

        # Step 4: Extract sources
        sources = self._extract_sources(filtered_content)

        logger.info(f"Query complete. Visited {len(traversal_path)} nodes.")

        return GraphQueryResult(
            answer=final_answer or "Unable to generate an answer from the available context.",
            traversal_path=traversal_path,
            traversal_steps=traversal_steps,
            filtered_content=filtered_content,
            sources=sources
        )

    def _retrieve_relevant_documents(self, query: str, k: int = 5) -> List[Any]:
        """Retrieve relevant documents using vector similarity."""
        logger.debug(f"Retrieving top {k} documents for query")
        try:
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": k}
            )
            return retriever.invoke(query)
        except Exception as e:
            logger.error(f"Document retrieval error: {e}")
            return []

    def _generate_answer(self, query: str, context: str) -> str:
        """Generate final answer using LLM."""
        logger.debug("Generating final answer...")
        try:
            response_prompt = PromptTemplate(
                input_variables=["query", "context"],
                template="""Based on the following context, provide a comprehensive answer to the query.

Context:
{context}

Query: {query}

Provide a clear, well-structured answer based on the information in the context. If the context doesn't contain enough information, acknowledge what's missing."""
            )
            response_chain = response_prompt | self.llm
            response = response_chain.invoke({
                "query": query,
                "context": context[:self.max_context_length]
            })
            return response.content
        except Exception as e:
            logger.error(f"Answer generation error: {e}")
            return "Error generating response."

    def _extract_sources(self, filtered_content: Dict[int, str]) -> List[Dict[str, Any]]:
        """Extract source information from traversed nodes."""
        sources = []
        for node_id, content in filtered_content.items():
            # Extract metadata if available
            node_data = self.knowledge_graph.graph.nodes.get(node_id, {})
            metadata = node_data.get('metadata', {})

            sources.append({
                "node_id": node_id,
                "preview": content[:200] + "..." if len(content) > 200 else content,
                "concepts": node_data.get('concepts', [])[:5],
                "metadata": metadata
            })

        return sources
