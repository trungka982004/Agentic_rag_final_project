# ==============================================================================
# Backend Dockerfile: Academic Studio IDE + FastAPI + LangGraph + Tectonic
# ==============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install system utilities, build tools, fontconfig & Tectonic compiler
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    libfontconfig1 \
    libgraphite2-3 \
    libharfbuzz0b \
    libicu72 \
    openssl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Download and install Tectonic standalone LaTeX compiler
RUN curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.tectonic-typesetting.net | sh \
    && mv tectonic /usr/local/bin/ \
    && tectonic --version

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
  CMD curl -f http://localhost:8000/api/health || exit 1

# Start FastAPI server via Uvicorn pointing to backend.main:app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
