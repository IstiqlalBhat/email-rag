# PST Coach - Email Intelligence & Self-Reflection Platform

An AI-powered email intelligence platform that analyzes Outlook PST files to provide personalized communication coaching, semantic search, and graph-based knowledge discovery.

## Table of Contents

- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Detailed Architecture](#detailed-architecture)
- [How It Works](#how-it-works)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

---

## Features

### Core Capabilities

- **PST File Processing**: Upload and parse Outlook PST files using Apache Tika
- **Smart Deduplication**: Automatic detection of duplicate uploads via MD5 hashing
- **Three RAG Modes**:
  - **Ask Inbox**: Natural language semantic search across your emails
  - **Coach Me**: Personalized coaching insights about communication patterns
  - **Graph RAG**: Knowledge graph-based retrieval with entity relationships
- **Explore Mode**: Interactive visualizations of email patterns and analytics
- **AI-Powered Analysis**: Uses Claude Sonnet 4.5 for intelligent insights
- **Privacy-First**: All processing happens locally or in your cloud instances

### Advanced Features

- **Query Expansion**: Automatically expands queries for better search results
- **Conversation Context**: Maintains chat history for follow-up questions
- **Multi-Hop Reasoning**: Graph traversal for complex queries
- **Incremental Processing**: Redundancy checks prevent re-processing
- **Source Attribution**: Every response includes source citations
- **Redis Caching**: LLM responses and analytics data cached for performance
- **Rate Limiting**: API protection with per-endpoint rate limits

---

## Architecture Overview

PST Coach is built on a modern microservices architecture with three primary layers:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                           │
│                         (Next.js Frontend)                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────────┐   │
│  │  Upload  │  │   Chat   │  │ Explore  │  │  Visualizations │   │
│  │   Page   │  │   Page   │  │   Mode   │  │  (Graph/Charts) │   │
│  └──────────┘  └──────────┘  └──────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                               │ HTTP/REST
┌─────────────────────────────────────────────────────────────────────┐
│                         APPLICATION LAYER                            │
│                         (FastAPI Backend)                            │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                      API Routes Layer                           │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────────┐     │ │
│  │  │ Uploads │  │  Chat   │  │Analytics│  │  Graph RAG   │     │ │
│  │  └─────────┘  └─────────┘  └─────────┘  └──────────────┘     │ │
│  └────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                   Middleware Layer                              │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐    │ │
│  │  │ Error Handle │  │  Request ID  │  │  Rate Limiter    │    │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘    │ │
│  │  ┌──────────────────────────────────────────────────────┐    │ │
│  │  │              Redis Cache Layer                        │    │ │
│  │  └──────────────────────────────────────────────────────┘    │ │
│  └────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                   Orchestration Layer                           │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │              LangGraph Chat Router                        │ │ │
│  │  │  ┌────────────┐  ┌────────────┐  ┌─────────────────┐   │ │ │
│  │  │  │  Classify  │→ │ Content    │→ │   Generate      │   │ │ │
│  │  │  │  Intent    │  │ RAG        │  │   Response      │   │ │ │
│  │  │  └────────────┘  └────────────┘  └─────────────────┘   │ │ │
│  │  │                     ↓                                    │ │ │
│  │  │                  ┌────────────┐                          │ │ │
│  │  │                  │ Insights   │                          │ │ │
│  │  │                  │ RAG        │                          │ │ │
│  │  │                  └────────────┘                          │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                      Service Layer                              │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌─────────┐ │ │
│  │  │  Ingest    │  │   Index    │  │  Insights  │  │  Graph  │ │ │
│  │  │  Service   │  │  Service   │  │  Processor │  │  RAG    │ │ │
│  │  └────────────┘  └────────────┘  └────────────┘  └─────────┘ │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA & AI LAYER                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │PostgreSQL│  │  Redis   │  │ Pinecone │  │  Claude API      │   │
│  │(Metadata)│  │ (Cache)  │  │(Vectors) │  │  (Anthropic)     │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘   │
│  ┌──────────┐  ┌──────────────────────────────────────────────┐   │
│  │  Tika    │  │        HuggingFace Embeddings                │   │
│  │ (Parser) │  │     (sentence-transformers/all-MiniLM-L6-v2) │   │
│  └──────────┘  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend Framework** | Next.js 14 (React, TypeScript) | Server-side rendering, routing |
| **UI Library** | Tailwind CSS, Lucide Icons | Responsive design, icons |
| **Backend Framework** | FastAPI (Python 3.11) | REST API, async support |
| **AI Orchestration** | LangGraph, LangChain | Workflow orchestration, RAG chains |
| **LLM** | Claude Sonnet 4.5 (Anthropic) | Text generation, analysis |
| **Embeddings** | HuggingFace all-MiniLM-L6-v2 | 384-dim local embeddings |
| **Vector Database** | Pinecone (Serverless) | Semantic search, similarity |
| **Document Parser** | Apache Tika 3.0 | PST file extraction |
| **Graph Engine** | NetworkX, FAISS | Knowledge graph, local vectors |
| **Metadata DB** | PostgreSQL 15 | Structured data storage |
| **Cache** | Redis 7 | Response caching, rate limiting, session management |
| **Containerization** | Docker Compose | Multi-container orchestration |
| **Validation** | Pydantic v2 | Schema validation |
| **Text Processing** | spaCy, NLTK | NER, text analysis |

---

## Quick Start

### Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Pinecone API Key ([get free tier](https://www.pinecone.io/))
- Anthropic API Key ([get from console](https://console.anthropic.com/))

### Installation

1. **Clone and navigate**:
   ```bash
   git clone <your-repo-url>
   cd RAG-personal/pst-coach
   ```

2. **Configure environment**:
   ```bash
   # Backend
   cp backend/env.example backend/.env

   # Frontend
   cp frontend/env.local.example frontend/.env.local
   ```

3. **Add API keys to `backend/.env`**:
   ```bash
   PINECONE_API_KEY=your-pinecone-key
   ANTHROPIC_API_KEY=your-anthropic-key
   ```

4. **Start services**:
   ```bash
   docker-compose up -d
   ```

5. **Verify deployment**:
   ```bash
   docker-compose ps
   ```

   All 6 containers should be running:
   - `pst-coach-frontend` (port 3001)
   - `pst-coach-backend` (port 8000)
   - `pst-coach-postgres` (port 5433)
   - `pst-coach-redis` (port 6379)
   - `pst-coach-tika` (port 9998)
   - `pst-coach-qdrant` (port 6333-6334)

6. **Access application**:
   - Frontend UI: http://localhost:3001
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### First Upload

1. Go to http://localhost:3001/upload
2. Upload your PST file (max 5GB)
3. Monitor processing: `docker logs pst-coach-backend -f`
4. Once complete, navigate to Chat page
5. Try queries like:
   - "Show me emails from last month"
   - "What patterns do you see in my communication?"
   - "How do I handle urgent requests?"

---

## Detailed Architecture

### 1. Frontend Architecture (Next.js)

```
frontend/
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── page.tsx                  # Landing page
│   │   ├── chat/page.tsx             # Multi-mode chat interface
│   │   ├── upload/page.tsx           # PST upload interface
│   │   └── dashboard/page.tsx        # Analytics dashboard
│   ├── components/
│   │   ├── ui/                       # Reusable UI components
│   │   │   └── LiquidButton.tsx      # Animated button
│   │   └── visualizations/           # Data visualization components
│   │       ├── VisualizationPanel.tsx    # Charts and graphs
│   │       └── GraphRAGPanel.tsx         # Knowledge graph UI
│   └── lib/
│       └── api.ts                    # Axios HTTP client
└── public/                           # Static assets
```

**Key Frontend Features**:

- **Mode Switching**: Toggle between Ask, Coach, Explore, and Graph modes
- **Conversation History**: Maintains chat context for follow-up questions
- **Source Citations**: Displays email metadata for each response
- **Upload Management**: Drag-and-drop PST upload with progress tracking
- **Visualizations**: Interactive charts for email patterns and trends

### 2. Backend Architecture (FastAPI)

```
backend/
├── api/
│   ├── main.py                       # FastAPI app entry point
│   ├── routes/                       # API endpoint handlers
│   │   ├── uploads.py                # POST /api/uploads (upload PST)
│   │   ├── chat.py                   # POST /api/chat/router (RAG queries)
│   │   ├── analytics.py              # GET /api/analytics/* (metrics)
│   │   └── graph_rag.py              # POST /api/graph/* (graph ops)
│   └── middleware/
│       ├── error_handler.py          # Global error handling
│       ├── request_id.py             # Request tracking
│       └── rate_limiter.py           # Redis-based rate limiting
├── core/
│   ├── config.py                     # Pydantic settings
│   └── logging.py                    # Loguru setup
├── graph/
│   └── chat_graph.py                 # LangGraph workflow
├── models/                           # SQLAlchemy models (future)
└── services/                         # Business logic layer
    ├── ingest/
    │   └── service.py                # PST parsing & extraction
    ├── index/
    │   └── service.py                # Vector embedding & Pinecone
    ├── insights/
    │   └── processor.py              # AI coaching insights
    ├── cache/
    │   └── redis_service.py          # Redis caching & rate limiting
    └── graph_rag/
        ├── service.py                # Graph RAG orchestration
        ├── knowledge_graph.py        # NetworkX graph builder
        ├── query_engine.py           # Graph traversal & query
        └── models.py                 # Pydantic schemas
```

### 3. LangGraph Chat Router

The system uses LangGraph to orchestrate different RAG modes based on query intent:

```python
# Simplified workflow from backend/graph/chat_graph.py

ChatState = TypedDict({
    "messages": list,           # Conversation history
    "upload_id": str,           # Active PST context
    "intent": str,              # "factual" | "reflective"
    "mode_used": str,           # "content" | "insights" | "graph"
    "context_str": str,         # Retrieved context
    "sources": list,            # Source attribution
    "response": str             # Final answer
})

Workflow:
1. classify_intent(state)       # Classify user query
2. route_to_mode(state)         # Route to appropriate RAG
   ├─> content_rag(state)       # Vector search in Pinecone
   ├─> insights_rag(state)      # Load pre-computed insights
   └─> graph_rag(state)         # Graph traversal (future)
3. generate_response(state)     # Generate answer with Claude
```

**Intent Classification**:
- **Factual** (→ Content RAG): "Show me emails from Dina", "What did John say about the project?"
- **Reflective** (→ Insights RAG): "How do I handle stress?", "What patterns in my communication?"

### 4. Service Layer Architecture

#### 4.1 Ingest Service (`services/ingest/service.py`)

**Responsibilities**:
- Accept PST file uploads
- Detect duplicate uploads via MD5 hashing
- Parse PST files using Apache Tika
- Extract individual emails with metadata
- Save to JSON format

**Key Functions**:
```python
handle_upload(file, background_tasks)
    ├─> check_if_already_indexed(upload_id)
    ├─> generate upload_id = f"{file_hash}-{uuid}"
    └─> background_tasks.add_task(process_pst_file)

process_pst_file(file_path, upload_id)
    ├─> call Apache Tika API
    ├─> parse_emails_from_blob(content)
    ├─> save to data/extracted/{upload_id}.json
    └─> trigger index_messages(upload_id)
```

**Email Parsing Strategy**:
1. Pattern matching on headers (`From:`, `Subject:`, `Date:`)
2. Body extraction with HTML stripping
3. Email deduplication via `email_id` hash
4. Fallback to chunking if no headers found

#### 4.2 Index Service (`services/index/service.py`)

**Responsibilities**:
- Chunk emails into smaller segments
- Generate embeddings using HuggingFace
- Upsert vectors to Pinecone
- Track indexed uploads to prevent re-indexing
- Trigger insights generation

**Key Functions**:
```python
index_messages(upload_id, force_reindex=False)
    ├─> check if already indexed
    ├─> ensure_pinecone_index()
    ├─> load emails from data/extracted/{upload_id}.json
    ├─> split text (chunk_size=500, overlap=50)
    ├─> embed chunks (HuggingFace all-MiniLM-L6-v2)
    ├─> upsert to Pinecone (batch_size=100)
    ├─> mark_upload_indexed(upload_id, vector_count)
    └─> trigger generate_insights(upload_id)
```

**Vector Schema**:
```python
{
    "id": f"{upload_id}_{email_id}_{chunk_index}",
    "values": [0.123, -0.456, ...],  # 384-dim embedding
    "metadata": {
        "upload_id": "abc123-xyz",
        "email_id": "def456",
        "date": "2024-01-15 10:30:00",
        "sender": "john@example.com",
        "to": "team@example.com",
        "subject": "Project Update",
        "text": "Email chunk text...",
        "type": "email"
    }
}
```

#### 4.3 Insights Processor (`services/insights/processor.py`)

**Responsibilities**:
- Analyze user's communication patterns
- Identify behavioral trends
- Generate coaching recommendations
- Save insights to JSON

**Key Functions**:
```python
generate_insights(upload_id)
    ├─> load emails from data/extracted/{upload_id}.json
    ├─> identify_user_email(emails)  # Most frequent sender
    ├─> filter emails FROM user (max 50 samples)
    ├─> send to Claude with coaching prompt
    ├─> parse structured JSON response
    └─> save to data/insights/{upload_id}_insights.json
```

**Insights Schema**:
```json
{
    "summary": "Executive summary...",
    "behavioral_patterns": ["Pattern 1", "Pattern 2"],
    "communication_style": "Direct and concise...",
    "mood_trends": "Generally positive...",
    "strengths": ["Strong follow-up", "Clear subject lines"],
    "areas_for_improvement": ["Response time", "After-hours emails"],
    "coaching_tips": ["Tip 1", "Tip 2"]
}
```

#### 4.4 Graph RAG Service (`services/graph_rag/`)

**Responsibilities**:
- Build knowledge graphs from emails
- Extract entities and relationships
- Perform graph traversal for queries
- Visualize graph structure

**Components**:

**4.4.1 Knowledge Graph Builder** (`knowledge_graph.py`):
```python
KnowledgeGraph.build_graph(documents, llm, embeddings)
    ├─> extract_concepts(doc)        # Use LLM to extract entities
    ├─> compute_similarity(concepts) # Cosine similarity
    ├─> add_edges(threshold=0.7)     # Connect similar concepts
    └─> persist to NetworkX graph

Graph Structure:
    Nodes: {
        "id": concept_index,
        "content": "Entity or concept text",
        "embedding": [0.1, -0.2, ...]
    }
    Edges: {
        "weight": similarity_score  # 0.0 - 1.0
    }
```

**4.4.2 Query Engine** (`query_engine.py`):
```python
GraphQueryEngine.query(query_str)
    ├─> retrieve_top_k_nodes(query)  # Vector search in FAISS
    ├─> traverse_graph(start_nodes)  # Multi-hop traversal
    ├─> filter_content(traversed_nodes)
    ├─> generate_answer(llm, filtered_context)
    └─> return GraphQueryResult(answer, traversal_path)
```

**Graph Traversal Algorithm**:
1. Start from top-k most relevant nodes (vector search)
2. Traverse to neighbors based on edge weights
3. Limit traversal depth (max_steps=10)
4. Collect context from visited nodes
5. Rank by relevance and recency

### 5. Data Storage Architecture

```
data/
├── uploads/                          # Original PST files
│   └── {upload_id}.pst
├── extracted/                        # Parsed emails (JSON)
│   └── {upload_id}.json
├── insights/                         # AI-generated insights
│   └── {upload_id}_insights.json
├── graphs/                           # Persisted knowledge graphs
│   ├── {upload_id}_graph.pkl        # NetworkX graph (pickled)
│   └── {upload_id}_vectors/         # FAISS vector store
└── indexed_uploads.json              # Tracking file for indexed uploads
```

### 6. RAG Modes Comparison

| Feature | Content RAG | Insights RAG | Graph RAG |
|---------|-------------|--------------|-----------|
| **Query Type** | Factual search | Coaching questions | Complex reasoning |
| **Data Source** | Pinecone vectors | Pre-computed insights | Knowledge graph |
| **Retrieval** | Similarity search | JSON lookup + vectors | Graph traversal |
| **Context** | Top-K email chunks | Insights + examples | Multi-hop entities |
| **Use Case** | "Emails from John" | "Communication patterns" | "How are X and Y related?" |
| **Latency** | ~2-3 sec | ~1-2 sec | ~5-8 sec |
| **Accuracy** | High for exact matches | High for patterns | High for relationships |

---

## How It Works

### End-to-End Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. UPLOAD & DEDUPLICATION                                           │
└─────────────────────────────────────────────────────────────────────┘
    User uploads PST
         ↓
    Calculate MD5 hash
         ↓
    Check if already processed  ────→ [YES] Return existing upload_id
         ↓ [NO]
    Save to data/uploads/{upload_id}.pst
         ↓
    Start background processing

┌─────────────────────────────────────────────────────────────────────┐
│ 2. PST PARSING (Apache Tika)                                        │
└─────────────────────────────────────────────────────────────────────┘
    Check if data/extracted/{upload_id}.json exists ─→ [YES] Skip
         ↓ [NO]
    Send PST to Tika server (HTTP POST)
         ↓
    Tika extracts raw text
         ↓
    Parse emails using regex patterns
         ├─> Extract headers (From, To, Subject, Date)
         ├─> Extract body content
         └─> Clean and format text
         ↓
    Generate email_id for each (MD5 hash)
         ↓
    Save to data/extracted/{upload_id}.json

┌─────────────────────────────────────────────────────────────────────┐
│ 3. VECTOR EMBEDDING (HuggingFace + Pinecone)                       │
└─────────────────────────────────────────────────────────────────────┘
    Check indexed_uploads.json ────→ [EXISTS] Skip indexing
         ↓ [NOT INDEXED]
    Load emails from JSON
         ↓
    For each email:
         ├─> Create full text (headers + body)
         ├─> Split into chunks (500 chars, 50 overlap)
         ├─> Generate embedding (all-MiniLM-L6-v2)
         └─> Create vector_id = {upload_id}_{email_id}_{chunk}
         ↓
    Batch upsert to Pinecone (100 vectors/batch)
         ↓
    Mark upload as indexed in indexed_uploads.json

┌─────────────────────────────────────────────────────────────────────┐
│ 4. INSIGHTS GENERATION (Claude Sonnet)                             │
└─────────────────────────────────────────────────────────────────────┘
    Load emails from JSON
         ↓
    Identify user email (most frequent sender)
         ↓
    Filter emails FROM user (max 50)
         ↓
    Send to Claude with coaching prompt
         ↓
    Parse structured JSON response
         ↓
    Save to data/insights/{upload_id}_insights.json

┌─────────────────────────────────────────────────────────────────────┐
│ 5. KNOWLEDGE GRAPH BUILDING (Optional)                             │
└─────────────────────────────────────────────────────────────────────┘
    User clicks "Build Graph"
         ↓
    Load extracted emails
         ↓
    Split into chunks
         ↓
    For each chunk:
         ├─> Extract concepts/entities (Claude)
         ├─> Generate embeddings
         └─> Create node in graph
         ↓
    Compute pairwise similarity
         ↓
    Add edges where similarity > threshold (0.7)
         ↓
    Persist graph (NetworkX → pickle)
         ↓
    Save local vectors (FAISS)

┌─────────────────────────────────────────────────────────────────────┐
│ 6. QUERY PROCESSING (LangGraph Router)                             │
└─────────────────────────────────────────────────────────────────────┘
    User enters query
         ↓
    LangGraph: classify_intent(query)
         ├─> "factual" → route to Content RAG
         └─> "reflective" → route to Insights RAG
         ↓
    Content RAG:
         ├─> Query expansion (Claude)
         ├─> Embed query (HuggingFace)
         ├─> Similarity search (Pinecone, k=10)
         ├─> Retrieve email chunks
         └─> Send to Claude with context
         ↓
    Insights RAG:
         ├─> Load insights JSON
         ├─> (Optional) Retrieve supporting emails
         └─> Send to Claude with insights
         ↓
    Graph RAG:
         ├─> Embed query
         ├─> Find top-k starting nodes (FAISS)
         ├─> Traverse graph (multi-hop)
         ├─> Collect context from visited nodes
         └─> Send to Claude with graph context
         ↓
    Generate response + source citations
         ↓
    Return to frontend
```

### Query Examples

**Content RAG**:
```
Query: "Show me emails from Dina"
  ↓
Query Expansion: "Dina Hi Dina Dear Dina Dina Cartagena"
  ↓
Vector Search: similarity_search(expanded_query, k=10)
  ↓
Context: 10 email chunks mentioning Dina
  ↓
Prompt: "Based on these emails, answer: Show me emails from Dina"
  ↓
Response: "I found 8 emails involving Dina Cartagena..."
  + Citations: [{date, sender, subject}, ...]
```

**Insights RAG**:
```
Query: "How do I handle urgent requests?"
  ↓
Load: data/insights/{upload_id}_insights.json
  ↓
Context: Pre-computed insights + sample urgent emails
  ↓
Prompt: "Using these insights, answer: How do I handle urgent requests?"
  ↓
Response: "Based on your patterns, you typically respond to urgent..."
```

**Graph RAG**:
```
Query: "What's the relationship between Project Alpha and Sarah?"
  ↓
Find Nodes: Vector search for "Project Alpha" and "Sarah"
  ↓
Traverse: Find shortest path or k-hop neighbors
  ↓
Context: All entities and emails along path
  ↓
Prompt: "Based on this graph context, explain the relationship..."
  ↓
Response: "Sarah is the lead on Project Alpha, as seen in..."
  + Visualization: Show graph with highlighted path
```

---

## Configuration

### Backend Environment Variables (`backend/.env`)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PINECONE_API_KEY` | Pinecone API key | - | ✅ |
| `ANTHROPIC_API_KEY` | Anthropic API key | - | ✅ |
| `LLM_MODEL` | Claude model name | `claude-3-5-sonnet-20241022` | ❌ |
| `EMBEDDING_MODEL` | HuggingFace model | `all-MiniLM-L6-v2` | ❌ |
| `EMBEDDING_DIMENSION` | Embedding size | `384` | ❌ |
| `PINECONE_INDEX_NAME` | Pinecone index | `pst-coach` | ❌ |
| `TIKA_SERVER_URL` | Tika endpoint | `http://tika:9998` | ❌ |
| `CHUNK_SIZE` | Text chunk size | `500` | ❌ |
| `CHUNK_OVERLAP` | Chunk overlap | `50` | ❌ |
| `MAX_PST_SIZE_MB` | Max upload size | `5000` | ❌ |
| `DATABASE_URL` | PostgreSQL URL | See config.py | ❌ |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` | ❌ |
| `CACHE_TTL_SECONDS` | Default cache TTL | `300` (5 min) | ❌ |
| `CACHE_LLM_TTL_SECONDS` | LLM response cache TTL | `3600` (1 hour) | ❌ |
| `RATE_LIMIT_REQUESTS` | Max requests per window | `60` | ❌ |
| `RATE_LIMIT_WINDOW_SECONDS` | Rate limit window | `60` | ❌ |
| `DEBUG` | Debug mode | `true` | ❌ |

### Redis Caching

The application uses Redis for:

| Feature | Cache Key Pattern | TTL |
|---------|------------------|-----|
| LLM Responses | `chat:{upload_id}:{hash}` | 1 hour |
| Timeline Data | `analytics:timeline:{upload_id}` | 10 min |
| Word Cloud Data | `analytics:wordcloud:{upload_id}` | 10 min |
| Network Data | `analytics:network:{upload_id}` | 10 min |

### Rate Limiting

| Endpoint | Limit |
|----------|-------|
| `/api/chat/*` | 30 req/min |
| `/api/analytics/*` | 60 req/min |
| `/api/uploads/*` | 10 req/min |
| `/api/graph/*` | 20 req/min |

Rate limit headers are included in all API responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in window
- `X-RateLimit-Window`: Window duration in seconds

### Frontend Environment Variables (`frontend/.env.local`)

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend URL | `http://localhost:8000` |

---

## API Reference

### Upload Endpoints

**POST `/api/uploads/`**
- Upload PST file
- Request: `multipart/form-data` with `file` field
- Response: `{upload_id, status, message}`

**GET `/api/uploads/`**
- List all uploads
- Response: `{uploads: [{upload_id, email_count, vector_count}]}`

**GET `/api/uploads/{upload_id}/status`**
- Get upload status
- Response: `{upload_id, status, email_count}`

### Chat Endpoints

**POST `/api/chat/router`**
- RAG query endpoint
- Request:
  ```json
  {
    "messages": [{"role": "user", "content": "Query"}],
    "upload_id": "abc123-xyz",
    "mode": "content" | "insights" | "graph"
  }
  ```
- Response:
  ```json
  {
    "content": "Answer text",
    "citations": [{date, sender, subject}],
    "mode_used": "content"
  }
  ```

### Graph RAG Endpoints

**POST `/api/graph/build`**
- Build knowledge graph
- Request: `{upload_id}`
- Response: `{status, message, node_count, edge_count}`

**POST `/api/graph/query`**
- Query knowledge graph
- Request: `{upload_id, query}`
- Response: `{answer, traversal_path, sources}`

**GET `/api/graph/status/{upload_id}`**
- Get graph build status
- Response: `{status, progress, node_count, edge_count}`

**GET `/api/graph/visualization/{upload_id}`**
- Get graph visualization data
- Response: `{nodes: [], edges: [], traversal_path: []}`

### Analytics Endpoints

**GET `/api/analytics/metrics`**
- Get email metrics
- Query params: `upload_id`, `start_date`, `end_date`
- Response: Email counts, trends, statistics

---

## Development

### Local Setup (Without Docker)

**Backend**:
```bash
cd pst-coach/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

**Frontend**:
```bash
cd pst-coach/frontend
npm install
npm run dev
```

**Dependencies**:
- PostgreSQL 15+ (port 5432)
- Redis 7+ (port 6379)
- Apache Tika (port 9998): `java -jar tika-server-standard-3.0.0.jar`

### Project Structure

```
pst-coach/
├── backend/
│   ├── api/                  # FastAPI routes & middleware
│   ├── core/                 # Config & logging
│   ├── graph/                # LangGraph workflows
│   ├── models/               # Database models
│   ├── services/             # Business logic
│   │   ├── ingest/
│   │   ├── index/
│   │   ├── insights/
│   │   └── graph_rag/
│   ├── init_db.py            # Database initialization
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages
│   │   ├── components/       # React components
│   │   └── lib/              # Utilities
│   ├── public/
│   └── package.json
├── docker-compose.yml
└── README.md
```

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Debugging

**View logs**:
```bash
# All containers
docker-compose logs -f

# Specific service
docker logs pst-coach-backend -f
docker logs pst-coach-tika -f
```

**Access databases**:
```bash
# PostgreSQL
docker exec -it pst-coach-postgres psql -U pstcoach -d pst_coach

# Redis
docker exec -it pst-coach-redis redis-cli
```

**Restart services**:
```bash
docker-compose restart backend
docker-compose restart frontend
```

---

## Troubleshooting

### Common Issues

**1. Containers won't start**
```bash
# Check Docker is running
docker ps

# Check logs
docker-compose logs

# Rebuild
docker-compose down
docker-compose up -d --build
```

**2. PST upload fails**
- Check Tika is running: `curl http://localhost:9998/tika`
- Check file size < 5GB
- View backend logs: `docker logs pst-coach-backend -f`

**3. No search results**
- Verify indexing completed: Check `data/indexed_uploads.json`
- Check Pinecone index: Visit Pinecone console
- Verify API keys in `backend/.env`

**4. Graph build fails**
- Ensure sufficient memory (4GB+ recommended)
- Check extracted emails exist: `ls data/extracted/`
- Monitor logs: `docker logs pst-coach-backend -f`

**5. Frontend can't connect**
- Verify backend is running: `curl http://localhost:8000/health`
- Check `frontend/.env.local` has correct API URL
- Check CORS settings in `backend/.env`

### Performance Tuning

For large PST files (>1GB):
- Increase Docker memory: Docker Desktop → Settings → Resources
- Adjust chunk size: `CHUNK_SIZE=1000` in `backend/.env`
- Monitor resources: `docker stats`

### Reset Everything

```bash
# Stop containers
docker-compose down

# Remove all data
rm -rf pst-coach/backend/data/*

# Remove volumes
docker-compose down -v

# Rebuild
docker-compose up -d --build
```

---

## Security Considerations

- Never commit `.env` files to version control
- Rotate API keys regularly
- PST files may contain sensitive data - handle with care
- Use strong `SECRET_KEY` in production
- Enable HTTPS for production deployments
- Review data before sharing insights
- Consider encryption at rest for stored PST files

---

## Future Enhancements

- [ ] User authentication (JWT, OAuth)
- [ ] Multi-user support with data isolation
- [ ] Real-time processing status via WebSockets
- [ ] Email thread reconstruction
- [ ] Sentiment analysis over time
- [ ] Export insights to PDF/CSV
- [ ] Support for MBOX, EML formats
- [ ] Advanced filters (date ranges, senders, topics)
- [ ] Email timeline visualization
- [ ] API rate limiting and caching
- [ ] Hybrid search (keyword + semantic)
- [ ] Fine-tuned embeddings for email domain

---

## License

MIT

---

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request with clear description

---

**Built with care for privacy-conscious professionals who want to understand and improve their communication patterns.**
