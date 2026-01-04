# Stop All Services
Write-Host "Stopping PST Coach services..." -ForegroundColor Yellow

docker-compose stop

Write-Host "All services stopped." -ForegroundColor Green
Write-Host "To remove containers and volumes: docker-compose down -v" -ForegroundColor Cyan
