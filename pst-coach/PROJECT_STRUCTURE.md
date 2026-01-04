# PST Coach - Complete Project Structure

## Directory Tree

```
pst-coach/
├── backend/                        # FastAPI Backend
│   ├── api/                       # REST API Layer
│   │   ├── routes/               # API Routes
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   ├── uploads.py       # PST upload endpoints
│   │   │   ├── jobs.py          # Job status endpoints
│   │   │   ├── mailboxes.py     # Mailbox & metrics endpoints
│   │   │   ├── chat.py          # Chat endpoints (Ask/Coach modes)
│   │   │   └── privacy.py       # Privacy & data control
│   │   ├── middleware/          # Custom middleware
│   │   │   ├── error_handler.py # Global error handling
│   │   │   ├── request_id.py    # Request tracing
│   │   │   └── tenant.py        # Multi-tenant isolation
│   │   └── main.py              # FastAPI application entry
│   ├── core/                    # Core configuration
│   │   ├── config.py            # Settings management
│   │   └── logging.py           # Logging setup
│   ├── graph/                   # LangGraph Workflows
│   │   ├── pipeline_graph.py    # PST processing pipeline
│   │   └── chat_graph.py        # Chat routing graph
│   ├── models/                  # SQLAlchemy Models
│   │   ├── base.py             # Base model
│   │   ├── tenant.py           # Tenant & User models
│   │   ├── mailbox.py          # Mailbox & Message models
│   │   ├── job.py              # Job & Upload models
│   │   ├── insights.py         # Metrics & Insights models
│   │   └── privacy.py          # Privacy settings models
│   ├── schemas/                # Pydantic Schemas
│   ├── services/               # Business Logic
│   │   ├── ingest/            # PST ingestion
│   │   ├── preprocess/        # Data cleaning
│   │   ├── index/             # Vector indexing
│   │   ├── insights/          # Metrics & insights
│   │   ├── chat/              # RAG chat logic
│   │   └── auth/              # Authentication
│   ├── utils/                 # Utility functions
│   ├── requirements.txt       # Python dependencies
│   └── .env.example          # Environment template
│
├── frontend/                   # Next.js Frontend
│   ├── src/
│   │   ├── app/               # Next.js App Router
│   │   │   ├── layout.tsx    # Root layout
│   │   │   ├── page.tsx      # Home page
│   │   │   ├── providers.tsx # React Query provider
│   │   │   └── globals.css   # Global styles
│   │   ├── components/        # React Components
│   │   │   ├── chat/         # Chat interface
│   │   │   ├── dashboard/    # Dashboard views
│   │   │   ├── upload/       # Upload UI
│   │   │   ├── settings/     # Settings pages
│   │   │   └── common/       # Shared components
│   │   ├── lib/              # Utilities
│   │   │   └── api.ts        # API client
│   │   ├── hooks/            # Custom React hooks
│   │   ├── types/            # TypeScript types
│   │   │   └── index.ts      # Shared types
│   │   └── styles/           # Additional styles
│   ├── public/               # Static assets
│   ├── package.json          # Node dependencies
│   ├── tsconfig.json         # TypeScript config
│   ├── next.config.js        # Next.js config
│   ├── tailwind.config.js    # Tailwind config
│   └── .env.example          # Environment template
│
├── workers/                   # Celery Workers
│   ├── parsers/              # PST parsing workers
│   ├── processors/           # Data processors
│   ├── indexers/             # Indexing workers
│   ├── tasks.py              # Celery tasks
│   └── requirements.txt      # Worker dependencies
│
├── shared/                    # Shared Code
│   ├── schemas/              # Shared data schemas
│   ├── types/                # Shared types
│   ├── constants/            # Constants
│   └── utils/                # Shared utilities
│
├── infrastructure/           # Deployment & DevOps
│   ├── docker/              # Dockerfiles
│   │   ├── api/            # Backend Dockerfile
│   │   ├── workers/        # Worker Dockerfile
│   │   ├── frontend/       # Frontend Dockerfile
│   │   └── postgres/       # PostgreSQL init scripts
│   ├── kubernetes/         # K8s manifests
│   ├── terraform/          # Infrastructure as Code
│   └── scripts/            # Deployment scripts
│       └── setup.sh        # Development setup
│
├── tests/                   # Test Suite
│   ├── unit/               # Unit tests
│   │   └── test_example.py
│   ├── integration/        # Integration tests
│   ├── e2e/               # End-to-end tests
│   ├── fixtures/          # Test fixtures
│   └── conftest.py        # Pytest configuration
│
├── docs/                   # Documentation
│   ├── architecture/      # Architecture docs
│   │   └── ARCHITECTURE.md
│   ├── api/              # API documentation
│   │   └── API_REFERENCE.md
│   ├── deployment/       # Deployment guides
│   └── user-guide/       # User documentation
│
├── data/                  # Data Storage (gitignored)
│   ├── raw/              # Uploaded PST files
│   ├── extracted/        # Extracted JSONL
│   ├── db/               # Local SQLite
│   └── vectordb/         # Local vector DB
│
├── .github/              # GitHub Configuration
│   └── workflows/        # CI/CD workflows
│
├── docker-compose.yml    # Local development services
├── Makefile             # Development commands
├── README.md            # Project overview
├── LICENSE              # License file
├── .gitignore          # Git ignore rules
├── .dockerignore       # Docker ignore rules
└── PROJECT_STRUCTURE.md # This file
```

