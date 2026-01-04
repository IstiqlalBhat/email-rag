"""
Chat routes for RAG and coaching modes.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict
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
    mode: Optional[str] = "auto"  # "auto", "content", "insights"


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
