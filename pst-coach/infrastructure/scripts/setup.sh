#!/bin/bash

# PST Coach Setup Script

set -e

echo "Setting up PST Coach development environment..."

# Check prerequisites
echo "Checking prerequisites..."
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose is required but not installed. Aborting." >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed. Aborting." >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js is required but not installed. Aborting." >&2; exit 1; }

# Create environment files
echo "Creating environment files..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "Created backend/.env - Please update with your settings"
fi

if [ ! -f frontend/.env.local ]; then
    cp frontend/.env.example frontend/.env.local
    echo "Created frontend/.env.local"
fi

# Create data directories
echo "Creating data directories..."
mkdir -p data/raw data/extracted data/db data/vectordb logs

# Start infrastructure services
echo "Starting infrastructure services..."
docker-compose up -d postgres redis tika qdrant

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Run database migrations
echo "Running database migrations..."
cd backend
source venv/bin/activate
# alembic upgrade head  # Uncomment when migrations are created
cd ..

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update backend/.env with your API keys"
echo "2. Start the backend: cd backend && source venv/bin/activate && uvicorn api.main:app --reload"
echo "3. Start the workers: cd workers && celery -A tasks worker --loglevel=info"
echo "4. Start the frontend: cd frontend && npm run dev"
echo ""
echo "Access the application at http://localhost:3000"
