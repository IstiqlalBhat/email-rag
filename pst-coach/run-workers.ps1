# Run Celery Workers
Write-Host "Starting PST Coach Workers..." -ForegroundColor Green

Set-Location workers

# Check if parent backend venv exists, otherwise try local
if (Test-Path "..\backend\venv\Scripts\Activate.ps1") {
    & ..\backend\venv\Scripts\Activate.ps1
} else {
    Write-Host "Virtual environment not found. Run setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Run Celery worker
celery -A tasks worker --loglevel=info --pool=solo
