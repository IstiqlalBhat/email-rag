.PHONY: help setup start stop clean test lint

help:
	@echo "PST Coach - Development Commands"
	@echo ""
	@echo "setup          - Initial project setup"
	@echo "start          - Start all services"
	@echo "stop           - Stop all services"
	@echo "clean          - Clean up containers and volumes"
	@echo "test           - Run tests"
	@echo "lint           - Run linters"
	@echo "migrate        - Run database migrations"
	@echo "logs           - View logs"

setup:
	@bash infrastructure/scripts/setup.sh

start:
	@docker-compose up -d
	@echo "Services started. Access at http://localhost:3000"

stop:
	@docker-compose stop

clean:
	@docker-compose down -v
	@rm -rf data/raw/* data/extracted/* data/db/* data/vectordb/*
	@echo "Cleaned up all containers and data"

test:
	@cd backend && pytest
	@cd frontend && npm test

lint:
	@cd backend && flake8 .
	@cd frontend && npm run lint

migrate:
	@cd backend && alembic upgrade head

logs:
	@docker-compose logs -f

.DEFAULT_GOAL := help
