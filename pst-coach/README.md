# PST Coach

An AI-powered email intelligence platform that analyzes your Outlook PST files to provide personalized communication coaching and insights.

## Features

- **📧 PST File Processing**: Upload Outlook PST files for analysis
- **🔍 Hybrid RAG Engine**: Combines **Vector Search** (for facts) and **Graph RAG** (for behavioral patterns)
- **🎯 Coach Me**: Get personalized coaching insights about your communication patterns
- **🧠 AI-Powered**: Uses Claude Sonnet / Gemini for intelligent analysis
- **🚀 GPU Accelerated**: Local CUDA-powered embedding generation for high performance
- **📊 Pattern Analysis**: Identifies behavioral patterns, mood trends, and areas for improvement

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI, Python 3.11 |
| **Frontend** | Next.js 14, React, TypeScript |
| **Vector RAG** | Pinecone (Cloud) |
| **Graph RAG** | NetworkX + FAISS (Local) |
| **LLM** | Claude Sonnet 4.5 / Gemini 2.0 Flash |
| **Embeddings** | HuggingFace (all-MiniLM-L6-v2) |
| **Acceleration** | NVIDIA CUDA (GPU) |
| **PST Parsing** | Apache Tika |
| **Orchestration** | LangGraph |
| **Container** | Docker Compose |

## Architecture: Hybrid RAG

This project uses a **Hybrid RAG (Retrieval Augmented Generation)** approach to solve different types of user queries:

### 1. Vector RAG (The "Search Engine")
- **Used for**: Specific factual queries (e.g., "What was the budget for Project X?", "Find emails from John about the deadline").
- **Technology**: **Pinecone**.
- **How it works**: Converts emails into mathematical vectors and finds the most similar documents based on keywords and semantic meaning.

### 2. Graph RAG (The "Detective")
- **Used for**: Complex behavioral questions (e.g., "How has my relationship with Sarah changed?", "What are my main communication bottlenecks?").
- **Technology**: **NetworkX** (Graph) + **FAISS** (Local Vectors).
- **How it works**: Builds a network of entities (People, Dates, Topics) and their relationships. It "hops" through the graph to connect distant pieces of information that vector search might miss.

---

## Hardware Acceleration (CUDA/GPU)

This application is optimized to run with **NVIDIA CUDA** acceleration to speed up the "Indexing" phase.

- **Why CUDA?**: The system needs to read thousands of emails and convert them into vector embeddings. Doing this on a CPU is slow.
- **Implementation**: The `docker-compose.yml` passes your host GPU to the backend container.
- **Result**: Embedding generation happens 20-50x faster, allowing you to index large PST files in minutes instead of hours.

---

## Quick Start

### Prerequisites

- Docker Desktop
- Pinecone API key (free tier works)
- Anthropic API key

### Setup

1. **Clone and configure**:
   ```bash
   cd pst-coach
   
   # Copy environment files
   cp backend/env.example backend/.env
   cp frontend/env.local.example frontend/.env.local
   
   # Edit backend/.env with your API keys:
   # PINECONE_API_KEY=your_key
   # ANTHROPIC_API_KEY=your_key
   ```

2. **Start the application**:
   ```bash
   docker-compose up -d
   ```

3. **Access the app**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs

### Usage

1. **Upload PST**: Go to `/upload` and drop your Outlook PST file
2. **Wait for Processing**: The system extracts emails, indexes them to Pinecone (Vector), and builds the Knowledge Graph.
3. **Chat**: Go to `/chat` and:
   - Use **"Ask Inbox"** to search your emails
   - Use **"Coach Me"** for personalized communication coaching

## Project Structure

```
pst-coach/
├── backend/                 # FastAPI backend
│   ├── api/                 # API routes and middleware
│   │   ├── routes/          # uploads.py, chat.py
│   │   └── middleware/      # error handling, request ID
│   ├── core/                # Configuration and logging
│   ├── graph/               # LangGraph chat workflow
│   ├── models/              # Database models (minimal)
│   └── services/            # Business logic
│       ├── ingest/          # PST parsing with Tika
│       ├── index/           # Pinecone indexing (Vector RAG)
│       ├── graph_rag/       # Graph RAG service
│       └── insights/        # AI insights generation
├── frontend/                # Next.js frontend
│   └── src/
│       ├── app/             # Pages (chat, upload, etc.)
│       ├── components/      # UI components
│       └── lib/             # API client
└── docker-compose.yml       # Container orchestration (with GPU support)
```

## Configuration

### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PINECONE_API_KEY` | Pinecone API key | Required |
| `ANTHROPIC_API_KEY` | Anthropic API key | Required |
| `LLM_MODEL` | Claude/Gemini model name | claude-sonnet-4-5 |
| `TIKA_SERVER_URL` | Tika server URL | http://tika:9998 |
| `DEBUG` | Enable debug mode | true |

### Frontend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | http://localhost:8000 |

## How It Works

1. **Upload**: PST file is uploaded and stored temporarily
2. **Parse**: Apache Tika extracts individual emails from the PST
3. **Index (Vector)**: Emails are embedded (via GPU) and stored in Pinecone for fast semantic search.
4. **Build (Graph)**: Entities and relationships are extracted to build a local Knowledge Graph for deep analysis.
5. **Insights**: AI analyzes email patterns and generates coaching insights
6. **Chat**: Users can query their emails via Hybrid RAG or get personalized coaching

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/uploads/` | POST | Upload PST file |
| `/api/uploads/` | GET | List all uploads |
| `/api/chat/router` | POST | Chat with RAG |
| `/health` | GET | Health check |

## Development

### Running locally without Docker

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn api.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Rebuilding containers

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Troubleshooting

**PST upload fails**: Ensure Tika container is running (`docker ps`)

**Chat returns errors**: Check API keys in `.env` file

**No insights generated**: Wait for indexing to complete (check backend logs)

```bash
docker logs pst-coach-backend --tail 50
```

## License

MIT
