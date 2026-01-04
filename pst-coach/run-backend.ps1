# Run Backend API Server
Write-Host "Starting PST Coach Backend API..." -ForegroundColor Green

Set-Location backend

# Activate virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Virtual environment not found. Run setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Run FastAPI server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
