"""
Chat routes for RAG and coaching modes.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict

router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message schema."""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Chat request schema."""
    messages: List[ChatMessage]
    mailbox_id: int
    mode: Optional[str] = "auto"


class Citation(BaseModel):
    """Citation schema."""
    message_id: str
    date: str
    folder: Optional[str] = None
    snippet: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response schema."""
    content: str
    citations: List[Citation] = []
    mode_used: str


@router.post("/ask", response_model=ChatResponse)
async def ask_inbox(request: ChatRequest):
    """
    Ask My Inbox mode - factual RAG over email content.
    Returns answers with citations.
    """
    return ChatResponse(
        content="Based on your emails...",
        citations=[
            Citation(
                message_id="msg_123",
                date="2024-01-01T10:00:00Z",
                folder="Sent Items"
            )
        ],
        mode_used="content"
    )


@router.post("/coach", response_model=ChatResponse)
async def coach_me(request: ChatRequest):
    """
    Coach Me mode - insights and coaching based on patterns.
    Pulls from insights artifacts first.
    """
    return ChatResponse(
        content="Based on your communication patterns...",
        citations=[],
        mode_used="insights"
    )


@router.post("/router", response_model=ChatResponse)
async def router_chat(request: ChatRequest):
    """
    Auto mode - intelligently route between content and insights.
    """
    return ChatResponse(
        content="Routing to appropriate mode...",
        citations=[],
        mode_used="auto"
    )