## Key Files

### Configuration
- `backend/.env.example` - Backend environment variables template
- `frontend/.env.example` - Frontend environment variables template
- `backend/core/config.py` - Centralized settings management
- `docker-compose.yml` - Local development stack

### Entry Points
- `backend/api/main.py` - FastAPI application
- `frontend/src/app/page.tsx` - Next.js home page
- `workers/tasks.py` - Celery worker tasks

### Database
- `backend/models/*.py` - SQLAlchemy ORM models
- `infrastructure/docker/postgres/init.sql` - Database initialization

### Workflows
- `backend/graph/pipeline_graph.py` - PST processing pipeline (LangGraph)
- `backend/graph/chat_graph.py` - Chat routing logic (LangGraph)

### API Routes
- `backend/api/routes/auth.py` - Authentication
- `backend/api/routes/chat.py` - Chat modes (Ask/Coach)
- `backend/api/routes/uploads.py` - PST uploads
- `backend/api/routes/privacy.py` - Privacy controls

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Workflows**: LangChain + LangGraph
- **Database**: PostgreSQL
- **Vector DB**: Pinecone / Qdrant
- **Queue**: Redis + Celery
- **Storage**: S3-compatible

### Frontend
- **Framework**: Next.js 14 (React)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: Zustand + React Query
- **Charts**: Recharts

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose (dev) / Kubernetes (prod)
- **Parsing**: Apache Tika
- **Monitoring**: Prometheus + Sentry

## Development Workflow

1. **Setup**: `make setup` or `bash infrastructure/scripts/setup.sh`
2. **Start Services**: `make start` or `docker-compose up -d`
3. **Run Backend**: `cd backend && uvicorn api.main:app --reload`
4. **Run Workers**: `cd workers && celery -A tasks worker --loglevel=info`
5. **Run Frontend**: `cd frontend && npm run dev`
6. **Run Tests**: `make test`

## Deployment

See `docs/deployment/` for production deployment guides.

## Architecture Highlights

### Two-Index RAG Strategy
1. **Content Index**: Email chunks for factual queries
2. **Insights Index**: Derived artifacts for coaching queries

### Multi-Tenant Isolation
- Every DB record has `tenant_id`
- Separate vector DB namespaces per tenant
- Row-level security enforcement

### Privacy-First Design
- Default redaction of PII
- Configurable excerpt policies
- One-click data deletion
- No clinical diagnosis language

### Resumable Processing
- LangGraph checkpointing
- Job state persistence
- Graceful failure recovery

## Next Steps

1. Configure environment variables in `.env` files
2. Add LLM API keys (OpenAI/Anthropic)
3. Set up vector DB (Pinecone or local Qdrant)
4. Run database migrations (when created)
5. Start building!

For detailed documentation, see the `docs/` directory.
