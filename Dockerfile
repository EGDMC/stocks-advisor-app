# Use Python 3.9 slim base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH="/app"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src/ ./src/
COPY vercel-deploy/api/ ./api/

# Create non-root user
RUN useradd -m appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# Expose port
EXPOSE ${PORT:-8080}

# Set resource limits
ENV MEMORY_LIMIT=2g \
    CPU_LIMIT=1

# Run the application with Gunicorn
CMD gunicorn --workers=2 \
    --threads=4 \
    --timeout=0 \
    --bind=0.0.0.0:${PORT:-8080} \
    --worker-class=gthread \
    --worker-tmp-dir=/dev/shm \
    --max-requests=1000 \
    --max-requests-jitter=50 \
    --log-level=info \
    --access-logfile=- \
    --error-logfile=- \
    "src.app:create_app()"