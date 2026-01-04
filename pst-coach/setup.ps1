# PST Coach Setup Script for Windows
# PowerShell setup script

Write-Host "Setting up PST Coach development environment..." -ForegroundColor Green

# Check prerequisites
Write-Host "`nChecking prerequisites..." -ForegroundColor Yellow

$prerequisites = @{
    "docker" = "Docker"
    "python" = "Python 3"
    "node" = "Node.js"
}

$missing = @()
foreach ($cmd in $prerequisites.Keys) {
    if (!(Get-Command $cmd -ErrorAction SilentlyContinue)) {
        $missing += $prerequisites[$cmd]
    }
}

if ($missing.Count -gt 0) {
    Write-Host "Missing prerequisites: $($missing -join ', ')" -ForegroundColor Red
    Write-Host "Please install the missing software and try again." -ForegroundColor Red
    exit 1
}

Write-Host "All prerequisites found!" -ForegroundColor Green

# Create environment files
Write-Host "`nCreating environment files..." -ForegroundColor Yellow

if (!(Test-Path "backend\.env")) {
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "Created backend\.env - Please update with your settings" -ForegroundColor Cyan
}

if (!(Test-Path "frontend\.env.local")) {
    Copy-Item "frontend\.env.example" "frontend\.env.local"
    Write-Host "Created frontend\.env.local" -ForegroundColor Cyan
}

# Create data directories
Write-Host "`nCreating data directories..." -ForegroundColor Yellow
$dataDirs = @("data\raw", "data\extracted", "data\db", "data\vectordb", "logs")
foreach ($dir in $dataDirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "Data directories created" -ForegroundColor Green

# Start infrastructure services
Write-Host "`nStarting infrastructure services..." -ForegroundColor Yellow
docker-compose up -d postgres redis tika qdrant

# Wait for services
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Install backend dependencies
Write-Host "`nInstalling backend dependencies..." -ForegroundColor Yellow
Set-Location backend
if (!(Test-Path "venv")) {
    python -m venv venv
}
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Set-Location ..

# Install frontend dependencies
Write-Host "`nInstalling frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install
Set-Location ..

Write-Host "`n==================================" -ForegroundColor Green
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Update backend\.env with your API keys"
Write-Host "2. Start the backend:  .\run-backend.ps1"
Write-Host "3. Start the workers:  .\run-workers.ps1"
Write-Host "4. Start the frontend: .\run-frontend.ps1"
Write-Host "`nOr use docker-compose up to run everything:`n   docker-compose up -d"
Write-Host "`nAccess the application at http://localhost:3000" -ForegroundColor Yellow
