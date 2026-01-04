# PST Coach

An AI-powered email intelligence platform that analyzes your Outlook PST files to provide personalized communication coaching and insights.

## Features

- **📧 PST File Processing**: Upload Outlook PST files for analysis
- **🔍 Ask Inbox**: Search your emails using natural language
- **🎯 Coach Me**: Get personalized coaching insights about your communication patterns
- **🧠 AI-Powered**: Uses Claude Sonnet for intelligent analysis
- **📊 Pattern Analysis**: Identifies behavioral patterns, mood trends, and areas for improvement
- **🔄 Smart Deduplication**: Automatically detects and skips duplicate PST uploads
- **⚡ Incremental Processing**: Redundancy checks prevent re-processing already indexed files

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI, Python 3.11 |
| **Frontend** | Next.js 14, React, TypeScript |
| **Vector DB** | Pinecone (Serverless) |
| **LLM** | Claude 3.5 Sonnet (Anthropic) |
| **Embeddings** | HuggingFace (all-MiniLM-L6-v2) |
| **PST Parsing** | Apache Tika |
| **Orchestration** | LangGraph |
| **Database** | PostgreSQL 15 |
| **Cache** | Redis 7 |
| **Container** | Docker Compose |

## Table of Contents

- [Quick Start (Docker)](#quick-start-docker)
- [Manual Setup (Without Docker)](#manual-setup-without-docker)
- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [API Reference](#api-endpoints)
- [Troubleshooting](#troubleshooting)

## Quick Start (Docker)

### Prerequisites

- **Docker Desktop** (Windows/Mac) or Docker Engine (Linux)
- **Pinecone API Key** - Sign up at [pinecone.io](https://www.pinecone.io/) (free tier available)
- **Anthropic API Key** - Get yours at [console.anthropic.com](https://console.anthropic.com/)

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd RAG-personal/pst-coach
   ```

2. **Configure environment variables**:
   ```bash
   # Backend configuration
   cp backend/env.example backend/.env

   # Frontend configuration
   cp frontend/env.local.example frontend/.env.local
   ```

3. **Edit `backend/.env` with your API keys**:
   ```bash
   # Required: Add your API keys
   PINECONE_API_KEY=your-pinecone-api-key-here
   ANTHROPIC_API_KEY=your-anthropic-api-key-here

   # Optional: Customize these if needed
   PINECONE_INDEX_NAME=pst-coach
   LLM_MODEL=claude-3-5-sonnet-20241022
   ```

4. **Start Docker Desktop** (Windows/Mac):
   - Launch Docker Desktop application
   - Wait for it to fully start (whale icon should be steady in system tray)

5. **Start all services**:
   ```bash
   docker-compose up -d
   ```

6. **Verify containers are running**:
   ```bash
   docker-compose ps
   ```

   You should see 6 containers running:
   - `pst-coach-frontend` - Next.js frontend (port 3001)
   - `pst-coach-backend` - FastAPI backend (port 8000)
   - `pst-coach-tika` - Apache Tika for PST parsing (port 9998)
   - `pst-coach-postgres` - PostgreSQL database (port 5433)
   - `pst-coach-redis` - Redis cache (port 6379)
   - `pst-coach-qdrant` - Qdrant vector DB (port 6333-6334, currently unused)

7. **Access the application**:
   - **Frontend UI**: http://localhost:3001
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

### First Time Usage

1. Navigate to http://localhost:3001/upload
2. Upload your Outlook PST file (supports files up to 5GB)
3. Wait for processing (check logs with `docker logs pst-coach-backend -f`)
4. Once complete, go to http://localhost:3001/chat
5. Try asking questions about your emails or request coaching insights

## Manual Setup (Without Docker)

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **Java 11+** (for Apache Tika)
- **PostgreSQL 15+**
- **Redis 7+**
- **Pinecone API Key**
- **Anthropic API Key**

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd pst-coach/backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup PostgreSQL**:
   ```bash
   # Create database
   createdb pst_coach

   # Or using psql:
   psql -U postgres
   CREATE DATABASE pst_coach;
   CREATE USER pstcoach WITH PASSWORD 'changeme123';
   GRANT ALL PRIVILEGES ON DATABASE pst_coach TO pstcoach;
   ```

5. **Start Redis** (in separate terminal):
   ```bash
   redis-server
   ```

6. **Download and start Apache Tika**:
   ```bash
   # Download Tika server
   wget https://dlcdn.apache.org/tika/3.0.0/tika-server-standard-3.0.0.jar

   # Start Tika server (in separate terminal)
   java -jar tika-server-standard-3.0.0.jar
   ```

7. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your settings:
   # - Update PINECONE_API_KEY and ANTHROPIC_API_KEY
   # - Update DATABASE_URL if needed
   # - Update TIKA_SERVER_URL=http://localhost:9998
   ```

8. **Create data directories**:
   ```bash
   mkdir -p data/uploads data/extracted data/insights
   ```

9. **Start the backend**:
   ```bash
   uvicorn api.main:app --reload --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory** (new terminal):
   ```bash
   cd pst-coach/frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment**:
   ```bash
   cp env.local.example .env.local
   # Edit .env.local:
   # NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Start the development server**:
   ```bash
   npm run dev
   ```

5. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000

### Manual Setup Summary

After completing these steps, you should have:
- ✅ PostgreSQL running on port 5432
- ✅ Redis running on port 6379
- ✅ Apache Tika running on port 9998
- ✅ FastAPI backend on port 8000
- ✅ Next.js frontend on port 3000

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
│       ├── index/           # Pinecone indexing
│       └── insights/        # AI insights generation
├── frontend/                # Next.js frontend
│   └── src/
│       ├── app/             # Pages (chat, upload, etc.)
│       ├── components/      # UI components
│       └── lib/             # API client
└── docker-compose.yml       # Container orchestration
```

## Configuration

### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PINECONE_API_KEY` | Pinecone API key | Required |
| `ANTHROPIC_API_KEY` | Anthropic API key | Required |
| `LLM_MODEL` | Claude model name | claude-sonnet-4-5 |
| `TIKA_SERVER_URL` | Tika server URL | http://tika:9998 |
| `DEBUG` | Enable debug mode | true |

### Frontend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | http://localhost:8000 |

## How It Works

PST Coach uses a multi-stage pipeline to transform your Outlook PST files into actionable insights:

### 1. Upload & Deduplication

**What happens:**
- User uploads a PST file via the frontend upload interface
- System calculates MD5 hash of the file content
- Checks against previously uploaded files to detect duplicates
- If duplicate detected, returns existing `upload_id` and skips processing
- If new, generates unique `upload_id` (format: `{file_hash}-{uuid}`)
- Saves PST file to `data/uploads/{upload_id}.pst`

**Files involved:**
- `backend/services/ingest/service.py:handle_upload()` - Main upload handler
- `backend/services/ingest/service.py:get_existing_upload_ids()` - Deduplication check

**Redundancy check:** MD5 hash comparison prevents duplicate uploads

### 2. PST Parsing with Apache Tika

**What happens:**
- Background task starts processing the PST file
- Checks if extraction already exists (redundancy check)
- Sends PST file to Apache Tika server for parsing
- Tika extracts raw text content from the PST container
- Parser identifies individual emails using header patterns:
  - `From:`, `Sent:`, `To:`, `Subject:` headers
  - Email body content
  - Metadata (dates, recipients)
- Each email gets unique `email_id` (MD5 hash of sender + subject + body snippet)
- Cleans email bodies (removes formatting, collapse whitespace)
- Saves extracted emails to `data/extracted/{upload_id}.json`

**Files involved:**
- `backend/services/ingest/service.py:process_pst_file()` - Main processing logic
- `backend/services/ingest/service.py:parse_emails_from_blob()` - Email parsing
- `backend/services/ingest/service.py:clean_body()` - Text cleaning

**Redundancy check:** Skips re-extraction if JSON file already exists

**Output format:**
```json
[
  {
    "email_id": "abc123...",
    "subject": "Project Update",
    "from": "john@example.com",
    "to": "team@example.com",
    "date": "2024-01-15 10:30:00",
    "body": "Email body text..."
  }
]
```

### 3. Vector Embedding & Indexing to Pinecone

**What happens:**
- Checks if upload is already indexed (redundancy check via `indexed_uploads.json`)
- Loads extracted emails from JSON file
- For each email:
  - Creates rich text representation with metadata (date, sender, subject, body)
  - Splits into chunks using RecursiveCharacterTextSplitter
    - Chunk size: 500 characters
    - Overlap: 50 characters
  - Generates embeddings using HuggingFace model (all-MiniLM-L6-v2, 384 dimensions)
  - Creates unique vector ID: `{upload_id}_{email_id}_{chunk_index}`
  - Prepares metadata for retrieval
- Upserts vectors to Pinecone in batches of 100
- Records total vector count in `data/indexed_uploads.json`

**Files involved:**
- `backend/services/index/service.py:index_messages()` - Main indexing logic
- `backend/services/index/service.py:ensure_pinecone_index()` - Index creation
- `backend/services/index/service.py:mark_upload_indexed()` - Track indexed uploads

**Redundancy check:** Skips re-indexing if already recorded in `indexed_uploads.json`

**Vector metadata structure:**
```json
{
  "upload_id": "abc123-xyz",
  "email_id": "def456",
  "date": "2024-01-15 10:30:00",
  "sender": "john@example.com",
  "subject": "Project Update",
  "text": "Chunk of email text...",
  "type": "email"
}
```

### 4. AI-Powered Insights Generation

**What happens:**
- Automatically triggered after indexing completes
- Loads extracted emails from JSON
- Identifies most frequent sender (assumes this is the user)
- Filters for emails FROM the user (to analyze their communication style)
- Takes sample of up to 50 emails
- Sends to Claude 3.5 Sonnet with coaching prompt
- Claude analyzes:
  - Communication patterns (responsiveness, tone, language habits)
  - Behavioral patterns (work hours, email volume)
  - Mood trends (emotional tone over time)
  - Strengths and areas for improvement
- Returns structured JSON with actionable insights
- Saves to `data/insights/{upload_id}_insights.json`

**Files involved:**
- `backend/services/insights/processor.py:generate_insights()` - Main insights logic

**Output format:**
```json
{
  "summary": "Executive summary of communication style...",
  "behavioral_patterns": ["Pattern 1", "Pattern 2"],
  "coaching_tips": ["Tip 1", "Tip 2"],
  "mood_trends": "Overall tone description...",
  "strengths": ["Strength 1", "Strength 2"],
  "areas_for_improvement": ["Area 1", "Area 2"]
}
```

### 5. Interactive Chat (RAG)

**What happens when user asks a question:**

**"Ask Inbox" mode (semantic search):**
- User types natural language query
- Query is embedded using same HuggingFace model
- Performs similarity search in Pinecone
- Retrieves top-k most relevant email chunks
- Sends context + query to Claude
- Claude generates answer based on retrieved emails
- Returns response with source attribution

**"Coach Me" mode (personalized insights):**
- Loads pre-generated insights from `data/insights/{upload_id}_insights.json`
- User can ask follow-up questions about their patterns
- Claude uses insights + email context to provide coaching
- Offers actionable advice and recommendations

**Files involved:**
- `backend/graph/workflow.py` - LangGraph chat orchestration
- `backend/api/routes/chat.py` - Chat API endpoint

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Upload Page  │  │  Chat Page   │  │  Insights Dashboard   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                  │                      │              │
└─────────┼──────────────────┼──────────────────────┼──────────────┘
          │                  │                      │
          │ HTTP             │ HTTP                 │ HTTP
          ▼                  ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                           │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────┐    │
│  │ Upload Routes │  │  Chat Routes  │  │  LangGraph Agent │    │
│  └───────┬───────┘  └───────┬───────┘  └────────┬─────────┘    │
│          │                   │                    │              │
│  ┌───────▼───────────────────▼────────────────────▼─────────┐   │
│  │              Service Layer                                │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │   │
│  │  │  Ingest  │  │  Index   │  │  Insights Processor  │   │   │
│  │  │ Service  │  │ Service  │  │      Service         │   │   │
│  │  └────┬─────┘  └────┬─────┘  └──────────┬───────────┘   │   │
│  └───────┼─────────────┼────────────────────┼───────────────┘   │
└──────────┼─────────────┼────────────────────┼───────────────────┘
           │             │                    │
           ▼             ▼                    ▼
    ┌──────────┐  ┌─────────────┐    ┌────────────────┐
    │  Tika    │  │  Pinecone   │    │    Claude API  │
    │  Server  │  │  (Vectors)  │    │   (Anthropic)  │
    └──────────┘  └─────────────┘    └────────────────┘
           │
           ▼
    ┌──────────┐  ┌─────────────┐    ┌────────────────┐
    │PostgreSQL│  │    Redis    │    │  HuggingFace   │
    │ Database │  │    Cache    │    │  (Embeddings)  │
    └──────────┘  └─────────────┘    └────────────────┘
```

### Data Flow

```
PST Upload → Tika Parsing → Email Extraction → Text Chunking
     ↓            ↓              ↓                  ↓
  storage/   raw text      JSON files         chunks
  uploads/                 extracted/

     → Embedding Generation → Vector Storage → Insights Analysis
            ↓                      ↓                 ↓
       HuggingFace            Pinecone          Claude API
       (384-dim)              (cosine)          (LLM)
            ↓                      ↓                 ↓
       embeddings              indexed           insights/
                                                 {id}_insights.json

User Query → Embedding → Similarity Search → Context Retrieval
     ↓           ↓              ↓                    ↓
  "Ask Inbox"  HuggingFace   Pinecone           Top-K chunks
     ↓           ↓              ↓                    ↓
  RAG Chain → Claude API → Generated Answer + Sources
```

### Component Responsibilities

| Component | Responsibility | Key Technologies |
|-----------|---------------|------------------|
| **Frontend** | User interface, file uploads, chat UI | Next.js, React, TypeScript, Tailwind |
| **Backend API** | REST endpoints, request handling, orchestration | FastAPI, Pydantic, Uvicorn |
| **Ingest Service** | PST parsing, email extraction, deduplication | Apache Tika, Python regex, hashlib |
| **Index Service** | Chunking, embedding, vector storage | LangChain, HuggingFace, Pinecone |
| **Insights Service** | AI analysis, coaching generation | LangChain, Claude API, prompt engineering |
| **Chat Service** | RAG pipeline, query handling | LangGraph, Pinecone, Claude API |
| **PostgreSQL** | Metadata storage (future use) | PostgreSQL 15 |
| **Redis** | Caching, session management (future use) | Redis 7 |
| **Pinecone** | Vector database for semantic search | Serverless index, cosine similarity |
| **Apache Tika** | Document parsing (PST files) | Tika Server 3.0 |

### Redundancy & Deduplication Mechanisms

The system implements multiple layers of redundancy checks to prevent duplicate processing:

1. **Upload Level** (`handle_upload()`):
   - MD5 hash comparison of file contents
   - Checks against `get_existing_upload_ids()`
   - Returns existing `upload_id` if duplicate found

2. **Extraction Level** (`process_pst_file()`):
   - Checks if `data/extracted/{upload_id}.json` exists
   - Skips Tika parsing if already extracted
   - Supports `force_reprocess` flag to override

3. **Indexing Level** (`index_messages()`):
   - Maintains `data/indexed_uploads.json` tracking file
   - Records `upload_id`, `vector_count`, and `indexed_at` timestamp
   - Skips re-indexing if already recorded
   - Supports `force_reindex` flag to override

4. **Email Level**:
   - Each email gets unique `email_id` via MD5 hash
   - Vector IDs format: `{upload_id}_{email_id}_{chunk_index}`
   - Prevents duplicate vectors even if re-indexed

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

### Common Issues

#### 1. Docker Containers Won't Start

**Symptom:** `docker-compose up -d` fails with connection errors

**Solutions:**
```bash
# Check if Docker Desktop is running
docker ps

# If not running, start Docker Desktop and wait for it to fully initialize

# Check for port conflicts
netstat -ano | findstr "8000"  # Windows
lsof -i :8000                  # Mac/Linux

# Restart Docker Compose
docker-compose down
docker-compose up -d
```

#### 2. PST Upload Fails

**Symptom:** Upload returns error or times out

**Possible causes:**
- Tika server not running or unhealthy
- PST file too large (>5GB default limit)
- Tika server crashed

**Solutions:**
```bash
# Check Tika container status
docker logs pst-coach-tika --tail 50

# Restart Tika if needed
docker-compose restart tika

# For large files, increase Tika timeout in backend/.env:
# (No specific setting exists yet, but Tika has 1 hour timeout by default)

# Check Tika is responding
curl http://localhost:9998/tika
```

#### 3. No Emails Extracted from PST

**Symptom:** Processing completes but `{upload_id}.json` has 0 or very few emails

**Possible causes:**
- PST file is encrypted or corrupted
- Email format not recognized by parser
- PST is empty or contains non-email items

**Solutions:**
```bash
# Check extracted JSON file
cat pst-coach/backend/data/extracted/{upload_id}.json

# Check backend logs for parsing warnings
docker logs pst-coach-backend | grep "email"

# Try opening PST in Outlook to verify it has emails
# Consider exporting PST again from Outlook if corrupted
```

#### 4. Indexing Fails or Vectors Not in Pinecone

**Symptom:** Extraction succeeds but search returns no results

**Possible causes:**
- Pinecone API key invalid or missing
- Pinecone index doesn't exist
- Network issues connecting to Pinecone
- Embedding model failed to load

**Solutions:**
```bash
# Check if index exists in Pinecone dashboard
# Or check backend logs
docker logs pst-coach-backend | grep -i pinecone

# Verify API key in backend/.env
echo $PINECONE_API_KEY  # Should not be empty

# Manually trigger re-indexing (future feature)
# For now, delete data/indexed_uploads.json and restart backend

# Check Pinecone index stats via API
curl http://localhost:8000/api/index/stats
```

#### 5. Chat Returns No Results or Errors

**Symptom:** Questions return "I don't have information" or error messages

**Possible causes:**
- No vectors indexed (check step 4)
- Anthropic API key missing/invalid
- Query embedding failed
- Pinecone connection issues

**Solutions:**
```bash
# Check Anthropic API key
grep ANTHROPIC_API_KEY pst-coach/backend/.env

# Check backend logs for errors
docker logs pst-coach-backend -f

# Test Claude API directly
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":100,"messages":[{"role":"user","content":"test"}]}'

# Verify vectors exist in Pinecone
# Check Pinecone dashboard or use API
```

#### 6. Insights Not Generated

**Symptom:** Upload and indexing complete but no insights file exists

**Possible causes:**
- Insights generation threw exception
- Claude API error
- Insufficient emails to analyze (<5 emails)

**Solutions:**
```bash
# Check if insights file exists
ls -la pst-coach/backend/data/insights/

# Check backend logs for insight errors
docker logs pst-coach-backend | grep -i insight

# Check extracted emails count
cat pst-coach/backend/data/extracted/{upload_id}.json | jq 'length'

# Manually trigger insights (future API endpoint)
```

#### 7. Frontend Can't Connect to Backend

**Symptom:** Frontend shows connection errors or 404s

**Possible causes:**
- Backend container not running
- CORS configuration issue
- Incorrect API URL in frontend config

**Solutions:**
```bash
# Check backend is running
docker ps | grep backend

# Check backend health
curl http://localhost:8000/health

# Verify frontend .env.local
cat pst-coach/frontend/.env.local
# Should have: NEXT_PUBLIC_API_URL=http://localhost:8000

# Check CORS settings in backend/.env
# Should include: CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Check frontend logs
docker logs pst-coach-frontend
```

#### 8. "Already Processed" Message on Upload

**Symptom:** Uploading PST shows "already processed" immediately

**Explanation:** This is **expected behavior** - the system detected you uploaded the same file before (via MD5 hash) and is reusing existing data

**If you want to force re-processing:**
```bash
# Option 1: Rename/modify the PST file (changes hash)

# Option 2: Manually delete existing data
rm pst-coach/backend/data/uploads/{upload_id}.pst
rm pst-coach/backend/data/extracted/{upload_id}.json

# Edit data/indexed_uploads.json and remove the entry
# Then re-upload

# Option 3: Future feature - Add force_reprocess API flag
```

### Viewing Logs

```bash
# All containers
docker-compose logs -f

# Specific container
docker logs pst-coach-backend -f
docker logs pst-coach-tika -f
docker logs pst-coach-frontend -f

# Filter logs
docker logs pst-coach-backend 2>&1 | grep ERROR
```

### Resetting Everything

```bash
# Stop all containers
docker-compose down

# Remove all data (WARNING: deletes uploads, extracts, insights)
rm -rf pst-coach/backend/data/*

# Remove volumes
docker-compose down -v

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

### Database Access

```bash
# Connect to PostgreSQL
docker exec -it pst-coach-postgres psql -U pstcoach -d pst_coach

# Connect to Redis
docker exec -it pst-coach-redis redis-cli

# Pinecone - Use dashboard at https://app.pinecone.io/
```

### Performance Tuning

For large PST files (>1GB):
- Increase Docker memory allocation (Docker Desktop → Settings → Resources)
- Monitor resource usage: `docker stats`
- Consider chunking upload or splitting PST files
- Adjust `CHUNK_SIZE` in `backend/.env` (default: 500)

## Development

### Running Tests

```bash
# Backend tests (if available)
cd pst-coach/backend
pytest

# Frontend tests (if available)
cd pst-coach/frontend
npm test
```

### Rebuilding Containers

```bash
# Rebuild after code changes
docker-compose down
docker-compose build
docker-compose up -d

# Rebuild specific service
docker-compose build backend
docker-compose up -d backend

# No-cache rebuild (slower but ensures clean build)
docker-compose build --no-cache
```

### Environment Variables Reference

See [Configuration](#configuration) section for complete list.

Key variables:
- `PINECONE_API_KEY` - Required for vector storage
- `ANTHROPIC_API_KEY` - Required for LLM
- `LLM_MODEL` - Claude model to use
- `CHUNK_SIZE` - Text chunk size for embeddings (default: 500)
- `MAX_PST_SIZE_MB` - Max upload size (default: 5000)

## Security Considerations

- Never commit `.env` files to git
- Rotate API keys regularly
- PST files may contain sensitive information - handle with care
- Use strong `SECRET_KEY` in production
- Enable HTTPS in production deployments
- Review and redact sensitive data before sharing insights

## Future Enhancements

- [ ] User authentication and multi-user support
- [ ] Email timeline visualization
- [ ] Export insights to PDF/CSV
- [ ] Advanced filtering (date ranges, senders, topics)
- [ ] Real-time processing status updates
- [ ] Support for other email formats (MBOX, EML)
- [ ] Sentiment analysis over time
- [ ] Email thread reconstruction
- [ ] API rate limiting and caching

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT

---
