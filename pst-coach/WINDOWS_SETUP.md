# PST Coach - Windows Setup Guide

## Prerequisites

Before you begin, install these tools:

1. **Python 3.11+**: [Download from python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Node.js 18+**: [Download from nodejs.org](https://nodejs.org/)

3. **Docker Desktop**: [Download from docker.com](https://www.docker.com/products/docker-desktop/)
   - Start Docker Desktop before running setup

4. **Git** (optional but recommended): [Download from git-scm.com](https://git-scm.com/download/win)

## Quick Start

### Option 1: Full Docker Setup (Easiest)

1. **Clone/Navigate to project**
```powershell
cd C:\CodeJaai\RAG-personal\pst-coach
```

2. **Configure environment**
```powershell
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env.local
# Edit backend\.env and add your API keys
```

3. **Start everything**
```powershell
.\start-all.ps1
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

5. **Stop services**
```powershell
.\stop-all.ps1
```

### Option 2: Development Setup (For Development)

1. **Run initial setup**
```powershell
.\setup.ps1
```

2. **Start infrastructure** (in one terminal)
```powershell
docker-compose up -d postgres redis tika qdrant
```

3. **Start backend** (in a new PowerShell window)
```powershell
.\run-backend.ps1
```

4. **Start workers** (in another PowerShell window)
```powershell
.\run-workers.ps1
```

5. **Start frontend** (in another PowerShell window)
```powershell
.\run-frontend.ps1
```

## Configuration

### Backend Configuration (backend\.env)

Required settings:
```env
SECRET_KEY=your-secret-key-at-least-32-characters-long
DATABASE_URL=postgresql://pstcoach:changeme123@localhost:5432/pst_coach
REDIS_URL=redis://localhost:6379/0

# LLM API Keys (choose one or both)
OPENAI_API_KEY=sk-your-openai-api-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# Vector Database (choose one)
# Option 1: Local Qdrant (default, no key needed)
QDRANT_URL=http://localhost:6333

# Option 2: Pinecone (for production)
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-west1-gcp
```

### Frontend Configuration (frontend\.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Troubleshooting

### Docker Desktop Not Running
```
Error: Cannot connect to Docker daemon
```
**Solution**: Start Docker Desktop and wait for it to fully start.

### Port Already in Use
```
Error: Port 3000/8000 is already allocated
```
**Solution**: Stop the service using the port or change the port in docker-compose.yml

### Python Virtual Environment Issues
```
Error: venv\Scripts\Activate.ps1 cannot be loaded
```
**Solution**: Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Node Modules Issues
```
Error: Cannot find module
```
**Solution**: Delete node_modules and reinstall:
```powershell
cd frontend
Remove-Item -Recurse -Force node_modules
npm install
```

### Database Connection Issues
```
Error: could not connect to server
```
**Solution**:
1. Check if PostgreSQL container is running: `docker-compose ps`
2. Restart PostgreSQL: `docker-compose restart postgres`
3. Wait 10 seconds and try again

## Common Commands

### Docker Commands
```powershell
# Start all services
docker-compose up -d

# Stop all services
docker-compose stop

# Remove containers and volumes
docker-compose down -v

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f api

# Restart a service
docker-compose restart api
```

### Development Commands
```powershell
# Backend tests
cd backend
.\venv\Scripts\Activate.ps1
pytest

# Frontend tests
cd frontend
npm test

# Type checking (frontend)
cd frontend
npm run type-check

# Linting
cd frontend
npm run lint
```

## Project Structure

```
pst-coach/
├── backend/           # Python FastAPI backend
├── frontend/          # Next.js frontend
├── workers/           # Celery background workers
├── infrastructure/    # Docker configs
├── setup.ps1         # Windows setup script
├── run-backend.ps1   # Start backend
├── run-workers.ps1   # Start workers
├── run-frontend.ps1  # Start frontend
├── start-all.ps1     # Start everything with Docker
└── stop-all.ps1      # Stop all services
```

## Next Steps

1. **Configure API Keys**: Edit `backend\.env` and add your LLM API keys
2. **Explore the API**: Visit http://localhost:8000/api/docs
3. **Start Development**:
   - Backend code is in `backend/`
   - Frontend code is in `frontend/src/`
   - Workers code is in `workers/`
4. **Read Documentation**: Check `docs/` folder for architecture and API docs

## Getting Help

- Architecture: See `docs/architecture/ARCHITECTURE.md`
- API Reference: See `docs/api/API_REFERENCE.md`
- Full Structure: See `PROJECT_STRUCTURE.md`

## Production Deployment

For production deployment, see `docs/deployment/` (to be created) or use the Kubernetes/Terraform configs in `infrastructure/`.
