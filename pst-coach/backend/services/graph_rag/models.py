"""
Pydantic models for Graph RAG service.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class Concepts(BaseModel):
    """Extracted concepts from text."""
    concepts_list: List[str] = Field(default_factory=list, description="List of concepts")


class AnswerCheck(BaseModel):
    """Answer completeness check result."""
    is_complete: bool = Field(description="Whether the current context provides a complete answer")
    answer: str = Field(default="", description="The current answer based on the context")


class GraphNode(BaseModel):
    """Represents a node in the knowledge graph."""
    id: int
    content: str
    concepts: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    """Represents an edge in the knowledge graph."""
    source: int
    target: int
    weight: float
    similarity: float
    shared_concepts: List[str] = Field(default_factory=list)


class TraversalStep(BaseModel):
    """A single step in graph traversal."""
    step: int
    node_id: int
    content_preview: str
    concepts: List[str]


class GraphQueryResult(BaseModel):
    """Result of a graph RAG query."""
    answer: str
    traversal_path: List[int]
    traversal_steps: List[TraversalStep]
    filtered_content: Dict[int, str]
    sources: List[Dict[str, Any]] = Field(default_factory=list)


class GraphVisualizationData(BaseModel):
    """Data for visualizing the knowledge graph."""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    traversal_path: List[int] = Field(default_factory=list)


class GraphBuildStatus(BaseModel):
    """Status of graph building process."""
    upload_id: str
    status: str  # "pending", "building", "ready", "error"
    node_count: int = 0
    edge_count: int = 0
    progress: float = 0.0
    error: Optional[str] = None
