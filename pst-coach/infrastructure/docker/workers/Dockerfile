FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY workers/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy worker code and shared modules
COPY workers/ .
COPY shared/ /shared/

# Run Celery worker
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info", "--concurrency=2"]
