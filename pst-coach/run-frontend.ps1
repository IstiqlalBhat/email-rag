# Run Frontend Development Server
Write-Host "Starting PST Coach Frontend..." -ForegroundColor Green

Set-Location frontend

# Check if node_modules exists
if (!(Test-Path "node_modules")) {
    Write-Host "Installing dependencies first..." -ForegroundColor Yellow
    npm install
}

# Run Next.js dev server
npm run dev
