# Start All Services with Docker Compose
Write-Host "Starting all PST Coach services..." -ForegroundColor Green

# Start all services
docker-compose up -d

Write-Host "`nServices starting..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Show status
docker-compose ps

Write-Host "`n==================================" -ForegroundColor Green
Write-Host "PST Coach is starting!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host "`nFrontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/api/docs" -ForegroundColor Cyan
Write-Host "`nView logs: docker-compose logs -f" -ForegroundColor Yellow
Write-Host "Stop services: docker-compose stop" -ForegroundColor Yellow
