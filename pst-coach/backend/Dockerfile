FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (needed for some python packages)
# libpst-dev provides readpst for parsing PST/OST files
RUN apt-get update && apt-get install -y gcc curl pst-utils && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create startup script that initializes DB then starts server
RUN echo '#!/bin/bash\npython init_db.py\nuvicorn api.main:app --host 0.0.0.0 --port 8000 --reload' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
