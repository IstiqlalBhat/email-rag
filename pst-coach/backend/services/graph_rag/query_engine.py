"""
Query Engine for Graph RAG - Optimized for speed.

Uses Dijkstra-like traversal but minimizes LLM calls:
- NO answer checking during traversal
- Single LLM call at the end to generate answer
"""

import heapq
from typing import List, Tuple, Dict, Any, Optional
from langchain_core.prompts import PromptTemplate
from loguru import logger

from .knowledge_graph import KnowledgeGraph
from .models import AnswerCheck, TraversalStep, GraphQueryResult


class GraphQueryEngine:
    """
    Fast query engine with minimal LLM calls.

    Only makes LLM calls when generating the final answer.
    No answer checking during traversal = much faster.
    """

    def __init__(
        self,
        vector_store: Any,
        knowledge_graph: KnowledgeGraph,
        llm: Any,
        max_context_length: int = 4000,
        max_traversal_steps: int = 10
    ):
        self.vector_store = vector_store
        self.knowledge_graph = knowledge_graph
        self.llm = llm
        self.max_context_length = max_context_length
        self.max_traversal_steps = max_traversal_steps

    def _find_closest_node(self, doc_content: str) -> Optional[int]:
        """Find graph node matching document content."""
        for node_id in self.knowledge_graph.graph.nodes:
            node_content = self.knowledge_graph.get_node_content(node_id)
            if doc_content in node_content or node_content in doc_content:
                return node_id
        return None

    def _expand_context(self, query: str, relevant_docs: List[Any]) -> Tuple[str, List[int], Dict[int, str], List[TraversalStep]]:
        """
        Expand context via graph traversal - NO LLM CALLS.

        Returns:
            - expanded_context: Accumulated context
            - traversal_path: Node IDs visited
            - filtered_content: Node ID -> content mapping
            - traversal_steps: Detailed step info
        """
        expanded_context = ""
        traversal_path: List[int] = []
        visited_concepts: set = set()
        filtered_content: Dict[int, str] = {}
        traversal_steps: List[TraversalStep] = []

        # Priority queue: (priority, node_id)
        priority_queue: List[Tuple[float, int]] = []
        distances: Dict[int, float] = {}

        logger.debug(f"Starting traversal for: {query[:50]}...")

        # Initialize with relevant documents
        for doc in relevant_docs:
            closest_node = self._find_closest_node(doc.page_content)
            if closest_node is not None:
                priority = 1.0
                heapq.heappush(priority_queue, (priority, closest_node))
                distances[closest_node] = priority

        if not priority_queue:
            logger.warning("No starting nodes found")
            return "", [], {}, []

        step = 0
        while priority_queue and step < self.max_traversal_steps:
            current_priority, current_node = heapq.heappop(priority_queue)

            if current_priority > distances.get(current_node, float('inf')):
                continue

            if current_node in traversal_path:
                continue

            step += 1
            traversal_path.append(current_node)

            # Get node data
            node_content = self.knowledge_graph.get_node_content(current_node)
            node_concepts = self.knowledge_graph.get_node_concepts(current_node)

            filtered_content[current_node] = node_content

            # Build context
            if expanded_context:
                expanded_context += "\n\n---\n\n" + node_content
            else:
                expanded_context = node_content

            # Record step
            traversal_steps.append(TraversalStep(
                step=step,
                node_id=current_node,
                content_preview=node_content[:200] + "..." if len(node_content) > 200 else node_content,
                concepts=node_concepts[:5]
            ))

            logger.debug(f"Step {step}: Node {current_node}")

            # Check context length
            if len(expanded_context) >= self.max_context_length:
                logger.debug("Max context reached")
                break

            # Expand to neighbors
            node_concepts_set = set(
                self.knowledge_graph._lemmatize_concept(c)
                for c in node_concepts
            )

            if not node_concepts_set.issubset(visited_concepts):
                visited_concepts.update(node_concepts_set)

                for neighbor in self.knowledge_graph.get_neighbors(current_node):
                    if neighbor not in traversal_path:
                        edge_data = self.knowledge_graph.get_edge_data(current_node, neighbor)
                        edge_weight = edge_data.get('weight', 0.5)
                        new_distance = current_priority + (1.0 / max(edge_weight, 0.001))

                        if new_distance < distances.get(neighbor, float('inf')):
                            distances[neighbor] = new_distance
                            heapq.heappush(priority_queue, (new_distance, neighbor))

        return expanded_context, traversal_path, filtered_content, traversal_steps

    def query(self, query: str, k: int = 5) -> GraphQueryResult:
        """
        Query the knowledge graph.

        Makes only ONE LLM call at the end.
        """
        logger.info(f"Query: {query}")

        # Step 1: Retrieve relevant documents (no LLM)
        relevant_docs = self._retrieve_relevant_documents(query, k)

        if not relevant_docs:
            return GraphQueryResult(
                answer="No relevant information found.",
                traversal_path=[],
                traversal_steps=[],
                filtered_content={},
                sources=[]
            )

        # Step 2: Traverse graph (no LLM)
        expanded_context, traversal_path, filtered_content, traversal_steps = \
            self._expand_context(query, relevant_docs)

        # Step 3: Generate answer (ONLY LLM call)
        final_answer = self._generate_answer(query, expanded_context)

        # Step 4: Extract sources
        sources = self._extract_sources(filtered_content)

        logger.info(f"Query done. Visited {len(traversal_path)} nodes.")

        return GraphQueryResult(
            answer=final_answer,
            traversal_path=traversal_path,
            traversal_steps=traversal_steps,
            filtered_content=filtered_content,
            sources=sources
        )

    def _retrieve_relevant_documents(self, query: str, k: int = 5) -> List[Any]:
        """Retrieve documents via vector similarity (no LLM)."""
        try:
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": k}
            )
            return retriever.invoke(query)
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return []

    def _generate_answer(self, query: str, context: str) -> str:
        """Generate answer - THE ONLY LLM CALL."""
        if not context:
            return "No context available to answer the query."

        logger.debug("Generating answer...")
        try:
            response_prompt = PromptTemplate(
                input_variables=["query", "context"],
                template="""Based on the following context from emails, answer the query comprehensively.

Context:
{context}

Query: {query}

Provide a clear, well-structured answer based on the information in the context."""
            )
            response_chain = response_prompt | self.llm
            response = response_chain.invoke({
                "query": query,
                "context": context[:self.max_context_length]
            })

            # Handle different response formats
            if hasattr(response, 'content'):
                content = response.content
                # Handle Gemini's list format
                if isinstance(content, list):
                    return ''.join(
                        block.get('text', '') if isinstance(block, dict) else str(block)
                        for block in content
                    )
                return str(content)
            return str(response)
        except Exception as e:
            logger.error(f"Answer generation error: {e}")
            return f"Error generating response: {str(e)}"

    def _extract_sources(self, filtered_content: Dict[int, str]) -> List[Dict[str, Any]]:
        """Extract source info from traversed nodes."""
        sources = []
        for node_id, content in filtered_content.items():
            node_data = self.knowledge_graph.graph.nodes.get(node_id, {})
            metadata = node_data.get('metadata', {})

            sources.append({
                "node_id": node_id,
                "preview": content[:200] + "..." if len(content) > 200 else content,
                "concepts": node_data.get('concepts', [])[:5],
                "metadata": metadata
            })

        return sources
