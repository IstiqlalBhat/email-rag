# PST Coach - Email Intelligence & Self-Reflection Platform

A SaaS platform that transforms your Outlook PST files into actionable insights about your communication patterns, workload, and professional habits.

## Features

### Core Capabilities
- **Ask My Inbox**: RAG-powered chat over your email history with source citations
- **Coach Me**: AI-driven insights and coaching based on your communication patterns
- **Privacy-First**: Local processing, redaction by default, one-click data deletion
- **Non-Clinical**: Focuses on behavior patterns, not medical diagnosis

### Insights Provided
- **Self-Reflection & Behavior Patterns**: Communication themes, follow-through analysis, overcommit signals
- **Communication Coaching**: Response patterns, clarity metrics, effective templates
- **Workload & Boundary Recommendations**: After-hours trends, email load analysis, boundary scripts
- **Mood/Tonality Trends**: Non-clinical tone analysis with actionable suggestions

## Architecture

### Tech Stack
- **Backend**: Python, FastAPI, LangChain, LangGraph
- **Frontend**: Next.js, TypeScript, Tailwind CSS
- **Database**: PostgreSQL (metadata, metrics), Pinecone (vector embeddings)
- **Parser**: Apache Tika (PST extraction)
- **Queue**: Redis + Celery
- **Storage**: S3-compatible object storage

### Project Structure
```
pst-coach/
├── backend/           # FastAPI application
│   ├── api/          # REST API routes
│   ├── core/         # Core configuration
│   ├── graph/        # LangGraph workflows
│   ├── services/     # Business logic
│   ├── models/       # Database models
│   └── schemas/      # Pydantic schemas
├── frontend/         # Next.js application
│   └── src/
│       ├── app/      # Next.js app router
│       ├── components/
│       └── lib/
├── workers/          # Background job workers
│   ├── parsers/      # PST parsing workers
│   ├── processors/   # Data processing
│   └── indexers/     # Vector indexing
├── shared/           # Shared code
├── infrastructure/   # Deployment configs
├── tests/           # Test suite
└── docs/            # Documentation
```

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Quick Start

1. **Clone and Setup**
```bash
git clone <repository-url>
cd pst-coach
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

4. **Start Services**
```bash
docker-compose up -d  # Starts Postgres, Redis, Tika, Qdrant
```

5. **Run Application**
```bash
# Terminal 1 - Backend
cd backend
uvicorn api.main:app --reload

# Terminal 2 - Workers
cd workers
celery -A tasks worker --loglevel=info

# Terminal 3 - Frontend
cd frontend
npm run dev
```

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Environment Variables
Copy `.env.example` to `.env` and configure:
- Database credentials
- Object storage settings
- LLM API keys
- Pinecone API key

## Deployment

See [deployment documentation](./docs/deployment/) for production setup guides.

## Security & Privacy

- All data encrypted at rest and in transit
- Multi-tenant isolation enforced at all layers
- Default redaction of personal information
- One-click data deletion
- No clinical diagnosis or profiling of others
- Audit logging for compliance

## License

[Your License Here]

## Support

For issues and questions, please open a GitHub issue or contact support@pstcoach.example.com
