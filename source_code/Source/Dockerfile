# ==============================================================================
# Backend Dockerfile: FastAPI + LangGraph Agentic Engine
# ==============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install system utilities & build dependencies for psycopg2 and numpy
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . /app

# Expose FastAPI port
EXPOSE 8000

# Default health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8000/docs || exit 1

# Start FastAPI server via Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
