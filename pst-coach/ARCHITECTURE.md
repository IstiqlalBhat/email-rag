# PST Coach - Deep Technical Architecture

> **AI-Powered Email Intelligence & Self-Reflection Platform**

A sophisticated hybrid RAG (Retrieval-Augmented Generation) system that analyzes Outlook PST files to provide personalized communication coaching, semantic search, and graph-based knowledge discovery.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Technology Stack](#2-technology-stack)
3. [Architecture Diagram](#3-architecture-diagram)
4. [Backend Architecture](#4-backend-architecture)
5. [Frontend Architecture](#5-frontend-architecture)
6. [Data Flow Pipelines](#6-data-flow-pipelines)
7. [RAG Implementation Deep Dive](#7-rag-implementation-deep-dive)
8. [Graph RAG System](#8-graph-rag-system)
9. [Vector Database & Embeddings](#9-vector-database--embeddings)
10. [LLM Integration](#10-llm-integration)
11. [Caching & Rate Limiting](#11-caching--rate-limiting)
12. [API Reference](#12-api-reference)
13. [Storage Architecture](#13-storage-architecture)
14. [GPU Acceleration](#14-gpu-acceleration)
15. [Docker Infrastructure](#15-docker-infrastructure)
16. [Security Considerations](#16-security-considerations)

---

## 1. System Overview

### 1.1 Purpose

PST Coach transforms personal email archives into an intelligent knowledge base that provides:

- **Semantic Email Search** - Natural language queries over email history
- **Communication Coaching** - AI-powered behavioral analysis and improvement suggestions
- **Knowledge Graph Exploration** - Multi-hop relationship discovery across email content
- **Visual Analytics** - Timeline, word cloud, and network visualizations

### 1.2 Core Capabilities

| Feature | Description | RAG Mode |
|---------|-------------|----------|
| **Ask Inbox** | Factual queries about email content | Content RAG |
| **Coach Me** | Behavioral pattern analysis & coaching | Insights RAG |
| **Explore** | Visual analytics (timeline, wordcloud, network) | N/A |
| **Graph** | Complex multi-hop relationship queries | Graph RAG |

### 1.3 High-Level Architecture

```
                                    +------------------+
                                    |   User Browser   |
                                    +--------+---------+
                                             |
                                             | HTTPS
                                             v
+--------------------------------------------------+
|                  FRONTEND (Next.js 14)           |
|  - React 18 + TypeScript                         |
|  - Tailwind CSS + Zustand State                  |
|  - Three.js 3D Visualizations                    |
|  - Recharts Analytics                            |
+--------------------------------------------------+
                                             |
                                             | REST API (Axios)
                                             v
+--------------------------------------------------+
|                  BACKEND (FastAPI)               |
|  +--------------------------------------------+  |
|  |              API Layer                     |  |
|  |  - Routes: /uploads, /chat, /analytics,   |  |
|  |            /graph                          |  |
|  |  - Middleware: CORS, Rate Limit, Error    |  |
|  +--------------------------------------------+  |
|  |            Service Layer                   |  |
|  |  - Ingest Service (PST Parsing)           |  |
|  |  - Index Service (Vector Embedding)       |  |
|  |  - Chat Graph (LangGraph Router)          |  |
|  |  - Insights Processor                     |  |
|  |  - Analytics Service                      |  |
|  |  - Graph RAG Service                      |  |
|  +--------------------------------------------+  |
+--------------------------------------------------+
          |              |              |
          v              v              v
   +----------+   +----------+   +------------+
   | Pinecone |   |  Redis   |   | PostgreSQL |
   | (Vectors)|   | (Cache)  |   | (Metadata) |
   +----------+   +----------+   +------------+
          |
          v
   +-------------------+
   |   FAISS (Local)   |
   |  (Graph Vectors)  |
   +-------------------+
```

---

## 2. Technology Stack

### 2.1 Frontend Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | Next.js | 14.0.4 | Full-stack React framework with App Router |
| **UI Library** | React | 18.2.0 | Component-based UI |
| **Language** | TypeScript | 5.3.3 | Type-safe JavaScript |
| **Styling** | Tailwind CSS | 3.4.0 | Utility-first CSS |
| **State Management** | Zustand | 4.4.7 | Lightweight global state |
| **API Client** | Axios | 1.6.2 | HTTP client |
| **Data Fetching** | TanStack React Query | 5.14.2 | Server state management |
| **Forms** | React Hook Form | 7.49.2 | Form handling |
| **Validation** | Zod | 3.22.4 | Schema validation |
| **Charts** | Recharts | 2.10.3 | Data visualization |
| **3D Graphics** | Three.js / React Three Fiber | 0.160.0 / 8.15.12 | 3D visualizations |
| **Icons** | Lucide React | 0.298.0 | Icon library |
| **Date Utils** | date-fns | 3.0.6 | Date manipulation |

### 2.2 Backend Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | 0.104.0+ | Async REST API |
| **Runtime** | Python | 3.11 | Core language |
| **Server** | Uvicorn | 0.24.0+ | ASGI server |
| **Validation** | Pydantic | 2.5.0 | Data validation |
| **Settings** | Pydantic Settings | 2.1.0 | Configuration management |
| **ORM** | SQLAlchemy | 2.0.23+ | Database abstraction |
| **Migrations** | Alembic | 1.12.1 | Schema migrations |
| **Background Tasks** | Celery | 5.3.0 | Async task queue |
| **Logging** | Loguru | 0.7.0 | Structured logging |
| **HTTP Client** | HTTPX | 0.25.0 | Async HTTP |

### 2.3 AI/ML Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **LLM Framework** | LangChain | 0.1.0+ | LLM orchestration |
| **Workflow Engine** | LangGraph | 0.0.20+ | State machine for chat routing |
| **Anthropic SDK** | langchain-anthropic | 0.1.0 | Claude integration |
| **Google SDK** | langchain-google-genai | 0.0.9 | Gemini integration |
| **Embeddings** | sentence-transformers | 2.2.0 | Local embedding models |
| **Vector DB** | Pinecone | 3.0.0+ | Cloud vector storage |
| **Local Vectors** | FAISS | 1.7.4+ | Fast similarity search |
| **Graph Engine** | NetworkX | 3.0+ | Knowledge graph |
| **NLP** | spaCy | 3.7.0 | Named entity recognition |
| **NLP** | NLTK | 3.8.0 | Text processing |
| **Deep Learning** | PyTorch | 2.0.0+ | GPU acceleration |
| **ML Utils** | scikit-learn | 1.3.0 | Similarity computation |

### 2.4 Infrastructure

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Database** | PostgreSQL | 15 (Alpine) | Relational data |
| **Cache** | Redis | 7 (Alpine) | Caching & rate limiting |
| **File Parser** | Apache Tika | Latest | PST/document extraction |
| **PST Tools** | pst-utils | System | Native PST extraction |
| **Containerization** | Docker Compose | Latest | Multi-container orchestration |
| **GPU Runtime** | NVIDIA Docker | Latest | CUDA support |

---

## 3. Architecture Diagram

### 3.1 Request Flow Architecture

```
                           +-----------------------+
                           |       User Query      |
                           +-----------+-----------+
                                       |
                                       v
                           +-----------+-----------+
                           |    Next.js Frontend   |
                           |  (React + TypeScript) |
                           +-----------+-----------+
                                       |
                                       | POST /api/chat/router
                                       v
+------------------------------------------------------------------------------+
|                              FastAPI Backend                                  |
|  +------------------------------------------------------------------------+  |
|  |                          Middleware Stack                              |  |
|  |  CORS -> Rate Limiter -> Request ID -> Error Handler -> GZip          |  |
|  +------------------------------------------------------------------------+  |
|                                       |                                      |
|                                       v                                      |
|  +------------------------------------------------------------------------+  |
|  |                         Chat Router Endpoint                           |  |
|  |                    (api/routes/chat.py:router_chat)                    |  |
|  +------------------------------------------------------------------------+  |
|                                       |                                      |
|                    +------------------+------------------+                    |
|                    |                                     |                   |
|                    v                                     v                   |
|  +--------------------------------+    +--------------------------------+    |
|  |     LangGraph Chat Router      |    |      Graph RAG Service         |    |
|  |   (graph/chat_graph.py)        |    | (services/graph_rag/service.py)|    |
|  +--------------------------------+    +--------------------------------+    |
|           |                                       |                          |
|           v                                       v                          |
|  +----------------+                    +---------------------+               |
|  | classify_intent|                    | GraphQueryEngine    |               |
|  +----------------+                    +---------------------+               |
|           |                                       |                          |
|     +-----+-----+                          +------+------+                   |
|     |           |                          |             |                   |
|     v           v                          v             v                   |
| +-------+  +--------+              +----------+  +-------------+            |
| |Content|  |Insights|              |  FAISS   |  | NetworkX    |            |
| |  RAG  |  |  RAG   |              | Search   |  | Traversal   |            |
| +-------+  +--------+              +----------+  +-------------+            |
|     |           |                          |             |                   |
|     v           v                          +------+------+                   |
| +------------------+                              |                          |
| | Pinecone Search  |                              v                          |
| +------------------+                    +--------------------+               |
|           |                             | generate_answer()  |               |
|           v                             +--------------------+               |
| +------------------+                              |                          |
| |generate_response |                              |                          |
| +------------------+                              |                          |
|           |                                       |                          |
|           +-------------------+-------------------+                          |
|                               |                                              |
|                               v                                              |
|                    +--------------------+                                    |
|                    |   LLM Invocation   |                                    |
|                    | (Claude / Gemini)  |                                    |
|                    +--------------------+                                    |
|                               |                                              |
+------------------------------------------------------------------------------+
                                |
                                v
                    +--------------------+
                    |   JSON Response    |
                    | {content, sources} |
                    +--------------------+
```

### 3.2 Data Processing Pipeline

```
+-------------+     +----------------+     +------------------+
|  PST File   | --> | Ingest Service | --> | Extracted JSON   |
| (Outlook)   |     | (readpst/Tika) |     | (emails array)   |
+-------------+     +----------------+     +------------------+
                                                   |
                           +-----------------------+
                           |
            +--------------+----------------+
            |                               |
            v                               v
+------------------------+    +------------------------+
|    Index Service       |    |   Insights Processor   |
| (Vector Embeddings)    |    |   (LLM Analysis)       |
+------------------------+    +------------------------+
            |                               |
            v                               v
+------------------------+    +------------------------+
|   Pinecone Index       |    |   Insights JSON        |
| (Cloud Vector Store)   |    | (Coaching Data)        |
+------------------------+    +------------------------+
            |
            v
+------------------------+
|   Graph RAG Builder    |
| (Optional, On-Demand)  |
+------------------------+
            |
    +-------+-------+
    |               |
    v               v
+----------+  +----------+
|  FAISS   |  | NetworkX |
| (Vectors)|  |  (Graph) |
+----------+  +----------+
```

---

## 4. Backend Architecture

### 4.1 Directory Structure

```
backend/
├── api/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── middleware/
│   │   ├── error_handler.py       # Global exception handling
│   │   ├── rate_limiter.py        # Request rate limiting
│   │   └── request_id.py          # Request tracing
│   └── routes/
│       ├── analytics.py           # Visualization data endpoints
│       ├── chat.py                # Chat/RAG endpoints
│       ├── graph_rag.py           # Graph RAG endpoints
│       └── uploads.py             # File upload endpoints
├── core/
│   ├── config.py                  # Pydantic settings
│   └── logging.py                 # Loguru configuration
├── graph/
│   └── chat_graph.py              # LangGraph state machine
├── models/
│   └── base.py                    # SQLAlchemy models
├── services/
│   ├── analytics/
│   │   └── analytics_service.py   # Timeline, wordcloud, network
│   ├── cache/
│   │   └── redis_service.py       # Redis caching utilities
│   ├── graph_rag/
│   │   ├── knowledge_graph.py     # NetworkX graph builder
│   │   ├── models.py              # Pydantic schemas
│   │   ├── query_engine.py        # Graph traversal engine
│   │   └── service.py             # Graph RAG orchestration
│   ├── index/
│   │   └── service.py             # Vector embedding service
│   ├── ingest/
│   │   └── service.py             # PST parsing service
│   └── insights/
│       └── processor.py           # AI coaching insights
├── data/                          # Local file storage
│   ├── uploads/                   # Raw PST files
│   ├── extracted/                 # Parsed email JSON
│   ├── insights/                  # Generated insights
│   └── graphs/                    # Persisted graph data
├── requirements.txt
├── Dockerfile
└── .env                           # Environment config
```

### 4.2 FastAPI Application Structure

**Entry Point** (`api/main.py`):

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI(
    title="PST Coach",
    version="1.0.0",
    description="Email Intelligence & Self-Reflection Platform",
    lifespan=lifespan,  # Handles Redis connection lifecycle
)

# Middleware stack (order matters - CORS must be last to execute first)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(CORSMiddleware, ...)

# Route registration
app.include_router(uploads.router, prefix="/api/uploads")
app.include_router(chat.router, prefix="/api/chat")
app.include_router(analytics.router, prefix="/api/analytics")
app.include_router(graph_rag.router, prefix="/api/graph")
```

### 4.3 Configuration System

**Settings** (`core/config.py`):

```python
class Settings(BaseSettings):
    # Application
    APP_NAME: str = "PST Coach"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://..."

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 300       # 5 min default
    CACHE_LLM_TTL_SECONDS: int = 3600  # 1 hour for LLM
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # Vector Database
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "pst-coach"

    # LLM Configuration
    LLM_PROVIDER: str = "google"       # or "anthropic"
    LLM_MODEL: str = "gemini-3-flash-preview"
    LLM_MAX_RPM: int = 15              # Rate limit
    LLM_MAX_RETRIES: int = 3

    # Embeddings
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    EMBEDDING_DIMENSION: int = 384

    # Processing
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    model_config = SettingsConfigDict(env_file=".env")
```

---

## 5. Frontend Architecture

### 5.1 Directory Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx             # Root layout
│   │   ├── page.tsx               # Landing page
│   │   ├── providers.tsx          # React Query provider
│   │   ├── chat/
│   │   │   └── page.tsx           # Main chat interface
│   │   ├── dashboard/
│   │   │   └── page.tsx           # Analytics dashboard
│   │   └── upload/
│   │       └── page.tsx           # File upload page
│   ├── components/
│   │   ├── scene/
│   │   │   └── BackgroundScene.tsx  # Three.js background
│   │   ├── ui/
│   │   │   ├── LiquidButton.tsx
│   │   │   └── LiquidCard.tsx
│   │   └── visualizations/
│   │       ├── GraphRAGPanel.tsx    # Knowledge graph UI
│   │       ├── NetworkGraph.tsx     # Contact network
│   │       ├── Timeline.tsx         # Activity timeline
│   │       ├── VisualizationPanel.tsx
│   │       └── WordCloud.tsx        # Topic cloud
│   └── lib/
│       └── api.ts                   # Axios client
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── Dockerfile
```

### 5.2 Chat Interface Modes

The chat interface (`chat/page.tsx`) supports four modes:

| Mode | Backend API | RAG Type | Description |
|------|-------------|----------|-------------|
| **Ask Inbox** | `/api/chat/router` + `mode=content` | Content RAG | Factual email search |
| **Coach Me** | `/api/chat/router` + `mode=insights` | Insights RAG | Behavioral coaching |
| **Explore** | `/api/analytics/*` | N/A | Visual analytics |
| **Graph** | `/api/chat/router` + `mode=graph` | Graph RAG | Knowledge graph queries |

### 5.3 State Management

**Zustand Store Pattern:**

```typescript
// Example: Chat state
const [messages, setMessages] = useState<Message[]>([])
const [activeMode, setActiveMode] = useState<'ask' | 'coach' | 'explore' | 'graph'>('coach')
const [uploadId, setUploadId] = useState<string | null>(null)
```

**React Query for API Calls:**

```typescript
const { data, isLoading } = useQuery({
  queryKey: ['uploads'],
  queryFn: () => api.get('/api/uploads/')
})
```

---

## 6. Data Flow Pipelines

### 6.1 Upload & Extraction Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          UPLOAD & EXTRACTION PIPELINE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. USER UPLOAD                                                             │
│     ┌──────────────┐                                                        │
│     │ PST File     │ ─────> POST /api/uploads/ (multipart/form-data)        │
│     │ (Outlook)    │                                                        │
│     └──────────────┘                                                        │
│            │                                                                │
│            v                                                                │
│  2. DEDUPLICATION CHECK                                                     │
│     ┌──────────────────────────────────────────────────────────────┐        │
│     │ MD5 Hash Computation                                         │        │
│     │ • Generate file hash: hashlib.md5(content).hexdigest()[:16]  │        │
│     │ • Check against existing uploads in data/extracted/          │        │
│     │ • Return existing upload_id if duplicate                     │        │
│     └──────────────────────────────────────────────────────────────┘        │
│            │                                                                │
│            v                                                                │
│  3. FILE STORAGE                                                            │
│     ┌──────────────────────────────────────────────────────────────┐        │
│     │ Save to: data/uploads/{upload_id}.pst                        │        │
│     │ upload_id format: {file_hash}-{uuid[:8]}                     │        │
│     └──────────────────────────────────────────────────────────────┘        │
│            │                                                                │
│            v                                                                │
│  4. BACKGROUND PROCESSING (process_pst_file)                                │
│     ┌──────────────────────────────────────────────────────────────┐        │
│     │ Primary: readpst -e -o {extract_dir} {file_path}             │        │
│     │ • Extracts individual .eml files                             │        │
│     │ • Timeout: 3600s (1 hour)                                    │        │
│     │                                                              │        │
│     │ Fallback 1: Apache Tika                                      │        │
│     │ • HTTP API: tika.parser.from_file()                          │        │
│     │ • Returns raw text blob                                      │        │
│     │                                                              │        │
│     │ Fallback 2: Blob Regex Parsing                               │        │
│     │ • Pattern: From: ... Sent: ... To: ... Subject: ...          │        │
│     │ • Splits by email headers                                    │        │
│     └──────────────────────────────────────────────────────────────┘        │
│            │                                                                │
│            v                                                                │
│  5. EMAIL PARSING (parse_eml_file)                                          │
│     ┌──────────────────────────────────────────────────────────────┐        │
│     │ For each .eml file:                                          │        │
│     │ • BytesParser with email.policy.default                      │        │
│     │ • Extract: Subject, From, To, Cc, Date, Body                 │        │
│     │ • Body preference: plain text > HTML (stripped)              │        │
│     │ • Generate email_id: MD5(from + subject + body[:100])        │        │
│     └──────────────────────────────────────────────────────────────┘        │
│            │                                                                │
│            v                                                                │
│  6. JSON OUTPUT                                                             │
│     ┌──────────────────────────────────────────────────────────────┐        │
│     │ Save to: data/extracted/{upload_id}.json                     │        │
│     │                                                              │        │
│     │ Schema:                                                      │        │
│     │ [                                                            │        │
│     │   {                                                          │        │
│     │     "subject": "Project Update",                             │        │
│     │     "from": "john@example.com",                              │        │
│     │     "to": "team@example.com",                                │        │
│     │     "cc": "",                                                │        │
│     │     "date": "Monday, September 9, 2024 9:22 AM",             │        │
│     │     "body": "Email content...",                              │        │
│     │     "email_id": "abc123def456..."                            │        │
│     │   },                                                         │        │
│     │   ...                                                        │        │
│     │ ]                                                            │        │
│     └──────────────────────────────────────────────────────────────┘        │
│            │                                                                │
│            v                                                                │
│  7. TRIGGER INDEXING                                                        │
│     └──────> services/index/service.py:index_messages()                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Indexing Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             INDEXING PIPELINE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. LOAD EXTRACTED EMAILS                                                   │
│     ┌──────────────────────────────────────────────────────────────┐        │
│     │ Input: data/extracted/{upload_id}.json                       │        │
│     │ Check: indexed_uploads.json for duplicates                   │        │
│     └──────────────────────────────────────────────────────────────┘        │
│            │                                                                │
│            v                                                                │
│  2. TEXT PREPARATION                                                        │
│     ┌──────────────────────────────────────────────────────────────┐        │
│     │ For each email, create rich text:                            │        │
│     │                                                              │        │
│     │ full_text = f"""                                             │        │
│     │ Date: {date}                                                 │        │
│     │ From: {sender}                                               │        │
│     │ To: {recipient}                                              │        │
│     │ Subject: {subject}                                           │        │
│     │                                                              │        │
│     │ {body}                                                       │        │
│     │ """                                                          │        │
│     └──────────────────────────────────────────────────────────────┘        │
│            │                                                                │
│            v                                                                │
│  3. CHUNKING                                                                │
│     ┌──────────────────────────────────────────────────────────────┐        │
│     │ RecursiveCharacterTextSplitter                               │        │
│     │ • chunk_size: 500 characters                                 │        │
│     │ • chunk_overlap: 50 characters                               │        │
│     │ • Separators: ["\n\n", "\n", " ", ""]                         │        │
│     └──────────────────────────────────────────────────────────────┘        │
│            │                                                                │
│            v                                                                │
│  4. EMBEDDING GENERATION                                                    │
│     ┌──────────────────────────────────────────────────────────────┐        │
│     │ Model: HuggingFaceEmbeddings                                 │        │
│     │ • Model name: sentence-transformers/all-MiniLM-L6-v2         │        │
│     │ • Dimension: 384                                             │        │
│     │ • Device: CUDA if available, else CPU                        │        │
│     │ • Batch size: 64 (GPU) / 16 (CPU)                            │        │
│     │                                                              │        │
│     │ embedding = embeddings.embed_query(chunk)                    │        │
│     │ # Returns: [0.123, -0.456, ...] (384 floats)                 │        │
│     └──────────────────────────────────────────────────────────────┘        │
│            │                                                                │
│            v                                                                │
│  5. VECTOR CREATION                                                         │
│     ┌──────────────────────────────────────────────────────────────┐        │
│     │ Vector Schema:                                               │        │
│     │ {                                                            │        │
│     │   "id": "{upload_id}_{email_id}_{chunk_index}",              │        │
│     │   "values": [0.123, -0.456, ...],  // 384-dim                │        │
│     │   "metadata": {                                              │        │
│     │     "upload_id": "abc123-xyz",                               │        │
│     │     "email_id": "def456",                                    │        │
│     │     "date": "2024-09-09 09:22:00",                           │        │
│     │     "sender": "john@example.com",                            │        │
│     │     "to": "team@example.com",                                │        │
│     │     "subject": "Project Update",                             │        │
│     │     "text": "Chunk text..." (max 1000 chars),                │        │
│     │     "type": "email"                                          │        │
│     │   }                                                          │        │
│     │ }                                                            │        │
│     └──────────────────────────────────────────────────────────────┘        │
│            │                                                                │
│            v                                                                │
│  6. PINECONE UPSERT                                                         │
│     ┌──────────────────────────────────────────────────────────────┐        │
│     │ index.upsert(vectors=batch)                                  │        │
│     │ • Batch size: 100 vectors                                    │        │
│     │ • Index: "pst-coach"                                         │        │
│     │ • Metric: cosine similarity                                  │        │
│     │ • Spec: Serverless (AWS us-east-1)                           │        │
│     └──────────────────────────────────────────────────────────────┘        │
│            │                                                                │
│            v                                                                │
│  7. TRACKING & INSIGHTS                                                     │
│     ┌──────────────────────────────────────────────────────────────┐        │
│     │ • Update: data/indexed_uploads.json                          │        │
│     │ • Trigger: insights/processor.py:generate_insights()         │        │
│     └──────────────────────────────────────────────────────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. RAG Implementation Deep Dive

### 7.1 Three RAG Modes Architecture

PST Coach implements a **Hybrid RAG** system with three specialized modes, orchestrated via LangGraph:

```
                           +------------------+
                           |   User Query     |
                           +--------+---------+
                                    |
                                    v
                        +-----------+-----------+
                        |   Intent Classifier   |
                        |   (Keyword Heuristic) |
                        +-----------+-----------+
                                    |
              +---------------------+---------------------+
              |                     |                     |
              v                     v                     v
    +-----------------+   +-----------------+   +-----------------+
    |   Content RAG   |   |  Insights RAG   |   |   Graph RAG     |
    |   (Factual)     |   |  (Reflective)   |   |   (Complex)     |
    +-----------------+   +-----------------+   +-----------------+
```

### 7.2 LangGraph State Machine

**State Definition** (`graph/chat_graph.py`):

```python
class ChatState(TypedDict):
    messages: list           # LangChain message history
    upload_id: str           # Active PST context
    intent: Literal["factual", "reflective", "unknown"]
    mode_used: str           # "content" | "insights" | "graph"
    context_str: str         # Retrieved context
    sources: list            # Citation metadata
    response: str            # Final LLM response
```

**Graph Structure:**

```python
workflow = StateGraph(ChatState)

# Nodes
workflow.add_node("classify", classify_intent)
workflow.add_node("content_rag", content_rag)
workflow.add_node("insights_rag", insights_rag)
workflow.add_node("generate", generate_response)

# Entry point
workflow.set_entry_point("classify")

# Conditional routing based on intent
workflow.add_conditional_edges(
    "classify",
    route_to_mode,
    {
        "content_rag": "content_rag",
        "insights_rag": "insights_rag"
    }
)

# All RAG modes flow to response generation
workflow.add_edge("content_rag", "generate")
workflow.add_edge("insights_rag", "generate")
workflow.add_edge("generate", END)
```

### 7.3 Content RAG (Ask Inbox)

**Purpose:** Factual queries about email content

**Flow:**
1. **Query Expansion** - LLM generates search term variations
2. **Vector Search** - Pinecone similarity search (k=10)
3. **Context Assembly** - Combine retrieved chunks
4. **Response Generation** - LLM answers with context

```python
def content_rag(state: ChatState) -> ChatState:
    # Query expansion
    expansion_prompt = f"""Extract key search terms from: {query}
    Include name variations, topics, dates..."""
    expanded_terms = llm.invoke(expansion_prompt)
    search_query = f"{query} {expanded_terms}"

    # Vector search
    results = vector_store.similarity_search(search_query, k=10)

    # Build context
    for doc in results:
        context_parts.append(f"""
        Date: {doc.metadata['date']}
        From: {doc.metadata['sender']}
        To: {doc.metadata['to']}
        Subject: {doc.metadata['subject']}
        Content: {doc.page_content}
        """)

    state["context_str"] = "\n\n---\n\n".join(context_parts)
    return state
```

### 7.4 Insights RAG (Coach Me)

**Purpose:** Behavioral pattern analysis and coaching

**Flow:**
1. **Load Pre-computed Insights** - From `insights/{upload_id}_insights.json`
2. **Optional Email Examples** - Pinecone search for supporting evidence
3. **Coaching Response** - LLM generates empathetic advice

```python
def insights_rag(state: ChatState) -> ChatState:
    # Load cached insights
    insights_path = f"data/insights/{upload_id}_insights.json"
    with open(insights_path) as f:
        insights_data = json.load(f)

    context = f"PRE-COMPUTED COACHING INSIGHTS:\n{json.dumps(insights_data)}"

    # Add supporting email examples
    results = vector_store.similarity_search(query, k=3)
    for doc in results:
        context += f"\n\nSUPPORTING EMAIL:\n{doc.page_content}"

    state["context_str"] = context
    return state
```

**Insights Generation** (`insights/processor.py`):

```python
INSIGHTS_SCHEMA = {
    "summary": "Executive summary of communication style",
    "behavioral_patterns": ["Pattern 1", "Pattern 2", ...],
    "coaching_tips": ["Tip 1", "Tip 2", ...],
    "mood_trends": "Description of tone/sentiment",
    "strengths": ["Strength 1", ...],
    "areas_for_improvement": ["Area 1", ...]
}
```

### 7.5 Intent Classification

**Keyword-Based Heuristic:**

```python
def classify_intent(state: ChatState) -> ChatState:
    query = state["messages"][-1].content.lower()

    reflective_keywords = [
        "pattern", "tendency", "usually", "work on",
        "improve", "coach", "insight", "behavior",
        "stress", "feeling", "tone"
    ]

    if any(kw in query for kw in reflective_keywords):
        state["intent"] = "reflective"
    else:
        state["intent"] = "factual"  # Default

    return state
```

---

## 8. Graph RAG System

### 8.1 Overview

Graph RAG enables **multi-hop reasoning** across email content by:
1. Building a knowledge graph from email chunks
2. Extracting concepts via NER
3. Computing semantic edges between related chunks
4. Traversing the graph to gather expanded context
5. Generating comprehensive answers from traversal results

### 8.2 Architecture Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            GRAPH RAG SYSTEM                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     GraphRAGService (service.py)                     │   │
│  │  • Orchestrates build/query operations                              │   │
│  │  • Manages GPU-accelerated embeddings                               │   │
│  │  • Rate-limited LLM wrapper                                         │   │
│  │  • Graph persistence (pickle + FAISS)                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                  ┌─────────────────┼─────────────────┐                     │
│                  │                 │                 │                     │
│                  v                 v                 v                     │
│  ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐        │
│  │  KnowledgeGraph   │ │  GraphQueryEngine │ │    FAISS Store    │        │
│  │ (knowledge_graph) │ │  (query_engine)   │ │  (vectors)        │        │
│  │                   │ │                   │ │                   │        │
│  │ • NetworkX Graph  │ │ • Vector Search   │ │ • Local vectors   │        │
│  │ • Node: Chunks    │ │ • BFS Traversal   │ │ • Fast similarity │        │
│  │ • Edge: Similarity│ │ • Answer Gen      │ │                   │        │
│  │ • Concepts: NER   │ │                   │ │                   │        │
│  └───────────────────┘ └───────────────────┘ └───────────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.3 Knowledge Graph Builder

**Building Process** (`knowledge_graph.py`):

```python
class KnowledgeGraph:
    def __init__(self,
                 edges_threshold=0.8,      # Min similarity for edge
                 alpha=0.7,                # Similarity weight
                 beta=0.3,                 # Concept overlap weight
                 top_k_neighbors=10):      # Edges per node
        self.graph = nx.Graph()
        self.concept_cache = {}

    def build_graph(self, splits, llm, embedding_model):
        # Step 1: Add nodes (one per chunk)
        self._add_nodes(splits)

        # Step 2: Create embeddings (GPU accelerated)
        embeddings = self._create_embeddings(splits, embedding_model)

        # Step 3: Extract concepts via NER (spaCy)
        self._extract_concepts_ner(splits)

        # Step 4: Add edges (top-k neighbors)
        self._add_edges_topk(embeddings)
```

**Node Structure:**

```python
self.graph.add_node(
    node_id,
    content=chunk.page_content,      # Full chunk text
    metadata=chunk.metadata,         # Email metadata
    concepts=[]                      # Extracted entities
)
```

**Edge Computation (Top-K Sparse):**

```python
def _add_edges_topk(self, embeddings):
    """Scalable O(n*k) instead of O(n²)"""
    for batch_start in range(0, num_nodes, batch_size):
        batch_embeddings = embeddings[batch_start:batch_end]

        # Compute similarity between batch and ALL nodes
        similarities = cosine_similarity(batch_embeddings, embeddings)

        for node in batch:
            # Get top-k indices (excluding self)
            top_k = np.argpartition(similarities[node], -k-1)[-k-1:]

            for neighbor in top_k:
                if similarity > threshold:
                    weight = alpha * similarity + beta * concept_overlap
                    self.graph.add_edge(node, neighbor, weight=weight)
```

**Concept Extraction (NER):**

```python
def _extract_concepts_ner(self, splits):
    """Fast local NER without LLM calls"""
    nlp = spacy.load("en_core_web_sm")

    for split in splits:
        doc = nlp(split.page_content[:3000])
        entities = [
            ent.text for ent in doc.ents
            if ent.label_ in ["PERSON", "ORG", "GPE", "DATE", "EVENT"]
        ]
        self.graph.nodes[node_id]['concepts'] = entities
```

### 8.4 Query Engine

**Query Flow** (`query_engine.py`):

```python
def query(self, query: str, k: int = 5) -> GraphQueryResult:
    # Step 1: Vector search for starting nodes
    relevant_docs = self.vector_store.similarity_search(query, k=k)

    # Step 2: Graph traversal (Dijkstra-like)
    context, path, filtered, steps = self._expand_context(query, relevant_docs)

    # Step 3: Generate answer (ONLY LLM call)
    answer = self._generate_answer(query, context)

    return GraphQueryResult(
        answer=answer,
        traversal_path=path,
        traversal_steps=steps,
        sources=self._extract_sources(filtered)
    )
```

**Dijkstra-Like Traversal:**

```python
def _expand_context(self, query, relevant_docs):
    priority_queue = []  # (priority, node_id)
    visited = set()

    # Initialize with relevant document nodes
    for doc in relevant_docs:
        node = self._find_closest_node(doc)
        heapq.heappush(priority_queue, (1.0, node))

    while priority_queue and len(visited) < max_steps:
        priority, current = heapq.heappop(priority_queue)

        if current in visited:
            continue
        visited.add(current)

        # Add node content to context
        context += self.knowledge_graph.get_node_content(current)

        # Expand to neighbors
        for neighbor in self.knowledge_graph.get_neighbors(current):
            edge_weight = self.knowledge_graph.get_edge_data(current, neighbor)['weight']
            new_priority = priority + (1.0 / edge_weight)
            heapq.heappush(priority_queue, (new_priority, neighbor))

    return context, list(visited)
```

### 8.5 Graph Persistence

```python
# Pickle for NetworkX graph
graph_data = {
    "graph": self.knowledge_graph.graph,
    "concept_cache": self.knowledge_graph.concept_cache,
    "edges_threshold": self.knowledge_graph.edges_threshold
}
pickle.dump(graph_data, open(f"data/graphs/{upload_id}_graph.pkl", "wb"))

# FAISS for vector store
self.vector_store.save_local(f"data/graphs/{upload_id}_vectors")
```

---

## 9. Vector Database & Embeddings

### 9.1 Pinecone Configuration

**Index Specification:**

| Property | Value |
|----------|-------|
| Index Name | `pst-coach` |
| Dimension | 384 |
| Metric | Cosine Similarity |
| Cloud | AWS |
| Region | us-east-1 |
| Spec | Serverless |

**Vector Schema:**

```json
{
  "id": "{upload_id}_{email_id}_{chunk_index}",
  "values": [0.123, -0.456, ...],  // 384 floats
  "metadata": {
    "upload_id": "abc123-xyz",
    "email_id": "def456",
    "date": "2024-09-09 09:22:00",
    "sender": "john@example.com",
    "to": "team@example.com",
    "subject": "Project Update",
    "text": "Chunk text...",
    "type": "email"
  }
}
```

### 9.2 Embedding Model

**Primary Model:** `sentence-transformers/all-MiniLM-L6-v2`

| Property | Value |
|----------|-------|
| Provider | HuggingFace |
| Dimension | 384 |
| Max Tokens | 256 |
| Speed | Fast (distilled) |
| Quality | Good for semantic similarity |

**Initialization:**

```python
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cuda' if torch.cuda.is_available() else 'cpu'},
    encode_kwargs={
        'batch_size': 64,  # GPU optimized
        'normalize_embeddings': True
    }
)
```

### 9.3 FAISS (Local Graph Vectors)

Used by Graph RAG for local similarity search:

```python
from langchain_community.vectorstores import FAISS

# Create from documents
vector_store = FAISS.from_documents(splits, embedding_model)

# Query
results = vector_store.similarity_search(query, k=5)

# Persistence
vector_store.save_local("data/graphs/{upload_id}_vectors")
vector_store = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
```

---

## 10. LLM Integration

### 10.1 Supported Providers

| Provider | Model | Temperature | Context Window |
|----------|-------|-------------|----------------|
| **Google** | gemini-3-flash-preview | 0.3 | 1M tokens |
| **Anthropic** | claude-sonnet-4-5 | 0.3 | 200K tokens |
| **Ollama** | llama3.2:3b (local) | 0 | 8K tokens |

### 10.2 LLM Initialization

```python
# Configuration-based selection
if settings.LLM_PROVIDER == "google":
    llm = ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.3
    )
else:
    llm = ChatAnthropic(
        model=settings.LLM_MODEL,
        api_key=settings.ANTHROPIC_API_KEY,
        temperature=0.3
    )
```

### 10.3 Rate-Limited LLM Wrapper

```python
class RateLimiter:
    def __init__(self, max_rpm=15, max_retries=3, base_delay=1.0):
        self.max_rpm = max_rpm
        self.request_times = []
        self._lock = threading.Lock()

    def wait_for_rate_limit(self):
        with self._lock:
            now = time.time()
            self.request_times = [t for t in self.request_times if now - t < 60]

            if len(self.request_times) >= self.max_rpm:
                wait_time = 60 - (now - self.request_times[0])
                time.sleep(wait_time)

            self.request_times.append(time.time())

class RateLimitedLLM:
    def invoke(self, input, config=None):
        return self.rate_limiter.execute_with_retry(self.llm.invoke, input)
```

### 10.4 Response Format Handling

```python
def extract_text_content(content) -> str:
    """Handle different LLM response formats"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        # Gemini returns [{'type': 'text', 'text': '...'}]
        parts = []
        for item in content:
            if isinstance(item, dict) and 'text' in item:
                parts.append(item['text'])
        return ''.join(parts)
    return str(content)
```

---

## 11. Caching & Rate Limiting

### 11.1 Redis Service

**Connection Management:**

```python
class RedisService:
    async def connect(self):
        self._client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        await self._client.ping()

    async def disconnect(self):
        await self._client.close()
```

### 11.2 Cache Patterns

| Key Pattern | TTL | Purpose |
|-------------|-----|---------|
| `chat:{upload_id}:{query_hash}` | 1 hour | LLM responses |
| `analytics:timeline:{upload_id}` | 10 min | Timeline data |
| `analytics:wordcloud:{upload_id}` | 10 min | Word frequencies |
| `analytics:network:{upload_id}` | 10 min | Contact network |
| `ratelimit:{identifier}` | 60 sec | Rate limit counters |

### 11.3 Caching Operations

```python
async def get_cached(self, key: str) -> Optional[Any]:
    value = await self._client.get(key)
    return json.loads(value) if value else None

async def set_cached(self, key: str, value: Any, ttl_seconds: int):
    await self._client.setex(key, ttl_seconds, json.dumps(value))

async def invalidate_upload_cache(self, upload_id: str):
    await self.delete_cached(f"chat:{upload_id}:*")
    await self.delete_cached(f"analytics:*:{upload_id}")
```

### 11.4 Rate Limiting Middleware

```python
class RateLimiterMiddleware:
    async def __call__(self, request: Request, call_next):
        identifier = f"{request.client.host}:{request.url.path}"
        is_allowed, remaining = await redis_service.check_rate_limit(identifier)

        if not is_allowed:
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"}
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
```

---

## 12. API Reference

### 12.1 Upload Endpoints

#### POST `/api/uploads/`
Upload a PST file for processing.

**Request:**
```
Content-Type: multipart/form-data
Body: file (PST file)
```

**Response:**
```json
{
  "upload_id": "abc123-xyz",
  "status": "processing",
  "message": "File uploaded. Processing started in background."
}
```

#### GET `/api/uploads/`
List all uploads.

**Response:**
```json
{
  "uploads": [
    {
      "upload_id": "abc123-xyz",
      "email_count": 1500,
      "vector_count": 3200,
      "indexed_at": "2024-01-15T10:30:00",
      "status": "completed"
    }
  ],
  "total": 1
}
```

#### GET `/api/uploads/{upload_id}/status`
Get upload processing status.

### 12.2 Chat Endpoints

#### POST `/api/chat/router`
Main RAG query endpoint.

**Request:**
```json
{
  "messages": [
    {"role": "user", "content": "Show emails from John about budget"}
  ],
  "upload_id": "abc123-xyz",
  "mode": "auto"  // "auto" | "content" | "insights" | "graph"
}
```

**Response:**
```json
{
  "content": "I found 3 emails from John regarding budget...",
  "citations": [
    {
      "date": "2024-01-15",
      "sender": "john@example.com",
      "subject": "Q1 Budget Review"
    }
  ],
  "mode_used": "content"
}
```

### 12.3 Analytics Endpoints

#### GET `/api/analytics/timeline?upload_id={id}`
Email activity over time.

#### GET `/api/analytics/wordcloud?upload_id={id}&top_n=100`
Word frequency data.

#### GET `/api/analytics/network?upload_id={id}`
Contact relationship network.

### 12.4 Graph RAG Endpoints

#### POST `/api/graph/build`
Start knowledge graph construction.

**Request:**
```json
{
  "upload_id": "abc123-xyz",
  "max_emails": 0,    // 0 = no limit
  "max_chunks": 0     // 0 = no limit
}
```

#### POST `/api/graph/query`
Query the knowledge graph.

**Request:**
```json
{
  "upload_id": "abc123-xyz",
  "query": "How are Project X and Sarah connected?"
}
```

**Response:**
```json
{
  "answer": "Project X and Sarah are connected through...",
  "traversal_path": [0, 5, 12, 18],
  "traversal_steps": [
    {
      "step": 1,
      "node_id": 0,
      "content_preview": "Email about Project X...",
      "concepts": ["Project X", "Q1"]
    }
  ],
  "sources": [...]
}
```

#### GET `/api/graph/status/{upload_id}`
Check graph build progress.

---

## 13. Storage Architecture

### 13.1 Local File System

```
data/
├── uploads/                    # Original PST files
│   └── {upload_id}.pst
│
├── extracted/                  # Parsed emails (JSON)
│   └── {upload_id}.json
│   Schema: [{subject, from, to, cc, date, body, email_id}, ...]
│
├── insights/                   # AI-generated insights
│   └── {upload_id}_insights.json
│   Schema: {summary, behavioral_patterns, coaching_tips, ...}
│
├── graphs/                     # Knowledge graphs
│   ├── {upload_id}_graph.pkl   # NetworkX (pickled)
│   └── {upload_id}_vectors/    # FAISS index
│       ├── index.faiss
│       └── index.pkl
│
└── indexed_uploads.json        # Tracking file
    Schema: {upload_id: {vector_count, indexed_at}}
```

### 13.2 PostgreSQL Schema

Currently minimal (ready for extension):

```sql
-- Future: User accounts, upload metadata, audit logs
CREATE TABLE uploads (
    id UUID PRIMARY KEY,
    filename VARCHAR(255),
    file_hash VARCHAR(32),
    email_count INT,
    vector_count INT,
    status VARCHAR(50),
    created_at TIMESTAMP,
    indexed_at TIMESTAMP
);
```

### 13.3 Redis Data

```
# Cache entries
chat:{upload_id}:{query_hash} -> JSON response (TTL: 3600s)
analytics:timeline:{upload_id} -> JSON data (TTL: 600s)
analytics:wordcloud:{upload_id} -> JSON data (TTL: 600s)
analytics:network:{upload_id} -> JSON data (TTL: 600s)

# Rate limiting
ratelimit:{ip}:{path} -> Counter (TTL: 60s)
```

---

## 14. GPU Acceleration

### 14.1 CUDA Configuration

**Requirements:**
- NVIDIA GPU (Compute Capability 7.0+)
- CUDA Toolkit 12.1+
- cuDNN 8.x
- nvidia-docker runtime

**Docker Compose GPU Configuration:**

```yaml
backend:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

### 14.2 GPU-Accelerated Components

| Component | GPU Usage | Speedup |
|-----------|-----------|---------|
| Embedding Generation | HuggingFace on CUDA | 20-50x |
| FAISS Indexing | CPU (FAISS-CPU) | N/A |
| Graph Similarity | NumPy on CPU | N/A |

### 14.3 Device Detection

```python
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
batch_size = 64 if device == "cuda" else 16

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': device},
    encode_kwargs={'batch_size': batch_size}
)
```

---

## 15. Docker Infrastructure

### 15.1 Docker Compose Services

```yaml
services:
  # Database Services
  postgres:
    image: postgres:15-alpine
    ports: ["5433:5432"]
    healthcheck: pg_isready

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    healthcheck: redis-cli ping

  # File Processing
  tika:
    image: apache/tika:latest
    ports: ["9998:9998"]

  # Optional Vector Store
  qdrant:
    image: qdrant/qdrant:latest
    ports: ["6333:6333", "6334:6334"]

  # Application
  backend:
    build: ./backend
    ports: ["8000:8000"]
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  frontend:
    build: ./frontend
    ports: ["3000:3000"]
```

### 15.2 Backend Dockerfile

```dockerfile
FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ pst-utils curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

COPY . .

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 15.3 Network Configuration

```yaml
networks:
  default:
    name: pst-coach-network
```

All services communicate over the `pst-coach-network` bridge network.

---

## 16. Security Considerations

### 16.1 Data Privacy

- **Local Processing**: Emails parsed and stored locally
- **No External Transmission**: Only embeddings sent to Pinecone
- **User Isolation**: Upload IDs separate user data
- **Redaction Ready**: `DEFAULT_REDACTION_LEVEL` setting

### 16.2 API Security

- **CORS Configuration**: Restricted origins in production
- **Rate Limiting**: 60 req/min default
- **JWT Ready**: `SECRET_KEY`, `JWT_ALGORITHM` configured
- **HTTPS**: Recommended for production

### 16.3 Environment Variables

Sensitive configuration via `.env`:

```env
SECRET_KEY=your-secret-key
PINECONE_API_KEY=your-pinecone-key
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key
DATABASE_URL=postgresql://...
```

### 16.4 File Upload Security

- **Size Limit**: `MAX_PST_SIZE_MB=5000`
- **Hash Deduplication**: Prevents duplicate processing
- **Temporary Directory Cleanup**: After extraction

---

## Appendix A: Quick Start

```bash
# 1. Start infrastructure
docker-compose up -d postgres redis tika

# 2. Configure environment
cp backend/.env.example backend/.env
# Edit with your API keys

# 3. Install dependencies
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 4. Run backend
cd backend && uvicorn api.main:app --reload

# 5. Run frontend
cd frontend && npm run dev

# 6. Access
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/docs
```

---

## Appendix B: Performance Tuning

| Parameter | Default | Description |
|-----------|---------|-------------|
| `CHUNK_SIZE` | 500 | Smaller = more vectors, higher precision |
| `CHUNK_OVERLAP` | 50 | Higher = better context continuity |
| `top_k_neighbors` | 10 | Graph connectivity |
| `edges_threshold` | 0.75 | Min similarity for edges |
| `max_traversal_steps` | 10 | Graph query depth |
| `LLM_MAX_RPM` | 15 | API rate limit |

---

## Appendix C: Troubleshooting

### Common Issues

1. **Pinecone Index Not Found**
   - Check `PINECONE_API_KEY` and `PINECONE_INDEX_NAME`
   - Index auto-created on first upload

2. **CUDA Not Detected**
   - Verify nvidia-docker: `docker run --gpus all nvidia/cuda:12.0-base nvidia-smi`
   - Falls back to CPU automatically

3. **PST Parsing Fails**
   - Install pst-utils: `apt-get install pst-utils`
   - Falls back to Tika automatically

4. **Rate Limit Errors**
   - Reduce `LLM_MAX_RPM` or wait 60 seconds
   - Check API quotas

---

*Last Updated: January 2025*
*Version: 1.0.0*
