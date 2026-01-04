"""
Analytics routes for visualization data.
Provides endpoints for timeline, word cloud, and network graph data.
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from services.analytics.analytics_service import analytics_service

router = APIRouter()


class TimelineResponse(BaseModel):
    """Timeline data response."""
    dates: List[str]
    counts: List[int]
    total: Optional[int] = 0
    error: Optional[str] = None


class WordItem(BaseModel):
    """Single word with count."""
    text: str
    value: int


class WordCloudResponse(BaseModel):
    """Word cloud data response."""
    words: List[WordItem]
    total_unique: Optional[int] = 0
    error: Optional[str] = None


class NetworkNode(BaseModel):
    """Network graph node."""
    id: int
    name: str


class NetworkEdge(BaseModel):
    """Network graph edge."""
    source: int
    target: int
    weight: int


class NetworkResponse(BaseModel):
    """Network graph data response."""
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]
    total_contacts: Optional[int] = 0
    total_connections: Optional[int] = 0
    error: Optional[str] = None


@router.get("/timeline", response_model=TimelineResponse)
async def get_timeline(upload_id: str = Query(..., description="Upload ID to analyze")):
    """
    Get email activity timeline data.
    Returns daily email counts for visualization.
    """
    data = await analytics_service.get_timeline_data(upload_id)
    return TimelineResponse(**data)


@router.get("/wordcloud", response_model=WordCloudResponse)
async def get_wordcloud(
    upload_id: str = Query(..., description="Upload ID to analyze"),
    top_n: int = Query(100, description="Number of top words to return")
):
    """
    Get word cloud data.
    Returns top N frequent words with their counts.
    """
    data = await analytics_service.get_wordcloud_data(upload_id, top_n)
    return WordCloudResponse(**data)


@router.get("/network", response_model=NetworkResponse)
async def get_network(upload_id: str = Query(..., description="Upload ID to analyze")):
    """
    Get network graph data.
    Returns nodes (contacts) and edges (email connections) for relationship visualization.
    """
    data = await analytics_service.get_network_data(upload_id)
    return NetworkResponse(**data)
