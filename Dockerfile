# Prism Analytics Engine - Docker Configuration
# Multi-stage build for production-ready container

# ===============================================
# Build Stage - Dependencies and Setup
# ===============================================
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# ===============================================
# Production Stage - Runtime Environment
# ===============================================
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd --gid 1000 precise && \
    useradd --uid 1000 --gid precise --shell /bin/bash --create-home precise

# Create application directories
WORKDIR /app
RUN mkdir -p /app/data /app/logs /app/exports && \
    chown -R precise:precise /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --chown=precise:precise . .

# Ensure executable permissions
RUN chmod +x run.py

# Switch to non-root user
USER precise

# Create required directories with proper permissions
RUN mkdir -p data logs exports

# ===============================================
# Health Check
# ===============================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-5000}/api/health || exit 1

# ===============================================
# Runtime Configuration
# ===============================================

# Expose port
EXPOSE 5000

# Set default environment variables
ENV FLASK_APP=run.py \
    FLASK_ENV=production \
    HOST=0.0.0.0 \
    PORT=5000 \
    WORKERS=4

# Default command
CMD ["python", "run.py"]

# ===============================================
# Build Arguments and Metadata
# ===============================================
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

LABEL maintainer="Precise Digital <contact@precise.digital>" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="Prism Analytics Engine" \
      org.label-schema.description="Lead generation tool for independent music services" \
      org.label-schema.url="https://precise.digital" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/precise-digital/prism-analytics" \
      org.label-schema.vendor="Precise Digital" \
      org.label-schema.version=$VERSION \
      org.label-schema.schema-version="1.0"