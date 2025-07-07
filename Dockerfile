# Multi-stage build for maximum optimization
FROM python:3.12-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Copy requirements files
COPY requirements-prod.txt ./

# Install production dependencies only
RUN pip install --user --upgrade setuptools && \
    pip install --user --no-cache-dir -r requirements-prod.txt

# Base runtime stage
FROM python:3.12-slim as base

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:$PATH"

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local
RUN chown -R appuser:appuser /home/appuser/.local

# Set working directory
WORKDIR /app

# Copy core Django files that both web and celery need
COPY --chown=appuser:appuser app/manage.py /app/
COPY --chown=appuser:appuser app/streambuddy/ /app/streambuddy/
COPY --chown=appuser:appuser app/streambuddy_common/ /app/streambuddy_common/

# Create empty __init__.py files for Python packages
RUN mkdir -p /app/accounts /app/videos && \
    touch /app/__init__.py /app/accounts/__init__.py /app/videos/__init__.py && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Web stage - includes all Django apps
FROM base as web

# Copy all Django apps for web server
COPY --chown=appuser:appuser app/accounts/ /app/accounts/
COPY --chown=appuser:appuser app/videos/ /app/videos/

# Remove Python cache files
RUN find /app -name "*.pyc" -delete && \
    find /app -name "__pycache__" -type d -exec rm -rf {} + || true

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "streambuddy.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]

# Celery stage - minimal files only
FROM base as celery

# Copy only essential files for Celery
COPY --chown=appuser:appuser app/videos/ /app/videos/
COPY --chown=appuser:appuser app/accounts/models.py /app/accounts/models.py


# Remove Python cache files
RUN find /app -name "*.pyc" -delete && \
    find /app -name "__pycache__" -type d -exec rm -rf {} + || true

CMD ["python", "-m", "celery", "-A", "streambuddy", "worker", "--loglevel=info", "--concurrency=2"]