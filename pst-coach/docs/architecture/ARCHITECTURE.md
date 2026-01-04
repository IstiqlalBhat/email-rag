# PST Coach Architecture

## Overview

PST Coach is a multi-tenant SaaS platform that processes Outlook PST files to provide:
- RAG-powered chat over email history (Ask My Inbox)
- AI-driven insights and coaching (Coach Me)
- Privacy-first design with redaction and data control

## System Components

### 1. Frontend (Next.js)
- **Technology**: Next.js 14, TypeScript, Tailwind CSS
- **Responsibilities**:
  - User interface for upload, chat, dashboard, settings
  - File upload handling with multipart support
  - Real-time job progress tracking
  - Data visualization for insights

### 2. API Service (FastAPI)
- **Technology**: Python, FastAPI, Pydantic
- **Responsibilities**:
  - REST API endpoints for all operations
  - Authentication and authorization
  - Multi-tenant isolation
  - Request validation and error handling

### 3. Worker Service (Celery)
- **Technology**: Celery, Redis
- **Responsibilities**:
  - Async PST processing pipeline
  - Background jobs for metrics and insights
  - Scheduled tasks for cleanup and reports
  - Resumable job execution

### 4. LangGraph Workflows
- **Technology**: LangChain, LangGraph
- **Responsibilities**:
  - PST processing pipeline orchestration
  - Chat routing and RAG orchestration
  - Stateful workflow management
  - Checkpointing for resumability

### 5. Data Layer

#### PostgreSQL
- Tenant and user data
- Message metadata
- Metrics timeseries
- Insight artifacts
- Job state and checkpoints

#### Vector Database (Pinecone/Qdrant)
- Email chunk embeddings (Content Index)
- Insight artifact embeddings (Insights Index)
- Metadata filtering for retrieval

#### Object Storage (S3)
- Uploaded PST files
- Extracted JSONL data
- Optional attachment storage

## Data Flow

### Upload & Processing Pipeline
```
1. User uploads PST → Object Storage
2. API creates Upload record → enqueues job
3. Worker downloads PST → runs LangGraph pipeline:
   a. Parse (Tika) → JSONL
   b. Normalize & clean
   c. Thread reconstruction
   d. Chunk & embed → Vector DB (Content Index)
   e. Compute metrics → PostgreSQL
   f. Generate insight artifacts (LLM) → PostgreSQL
   g. Embed insights → Vector DB (Insights Index)
4. Job completes → user can chat & view insights
```

### Chat Interaction
```
1. User sends message → API
2. API invokes LangGraph chat_graph:
   a. Classify intent (factual vs reflective)
   b. Route to Content RAG or Insights RAG
   c. Retrieve context from appropriate index
   d. Apply guardrails (redaction, citations)
   e. Generate response with LLM
3. Return response with citations
```

## Two-Index Strategy

### Content Index
- **Purpose**: Answer "What did I say/receive about X?"
- **Contents**: Email body chunks with metadata
- **Metadata**: date, direction, folder, thread_id, contacts
- **Use case**: Factual queries, finding specific information

### Insights Index
- **Purpose**: Answer "What patterns do you see?"
- **Contents**: Derived insight artifacts and summaries
- **Metadata**: period, artifact_type, confidence
- **Use case**: Coaching queries, trend analysis

## Security & Privacy

### Multi-Tenancy
- Every record has `tenant_id`
- Vector DB namespaces per tenant
- Object storage keys prefixed by tenant
- Row-level security enforced in queries

### Privacy Controls
- Default redaction of names/emails
- Configurable excerpt display policy
- Retention period enforcement
- One-click data deletion

### Guardrails
- No clinical diagnosis language
- No profiling others
- Mandatory citations for factual claims
- Redaction enforcement

## Scalability Considerations

### Horizontal Scaling
- API: Stateless, scales with load balancer
- Workers: Scale worker pool size
- Database: Read replicas for queries
- Vector DB: Sharding by tenant

### Performance Optimizations
- Chunked/streaming PST parsing
- Batch embedding generation
- Result caching for common queries
- Progressive indexing (recent first)

## Deployment Architecture

### Development
- Docker Compose for all services
- Local Qdrant for vector DB
- Local file storage

### Production
- Kubernetes for orchestration
- Managed PostgreSQL (RDS/Cloud SQL)
- Managed Redis (ElastiCache)
- Pinecone or managed Qdrant
- S3/GCS for object storage
- CDN for frontend assets

## Monitoring & Observability

### Metrics
- Job completion rate and duration
- API latency (p50, p95, p99)
- Embedding/LLM token usage
- Vector search performance
- Error rates by endpoint

### Logging
- Structured JSON logs
- Request ID tracing
- PII redaction in logs
- Centralized log aggregation

### Alerting
- Job failure spikes
- API error rate thresholds
- Cost anomalies (LLM usage)
- Database connection pool exhaustion
