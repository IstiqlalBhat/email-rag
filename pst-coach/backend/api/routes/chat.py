"""
Chat routes for RAG and coaching modes.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from graph.chat_graph import chat_graph, content_rag, insights_rag, generate_response, ChatState
from loguru import logger

router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message schema."""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Chat request schema."""
    messages: List[ChatMessage]
    upload_id: str  # Required for context
    mode: Optional[str] = "auto"  # "auto", "content", "insights", "graph"


class Citation(BaseModel):
    """Citation schema."""
    date: str
    sender: str
    subject: str
    snippet: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response schema."""
    content: str
    citations: List[Citation] = []
    mode_used: str


@router.post("/router", response_model=ChatResponse)
async def router_chat(request: ChatRequest):
    """
    Unified chat endpoint that uses LangGraph to route and answer.
    Respects the 'mode' parameter: 'content' for Ask Inbox, 'insights' for Coach Me.
    """
    # Convert all messages to LangChain format, preserving conversation history
    lc_messages = []
    has_user_message = False
    for msg in request.messages:
        if msg.role == "user":
            lc_messages.append(HumanMessage(content=msg.content))
            has_user_message = True
        else:
            lc_messages.append(AIMessage(content=msg.content))
    
    if not has_user_message:
        return ChatResponse(content="No user message found.", mode_used="error")

    logger.info(f"Chat request - mode: {request.mode}, upload_id: {request.upload_id}")

    # Handle graph mode separately (uses different service)
    if request.mode == "graph":
        from services.graph_rag.service import query_graph, get_build_status

        # Check if graph is built
        status = get_build_status(request.upload_id)
        if status.status != "ready":
            return ChatResponse(
                content=f"Knowledge graph not ready (status: {status.status}). "
                        f"Please build the graph first via the Explore tab.",
                citations=[],
                mode_used="graph"
            )

        # Get the latest user message
        user_query = lc_messages[-1].content if lc_messages else ""

        # Query the graph
        result = query_graph(request.upload_id, user_query)

        # Convert sources to citations
        citations = []
        for source in result.sources[:5]:  # Limit citations
            metadata = source.get("metadata", {})
            citations.append(Citation(
                date=str(metadata.get("date", "")),
                sender=str(metadata.get("sender", "")),
                subject=str(metadata.get("subject", "")),
                snippet=source.get("preview", "")[:200]
            ))

        return ChatResponse(
            content=result.answer,
            citations=citations,
            mode_used="graph"
        )

    # If mode is explicitly set, bypass the classifier
    if request.mode in ["content", "insights"]:
        # Create initial state
        state: ChatState = {
            "messages": lc_messages,
            "upload_id": request.upload_id,
            "intent": "factual" if request.mode == "content" else "reflective",
            "mode_used": request.mode,
            "context_str": "",
            "sources": [],
            "response": ""
        }
        
        # Run the appropriate RAG
        if request.mode == "content":
            state = content_rag(state)
        else:
            state = insights_rag(state)
        
        # Generate response
        state = generate_response(state)
        
        result = state
    else:
        # Use auto-classification via the graph
        chain_input = {
            "messages": lc_messages,
            "upload_id": request.upload_id
        }
        result = chat_graph.invoke(chain_input)

    # Parse result
    response_text = result.get("response", "Sorry, I couldn't generate a response.")
    mode = result.get("mode_used", "unknown")
    sources = result.get("sources", [])

    citations = []
    for s in sources:
        if isinstance(s, dict):
            citations.append(Citation(
                date=str(s.get("date", "")),
                sender=str(s.get("from", "")),
                subject=str(s.get("subject", ""))
            ))
        elif isinstance(s, str):
            citations.append(Citation(date="", sender=s, subject=""))

    return ChatResponse(
        content=response_text,
        citations=citations,
        mode_used=mode
    )
