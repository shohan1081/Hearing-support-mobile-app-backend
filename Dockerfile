# ==============================================================================
# Multi-stage Production Dockerfile for Hearing Improvement Mobile App Backend
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Build dependencies
# ------------------------------------------------------------------------------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependencies file
COPY requirements.txt .

# Create wheel package dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir gunicorn && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# ------------------------------------------------------------------------------
# Stage 2: Final minimal runtime image
# ------------------------------------------------------------------------------
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

# Install runtime system libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy built wheels from builder stage
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install wheels and gunicorn
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir /wheels/* && \
    pip install --no-cache-dir gunicorn && \
    rm -rf /wheels

# Create non-root system user for production security
RUN groupadd -r appgroup && useradd -r -g appgroup -u 1000 appuser

# Create static root, media root, and logs directories
RUN mkdir -p $APP_HOME/staticfiles $APP_HOME/media $APP_HOME/logs

# Copy application source code
COPY . $APP_HOME

# Make entrypoint script executable & set directory permissions
RUN chmod +x $APP_HOME/entrypoint.sh && \
    chown -R appuser:appgroup $APP_HOME

# Switch to non-root user
USER appuser

# Expose container port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
