"""
LangGraph chat router for RAG modes.
Routes between Content RAG and Insights RAG.
"""
from typing import TypedDict, Literal, List, Any, Optional
from langgraph.graph import StateGraph, END
from loguru import logger
import os
import json

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from core.config import settings

# Initialize LLM
llm = ChatAnthropic(
    model=settings.LLM_MODEL,
    api_key=settings.ANTHROPIC_API_KEY,
    temperature=0.3
)

# Initialize Embeddings
embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)

# Lazy-initialized vector store
_vector_store: Optional[PineconeVectorStore] = None

def get_vector_store() -> Optional[PineconeVectorStore]:
    """Get or create the Pinecone vector store. Returns None if index doesn't exist."""
    global _vector_store
    
    if _vector_store is not None:
        return _vector_store
    
    try:
        # Check if index exists, create if not
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        
        existing_indexes = [idx.name for idx in pc.list_indexes()]
        
        if settings.PINECONE_INDEX_NAME not in existing_indexes:
            logger.info(f"Creating Pinecone index: {settings.PINECONE_INDEX_NAME}")
            pc.create_index(
                name=settings.PINECONE_INDEX_NAME,
                dimension=settings.EMBEDDING_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            logger.info("Index created successfully")
        
        _vector_store = PineconeVectorStore(
            index_name=settings.PINECONE_INDEX_NAME,
            embedding=embeddings,
            pinecone_api_key=settings.PINECONE_API_KEY
        )
        return _vector_store
    except Exception as e:
        logger.error(f"Failed to initialize Pinecone: {e}")
        return None


class ChatState(TypedDict):
    """State for chat interaction."""
    messages: list  # List of LangChain messages
    upload_id: str  # The active PST upload ID context
    
    # Routing
    intent: Literal["factual", "reflective", "unknown"]
    mode_used: str

    # Retrieved context
    context_str: str
    sources: list

    # Response
    response: str


def classify_intent(state: ChatState) -> ChatState:
    """Classify user query intent."""
    last_message = state["messages"][-1]
    last_content = last_message.content.lower() if hasattr(last_message, 'content') else str(last_message)
    
    logger.info(f"Classifying query: {last_content[:50]}...")

    # Simple heuristic classification
    reflective_keywords = ["pattern", "tendency", "usually", "work on", "improve", "coach", "insight", "behavior", "stress", "feeling", "tone"]
    factual_keywords = ["what did", "when did", "who", "summarize", "find", "search", "email about"]

    if any(kw in last_content for kw in reflective_keywords):
        state["intent"] = "reflective"
    else:
        # Default to factual/content search for safety
        state["intent"] = "factual"

    logger.info(f"Classified intent as: {state['intent']}")
    return state


def route_to_mode(state: ChatState) -> Literal["content_rag", "insights_rag"]:
    if state["intent"] == "reflective":
        return "insights_rag"
    else:
        return "content_rag"


def content_rag(state: ChatState) -> ChatState:
    """Content RAG: retrieve from email chunks in Pinecone with query expansion."""
    logger.info("Running Content RAG")
    state["mode_used"] = "content"
    
    messages = state.get("messages", [])
    last_message = messages[-1] if messages else None
    
    if not last_message:
        state["context_str"] = "No query provided."
        state["sources"] = []
        return state
    
    original_query = last_message.content if hasattr(last_message, 'content') else str(last_message)
    logger.info(f"Original query: {original_query[:100]}...")
    
    # Query expansion: extract key search terms for better vector match
    # This converts "Any emails from Dina?" → "Dina Hi Dina Dear Dina Dina Cartagena"
    try:
        expansion_prompt = f"""Extract the key search terms from this question about emails.
Output ONLY the search terms, nothing else. Include variations like:
- The person's name in different forms (first name, full name, "Hi [Name]", "Dear [Name]")
- Key topics or subjects mentioned
- Any specific dates or keywords

Question: {original_query}

Search terms:"""
        
        expansion_response = llm.invoke(expansion_prompt)
        expanded_terms = expansion_response.content.strip()
        
        # Combine original query with expanded terms for better coverage
        search_query = f"{original_query} {expanded_terms}"
        logger.info(f"Expanded search query: {search_query[:150]}...")
    except Exception as e:
        logger.error(f"Query expansion failed: {e}")
        search_query = original_query

    context_parts = []
    sources = []
    
    # Get vector store (lazy init)
    vector_store = get_vector_store()
    
    if vector_store:
        try:
            # Use k=10 for better coverage when searching for people/names
            results = vector_store.similarity_search(search_query, k=10)
            
            for doc in results:
                date = doc.metadata.get("date", "Unknown Date")
                sender = doc.metadata.get("sender", "Unknown Sender")
                subject = doc.metadata.get("subject", "No Subject")
                
                context_parts.append(f"Date: {date}\nFrom: {sender}\nSubject: {subject}\nContent: {doc.page_content}")
                sources.append({"date": date, "from": sender, "subject": subject})
        except Exception as e:
            logger.error(f"Error searching Pinecone: {e}")
            context_parts.append("No email data available yet. Please upload a PST file first.")
    else:
        context_parts.append("No email data available yet. Please upload a PST file first.")
        
    state["context_str"] = "\n\n---\n\n".join(context_parts) if context_parts else "No context available."
    state["sources"] = sources
    
    return state


def insights_rag(state: ChatState) -> ChatState:
    """Insights RAG: retrieve from insight artifacts."""
    logger.info("Running Insights RAG")
    state["mode_used"] = "insights"
    
    upload_id = state.get("upload_id")
    context_str = ""
    
    # Try to load pre-computed insights
    if upload_id:
        insights_path = os.path.join(settings.DATA_DIR, "insights", f"{upload_id}_insights.json")
        if os.path.exists(insights_path):
            try:
                with open(insights_path, "r", encoding="utf-8") as f:
                    insights_data = json.load(f)
                    context_str = f"PRE-COMPUTED COACHING INSIGHTS:\n{json.dumps(insights_data, indent=2)}\n"
            except Exception as e:
                logger.error(f"Failed to load insights: {e}")
    
    # Also grab proper email examples to support the coaching (Hybrid approach)
    vector_store = get_vector_store()
    
    if vector_store:
        try:
            last_message = state["messages"][-1]
            query = last_message.content if hasattr(last_message, 'content') else str(last_message)
            results = vector_store.similarity_search(query, k=3)
            
            for doc in results:
                context_str += f"\n\nSUPPORTING EMAIL:\n{doc.page_content}"
        except Exception as e:
            logger.error(f"Error searching Pinecone for insights: {e}")
    
    if not context_str:
        context_str = "No email data or insights available yet. Please upload a PST file first to get personalized coaching."

    state["context_str"] = context_str
    state["sources"] = ["Insights Engine"]
    
    return state


def generate_response(state: ChatState) -> ChatState:
    """Generate final response using LLM with conversation history context."""
    logger.info(f"Generating response in {state['mode_used']} mode")
    
    # Build conversation history string for context
    history_str = ""
    messages = state.get("messages", [])
    if len(messages) > 1:
        # Include previous turns for context (last 6 messages max)
        recent_history = messages[-7:-1] if len(messages) > 7 else messages[:-1]
        history_parts = []
        for msg in recent_history:
            role = "User" if hasattr(msg, 'content') and isinstance(msg, HumanMessage) else "Assistant"
            content = msg.content if hasattr(msg, 'content') else str(msg)
            history_parts.append(f"{role}: {content}")
        history_str = "\n".join(history_parts)
    
    system_prompt = ""
    if state["mode_used"] == "insights":
        system_prompt = """You are an empathetic executive coach with excellent memory and contextual understanding.

**CRITICAL INSTRUCTIONS:**
- USE THE CONVERSATION HISTORY to understand follow-up questions and pronouns (e.g., "he", "she", "they")
- INFER full names from partial mentions: if user says "Freeman", look for "Dr. Freeman" or similar in context
- When a partial name or reference is ambiguous, check the email context AND conversation history for matches
- Focus on behavioral patterns, improvement areas, and positive reinforcement
- Do not diagnose. Be constructive.
- If no data is available, explain that the user needs to upload their PST file first."""
    else:
        system_prompt = """You are a smart email assistant with excellent context awareness and memory.

**CRITICAL INSTRUCTIONS FOR FINDING PEOPLE:**
- When user asks about emails "from", "to", or "about" a person, look for that name EVERYWHERE:
  - In the sender/from field
  - In the recipient/to field (emails starting with "Hi [Name]" or "Dear [Name]")
  - Mentioned anywhere in the email body
- "Emails from Dina" should also find emails TO Dina or mentioning Dina
- INFER full names from partial mentions: "Freeman" → "Dr. Freeman", "Dina" → "Dina Cartagena"
- If you find emails where the user wrote TO someone (e.g., "Hi Dina"), report those too!

**CONTEXT AWARENESS:**
- USE CONVERSATION HISTORY to understand follow-up questions
- If user references "he", "she", "they" - use conversation history to determine who they mean
- Cite the date and sender when possible
- If the answer is not in the context, say so
- If no email data is available, explain that the user needs to upload their PST file first."""

    # Build the prompt with history if available
    if history_str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("system", "CONVERSATION HISTORY:\n{history}"),
            ("system", "EMAIL CONTEXT:\n{context}"),
            ("human", "{question}")
        ])
    else:
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("system", "EMAIL CONTEXT:\n{context}"),
            ("human", "{question}")
        ])
    
    last_message = state["messages"][-1]
    question = last_message.content if hasattr(last_message, 'content') else str(last_message)
    
    chain = prompt | llm
    
    invoke_args = {
        "context": state["context_str"],
        "question": question
    }
    if history_str:
        invoke_args["history"] = history_str
    
    response_msg = chain.invoke(invoke_args)
    
    state["response"] = response_msg.content
    return state


# Build the chat graph
def create_chat_graph() -> StateGraph:
    """Create the chat routing graph."""
    workflow = StateGraph(ChatState)

    # Add nodes
    workflow.add_node("classify", classify_intent)
    workflow.add_node("content_rag", content_rag)
    workflow.add_node("insights_rag", insights_rag)
    workflow.add_node("generate", generate_response)

    # Define routing
    workflow.set_entry_point("classify")
    
    workflow.add_conditional_edges(
        "classify",
        route_to_mode,
        {
            "content_rag": "content_rag",
            "insights_rag": "insights_rag"
        }
    )

    # Edges
    workflow.add_edge("content_rag", "generate")
    workflow.add_edge("insights_rag", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()


# Export compiled graph
chat_graph = create_chat_graph()
