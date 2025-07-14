# Docker fallback if PYTHON_VERSION doesn't work

Write-Host "🐳 FALLBACK: Docker Deployment (if PYTHON_VERSION failed)" -ForegroundColor Yellow
Write-Host ""

Write-Host "📝 Creating Dockerfile with Python 3.11..." -ForegroundColor Green

$dockerfile = @"
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create app user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/api/status || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "wsgi:app"]
"@

$dockerfile | Out-File -FilePath "Dockerfile" -Encoding UTF8

Write-Host "📝 Creating Docker-based render.yaml..." -ForegroundColor Green

$renderDockerYaml = @"
services:
  - type: pserv
    name: isrc-analyzer-postgres
    plan: starter

  - type: web
    name: isrc-analyzer-api
    runtime: docker
    plan: starter
    dockerfilePath: ./Dockerfile
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: isrc-analyzer-postgres
          property: connectionString
      - key: FLASK_ENV
        value: production
      - key: SPOTIFY_CLIENT_ID
        sync: false
      - key: SPOTIFY_CLIENT_SECRET
        sync: false
      - key: YOUTUBE_API_KEY
        sync: false
      - key: LASTFM_API_KEY
        sync: false
      - key: SECRET_KEY
        sync: false
      - key: CORS_ORIGINS
        value: "*"
    healthCheckPath: /api/status
"@

$renderDockerYaml | Out-File -FilePath "render.yaml" -Encoding UTF8

Write-Host "✅ Docker fallback ready!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 If PYTHON_VERSION test fails, run:" -ForegroundColor Yellow
Write-Host "git add Dockerfile render.yaml" -ForegroundColor Gray
Write-Host "git commit -m 'fix: Docker deployment with Python 3.11'" -ForegroundColor Gray
Write-Host "git push origin main" -ForegroundColor Gray
Write-Host ""
Write-Host "💡 Docker guarantees Python 3.11 with full pandas support" -ForegroundColor Blue