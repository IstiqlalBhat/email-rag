"""
Graph RAG API routes.

Provides endpoints for:
- Building knowledge graphs
- Querying with graph-enhanced retrieval
- Getting graph visualization data
- Checking build status
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from loguru import logger

from services.graph_rag.service import (
    build_graph,
    query_graph,
    get_build_status,
    get_visualization,
    get_graph_service
)
from services.graph_rag.models import GraphQueryResult, GraphBuildStatus

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class GraphBuildRequest(BaseModel):
    """Request to build a knowledge graph."""
    upload_id: str
    max_emails: int = 0  # 0 = process ALL emails for complete understanding
    max_chunks: int = 0  # 0 = process ALL chunks


class GraphQueryRequest(BaseModel):
    """Request to query a knowledge graph."""
    upload_id: str
    query: str


class GraphVisualizationRequest(BaseModel):
    """Request for graph visualization data."""
    upload_id: str
    traversal_path: Optional[List[int]] = None


class TraversalStepResponse(BaseModel):
    """A single traversal step in the response."""
    step: int
    node_id: int
    content_preview: str
    concepts: List[str]


class GraphQueryResponse(BaseModel):
    """Response from a graph query."""
    answer: str
    traversal_path: List[int]
    traversal_steps: List[TraversalStepResponse]
    sources: List[Dict[str, Any]]
    mode_used: str = "graph"


class GraphBuildStatusResponse(BaseModel):
    """Response for graph build status."""
    upload_id: str
    status: str
    node_count: int
    edge_count: int
    progress: float
    error: Optional[str] = None


class GraphVisualizationResponse(BaseModel):
    """Response with graph visualization data."""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    traversal_path: List[int]


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/build", response_model=GraphBuildStatusResponse)
async def start_graph_build(request: GraphBuildRequest, background_tasks: BackgroundTasks):
    """
    Start building a knowledge graph for an upload.

    This is a long-running operation that runs in the background.
    Use GET /status/{upload_id} to check progress.
    """
    logger.info(f"Starting graph build for upload: {request.upload_id}")

    # Check current status
    status = get_build_status(request.upload_id)

    if status.status == "building":
        return GraphBuildStatusResponse(
            upload_id=status.upload_id,
            status="building",
            node_count=status.node_count,
            edge_count=status.edge_count,
            progress=status.progress,
            error=None
        )

    if status.status == "ready":
        return GraphBuildStatusResponse(
            upload_id=status.upload_id,
            status="ready",
            node_count=status.node_count,
            edge_count=status.edge_count,
            progress=1.0,
            error=None
        )

    # Start build in background with configurable limits
    background_tasks.add_task(
        build_graph,
        request.upload_id,
        None,  # progress_callback
        request.max_emails,
        request.max_chunks
    )

    return GraphBuildStatusResponse(
        upload_id=request.upload_id,
        status="building",
        node_count=0,
        edge_count=0,
        progress=0.0,
        error=None
    )


@router.get("/status/{upload_id}", response_model=GraphBuildStatusResponse)
async def get_graph_status(upload_id: str):
    """Get the build status for a knowledge graph."""
    status = get_build_status(upload_id)

    return GraphBuildStatusResponse(
        upload_id=status.upload_id,
        status=status.status,
        node_count=status.node_count,
        edge_count=status.edge_count,
        progress=status.progress,
        error=status.error
    )


@router.post("/query", response_model=GraphQueryResponse)
async def query_knowledge_graph(request: GraphQueryRequest):
    """
    Query the knowledge graph using graph-enhanced retrieval.

    Returns an answer along with the traversal path through the graph.
    """
    logger.info(f"Graph query for upload {request.upload_id}: {request.query[:100]}...")

    # Check if graph is built
    status = get_build_status(request.upload_id)
    if status.status != "ready":
        raise HTTPException(
            status_code=400,
            detail=f"Graph not ready. Current status: {status.status}. "
                   f"Please build the graph first using POST /build"
        )

    # Execute query
    result = query_graph(request.upload_id, request.query)

    # Convert traversal steps
    traversal_steps = [
        TraversalStepResponse(
            step=step.step,
            node_id=step.node_id,
            content_preview=step.content_preview,
            concepts=step.concepts
        )
        for step in result.traversal_steps
    ]

    return GraphQueryResponse(
        answer=result.answer,
        traversal_path=result.traversal_path,
        traversal_steps=traversal_steps,
        sources=result.sources,
        mode_used="graph"
    )


@router.post("/visualization", response_model=GraphVisualizationResponse)
async def get_graph_visualization(request: GraphVisualizationRequest):
    """
    Get visualization data for the knowledge graph.

    Optionally highlight a traversal path.
    """
    # Check if graph is built
    status = get_build_status(request.upload_id)
    if status.status != "ready":
        raise HTTPException(
            status_code=400,
            detail=f"Graph not ready. Current status: {status.status}"
        )

    viz_data = get_visualization(request.upload_id, request.traversal_path)

    return GraphVisualizationResponse(
        nodes=viz_data.get("nodes", []),
        edges=viz_data.get("edges", []),
        traversal_path=viz_data.get("traversal_path", [])
    )


@router.get("/stats/{upload_id}")
async def get_graph_stats(upload_id: str):
    """Get statistics about a knowledge graph."""
    status = get_build_status(upload_id)

    if status.status != "ready":
        return {
            "upload_id": upload_id,
            "status": status.status,
            "stats": None
        }

    service = get_graph_service(upload_id)

    if not service.knowledge_graph:
        return {
            "upload_id": upload_id,
            "status": "not_loaded",
            "stats": None
        }

    graph = service.knowledge_graph.graph

    # Calculate stats
    degrees = [d for _, d in graph.degree()]
    avg_degree = sum(degrees) / len(degrees) if degrees else 0

    # Get concept distribution
    all_concepts = []
    for node in graph.nodes:
        concepts = graph.nodes[node].get('concepts', [])
        all_concepts.extend(concepts)

    concept_counts = {}
    for concept in all_concepts:
        concept_counts[concept] = concept_counts.get(concept, 0) + 1

    top_concepts = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)[:20]

    return {
        "upload_id": upload_id,
        "status": "ready",
        "stats": {
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "average_degree": round(avg_degree, 2),
            "max_degree": max(degrees) if degrees else 0,
            "min_degree": min(degrees) if degrees else 0,
            "unique_concepts": len(concept_counts),
            "top_concepts": [{"concept": c, "count": n} for c, n in top_concepts]
        }
    }
