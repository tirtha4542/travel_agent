# ==============================================================================
# TreapMate AI - Production Dockerfile
# Multi-Agent Autonomous Travel Planner (FastAPI + LangGraph)
# ==============================================================================

FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable immediate unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Set container working directory
WORKDIR /app

# Install minimal system utilities (curl for container healthcheck)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies without caching to keep image size small
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code and assets
COPY app/ ./app/
COPY templates/ ./templates/
COPY static/ ./static/
COPY app.py .

# Create a non-root user for security best practices
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose FastAPI application port
EXPOSE 8000

# Container Healthcheck (pings /health endpoint)
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Start Uvicorn server dynamically binding to Render's $PORT or defaulting to 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

