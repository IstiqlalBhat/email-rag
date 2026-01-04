"""
LangGraph chat router for RAG modes.
Routes between Content RAG and Insights RAG.
"""
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from loguru import logger


class ChatState(TypedDict):
    """State for chat interaction."""
    messages: list
    mailbox_id: int
    tenant_id: int

    # Routing
    intent: Literal["factual", "reflective", "unknown"]
    mode_used: str

    # Retrieved context
    retrieved_chunks: list
    retrieved_insights: list

    # Response
    response: str
    citations: list

    # Guardrails
    redaction_level: str
    passed_guardrails: bool


def classify_intent(state: ChatState) -> ChatState:
    """Classify user query intent."""
    logger.info("Classifying query intent")

    last_message = state["messages"][-1]["content"].lower()

    # Simple heuristic classification
    reflective_keywords = ["pattern", "tend to", "usually", "work on", "improve", "coach", "insight"]
    factual_keywords = ["what did", "when did", "who", "summarize", "find"]

    if any(kw in last_message for kw in reflective_keywords):
        state["intent"] = "reflective"
    elif any(kw in last_message for kw in factual_keywords):
        state["intent"] = "factual"
    else:
        state["intent"] = "unknown"

    logger.info(f"Classified intent as: {state['intent']}")
    return state


def route_to_mode(state: ChatState) -> Literal["content_rag", "insights_rag", "clarify"]:
    """Route to appropriate RAG mode based on intent."""
    if state["intent"] == "factual":
        return "content_rag"
    elif state["intent"] == "reflective":
        return "insights_rag"
    else:
        return "clarify"


def content_rag(state: ChatState) -> ChatState:
    """Content RAG: retrieve from email chunks."""
    logger.info("Running Content RAG")
    state["mode_used"] = "content"

    # TODO: Implement content retrieval
    # - Query vector DB (content index)
    # - Apply metadata filters
    # - Retrieve top-k chunks with citations

    state["retrieved_chunks"] = []
    state["citations"] = []

    return state


def insights_rag(state: ChatState) -> ChatState:
    """Insights RAG: retrieve from insight artifacts."""
    logger.info("Running Insights RAG")
    state["mode_used"] = "insights"

    # TODO: Implement insights retrieval
    # - Query insights index
    # - Optionally pull supporting examples from content

    state["retrieved_insights"] = []
    state["citations"] = []

    return state


def clarify(state: ChatState) -> ChatState:
    """Ask for clarification when intent is unclear."""
    logger.info("Requesting clarification")
    state["mode_used"] = "clarify"
    state["response"] = "Could you clarify whether you're looking for specific information from your emails or broader patterns?"

    return state


def apply_guardrails(state: ChatState) -> ChatState:
    """Apply safety and privacy guardrails."""
    logger.info("Applying guardrails")

    # TODO: Implement guardrails
    # - Check for diagnosis language
    # - Check for profiling others
    # - Apply redaction based on settings
    # - Enforce citation requirements

    state["passed_guardrails"] = True
    return state


def generate_response(state: ChatState) -> ChatState:
    """Generate final response using LLM."""
    logger.info(f"Generating response in {state['mode_used']} mode")

    # TODO: Implement response generation
    # - Build context from retrieved content/insights
    # - Call LLM with appropriate prompt
    # - Format citations

    state["response"] = "Generated response based on your emails."
    return state


# Build the chat graph
def create_chat_graph() -> StateGraph:
    """Create the chat routing graph."""
    workflow = StateGraph(ChatState)

    # Add nodes
    workflow.add_node("classify", classify_intent)
    workflow.add_node("content_rag", content_rag)
    workflow.add_node("insights_rag", insights_rag)
    workflow.add_node("clarify", clarify)
    workflow.add_node("guardrails", apply_guardrails)
    workflow.add_node("generate", generate_response)

    # Define routing
    workflow.set_entry_point("classify")
    workflow.add_conditional_edges(
        "classify",
        route_to_mode,
        {
            "content_rag": "content_rag",
            "insights_rag": "insights_rag",
            "clarify": "clarify"
        }
    )

    # Both RAG modes flow to guardrails
    workflow.add_edge("content_rag", "guardrails")
    workflow.add_edge("insights_rag", "guardrails")
    workflow.add_edge("guardrails", "generate")
    workflow.add_edge("generate", END)
    workflow.add_edge("clarify", END)

    return workflow.compile()


# Export compiled graph
chat_graph = create_chat_graph()
