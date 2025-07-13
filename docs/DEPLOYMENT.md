# Deployment Guide

## Production Deployment Options

### Option 1: Docker Deployment (Recommended)

#### Prerequisites
- Docker and Docker Compose installed
- Domain name configured (optional)
- SSL certificates (for HTTPS)
- **YouTube Data API key configured** (NEW)

#### Deployment Steps

1. **Prepare the server**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Clone and configure the application**
   ```bash
   git clone <repository-url>
   cd precise-digital-leads
   
   # Create production environment file with YouTube configuration
   cp .env.example .env
   # Edit .env with production values including YouTube API key
   ```

3. **Configure SSL (optional but recommended)**
   ```bash
   # Create SSL directory
   mkdir ssl
   
   # Copy your SSL certificates
   cp your-cert.pem ssl/cert.pem
   cp your-key.pem ssl/key.pem
   
   # Or generate self-signed certificates for testing
   openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes
   ```

4. **Deploy the application**
   ```bash
   # Make deployment script executable
   chmod +x scripts/deploy.sh
   
   # Run deployment with YouTube integration
   ./scripts/deploy.sh
   ```

5. **Verify deployment including YouTube**
   ```bash
   # Check application health (now includes YouTube status)
   curl http://localhost/api/health
   
   # Check YouTube integration specifically
   curl http://localhost/api/youtube/stats
   
   # Check logs
   docker-compose logs app
   ```

#### Production Environment Variables (Updated)

```env
# Application
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=your-strong-secret-key-here

# Database (upgrade to PostgreSQL for production)
DATABASE_URL=postgresql://user:password@localhost/precise_digital

# API Keys (required)
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
LASTFM_API_KEY=your_lastfm_api_key

# YouTube API Configuration (NEW - REQUIRED)
YOUTUBE_API_KEY=your_youtube_api_key
YOUTUBE_DAILY_QUOTA=10000
YOUTUBE_REQUESTS_PER_MINUTE=100

# Redis
REDIS_URL=redis://redis:6379/0

# Security
CORS_ORIGINS=https://yourdomain.com

# YouTube Monitoring (NEW)
YOUTUBE_QUOTA_WARNING_THRESHOLD=8000
YOUTUBE_QUOTA_ALERT_EMAIL=admin@precise.digital
```

#### Updated Docker Compose Configuration

```yaml
# docker-compose.yml with YouTube integration
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://precise:password@db:5432/precise_digital
      - FLASK_ENV=production
      - FLASK_DEBUG=false
      - YOUTUBE_API_KEY=${YOUTUBE_API_KEY}
      - YOUTUBE_DAILY_QUOTA=${YOUTUBE_DAILY_QUOTA:-10000}
      - YOUTUBE_REQUESTS_PER_MINUTE=${YOUTUBE_REQUESTS_PER_MINUTE:-100}
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - db
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=precise_digital
      - POSTGRES_USER=precise
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

  # NEW: YouTube quota monitoring service
  youtube-monitor:
    build: .
    command: python scripts/youtube_quota_monitor.py
    environment:
      - YOUTUBE_API_KEY=${YOUTUBE_API_KEY}
      - YOUTUBE_QUOTA_WARNING_THRESHOLD=${YOUTUBE_QUOTA_WARNING_THRESHOLD:-8000}
    env_file:
      - .env
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Option 2: Traditional Server Deployment

#### Prerequisites
- Ubuntu 20.04+ or similar Linux distribution
- Python 3.8+
- PostgreSQL (recommended for production)
- Nginx
- Redis (optional, for rate limiting)
- **YouTube Data API access** (NEW)

#### Installation Steps

1. **Install system dependencies**
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server curl
   ```

2. **Set up PostgreSQL**
   ```bash
   sudo -u postgres createuser --interactive
   sudo -u postgres createdb precise_digital
   
   # Set password for database user
   sudo -u postgres psql
   ALTER USER username PASSWORD 'password';
   \q
   ```

3. **Clone and set up application**
   ```bash
   cd /opt
   sudo git clone <repository-url> precise-digital-leads
   cd precise-digital-leads
   
   # Create virtual environment
   sudo python3 -m venv venv
   sudo chown -R www-data:www-data .
   
   # Activate environment and install dependencies (includes YouTube client)
   sudo -u www-data venv/bin/pip install -r requirements.txt
   ```

4. **Configure environment with YouTube**
   ```bash
   sudo -u www-data cp .env.example .env
   # Edit .env with production settings including YouTube API key
   sudo -u www-data nano .env
   ```

5. **Initialize database with YouTube schema**
   ```bash
   sudo -u www-data venv/bin/python cli.py init
   
   # Verify YouTube migration is applied
   sudo -u www-data venv/bin/python cli.py youtube-status
   ```

6. **Set up systemd service with YouTube monitoring**
   ```bash
   sudo cp scripts/precise-digital.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable precise-digital
   sudo systemctl start precise-digital
   
   # Verify YouTube integration is working
   sudo systemctl status precise-digital
   curl http://localhost:5000/api/youtube/stats
   ```

7. **Configure Nginx with YouTube endpoint support**
   ```bash
   sudo cp scripts/nginx-site.conf /etc/nginx/sites-available/precise-digital
   sudo ln -s /etc/nginx/sites-available/precise-digital /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

#### Updated Nginx Configuration

```nginx
# /etc/nginx/sites-available/precise-digital
server {
    listen 80;
    server_name yourdomain.com;
    
    # YouTube API endpoints may have larger responses
    client_max_body_size 20M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Longer timeout for YouTube API calls
        proxy_read_timeout 60s;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
    }
    
    # Special handling for YouTube endpoints that may take longer
    location ~ ^/api/youtube/(test|refresh) {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Extended timeout for YouTube API operations
        proxy_read_timeout 120s;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
    }
}
```

### Option 3: Cloud Platform Deployment

#### Heroku Deployment (Updated)

1. **Install Heroku CLI**
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Prepare application with YouTube support**
   ```bash
   # Create Procfile
   echo "web: python run.py" > Procfile
   echo "youtube-monitor: python scripts/youtube_quota_monitor.py" >> Procfile
   
   # Create runtime.txt
   echo "python-3.11.0" > runtime.txt
   ```

3. **Deploy to Heroku with YouTube configuration**
   ```bash
   heroku create your-app-name
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set SPOTIFY_CLIENT_ID=your-id
   heroku config:set SPOTIFY_CLIENT_SECRET=your-secret
   heroku config:set YOUTUBE_API_KEY=your-youtube-key
   heroku config:set YOUTUBE_DAILY_QUOTA=10000
   
   # Add PostgreSQL addon
   heroku addons:create heroku-postgresql:mini
   
   # Add Redis addon for rate limiting
   heroku addons:create heroku-redis:mini
   
   git push heroku main
   
   # Initialize database with YouTube schema
   heroku run python cli.py init
   
   # Verify YouTube integration
   heroku run python cli.py youtube-status
   ```

#### Railway Deployment (Updated)

1. **Connect repository to Railway**
   - Go to railway.app
   - Connect your GitHub repository
   - Configure environment variables including YouTube

2. **Set environment variables with YouTube support**
   ```
   FLASK_ENV=production
   SECRET_KEY=your-secret-key
   SPOTIFY_CLIENT_ID=your-id
   SPOTIFY_CLIENT_SECRET=your-secret
   YOUTUBE_API_KEY=your-youtube-key
   YOUTUBE_DAILY_QUOTA=10000
   DATABASE_URL=postgresql://...
   ```

## Monitoring and Maintenance

### Health Monitoring (Updated)

```bash
# Check application health including YouTube integration
curl https://yourdomain.com/api/health

# Monitor YouTube API status specifically
curl https://yourdomain.com/api/youtube/stats

# Check YouTube quota usage
curl https://yourdomain.com/api/status | jq '.youtube_integration'

# Monitor logs including YouTube API calls
docker-compose logs -f app | grep -i youtube

# Check system status
curl https://yourdomain.com/api/status
```

### Backup Strategy (Enhanced)

```bash
# Automated backup script with YouTube data preservation
chmod +x scripts/backup.sh

# Enhanced backup that includes YouTube migration status
cat > scripts/backup_with_youtube.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
APP_DIR="/opt/precise-digital-leads"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump precise_digital > $BACKUP_DIR/db_backup_$DATE.sql

# Backup YouTube migration status
python3 -c "from config.database import check_youtube_migration_needed; print('YouTube migration needed:', check_youtube_migration_needed())" > $BACKUP_DIR/youtube_status_$DATE.txt

# Backup configuration
cp $APP_DIR/.env $BACKUP_DIR/env_backup_$DATE.txt

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.txt" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

# Set up daily backup cron job
echo "0 2 * * * /opt/precise-digital-leads/scripts/backup_with_youtube.sh" | sudo crontab -
```

### Performance Monitoring (Enhanced)

#### Key Metrics to Monitor (Updated)
- Response times for API endpoints including YouTube endpoints
- Database query performance including YouTube table queries
- Rate limit usage for external APIs including YouTube daily quotas
- Memory and CPU usage
- Error rates including YouTube API errors
- **YouTube quota consumption patterns** (NEW)
- **YouTube API response times** (NEW)

#### Tools (Updated)
- **Application Performance Monitoring**: New Relic, DataDog (with YouTube custom metrics)
- **Infrastructure Monitoring**: Prometheus + Grafana (YouTube quota dashboards)
- **Log Management**: ELK Stack, Splunk (YouTube API logging)
- **YouTube-Specific Monitoring**: Custom quota tracking dashboard

#### YouTube-Specific Monitoring Script

```python
# scripts/youtube_quota_monitor.py
import os
import requests
import time
from datetime import datetime

def monitor_youtube_quota():
    """Monitor YouTube API quota usage and send alerts"""
    api_url = os.getenv('APP_URL', 'http://localhost:5000')
    warning_threshold = int(os.getenv('YOUTUBE_QUOTA_WARNING_THRESHOLD', 8000))
    
    while True:
        try:
            response = requests.get(f"{api_url}/api/youtube/stats")
            if response.status_code == 200:
                data = response.json()
                quota_used = data.get('daily_quota_used', 0)
                quota_limit = data.get('daily_quota_limit', 10000)
                
                if quota_used > warning_threshold:
                    print(f"WARNING: YouTube quota usage high: {quota_used}/{quota_limit}")
                    # Send alert email/notification here
                
                print(f"YouTube quota: {quota_used}/{quota_limit} ({quota_used/quota_limit*100:.1f}%)")
            
        except Exception as e:
            print(f"Error monitoring YouTube quota: {e}")
        
        time.sleep(3600)  # Check every hour

if __name__ == '__main__':
    monitor_youtube_quota()
```

### Security Considerations (Updated)

#### Environment Security (Enhanced)
- Use strong, unique passwords
- Keep API keys secure and rotate regularly **including YouTube API keys**
- Use HTTPS in production
- Implement proper CORS settings
- Keep dependencies updated
- **Restrict YouTube API key to specific IP addresses in production** (NEW)
- **Monitor YouTube API key usage for suspicious activity** (NEW)

#### Database Security (Enhanced)
- Use connection pooling
- Implement proper backup encryption
- Regular security updates
- Monitor for unusual activity
- **Secure YouTube data with appropriate access controls** (NEW)

#### YouTube API Security Best Practices (NEW)
- Restrict API key to YouTube Data API v3 only
- Use IP restrictions in Google Cloud Console
- Monitor quota usage for anomalies
- Implement rate limiting to prevent quota exhaustion
- Log all YouTube API requests for audit trails

### Scaling Considerations (Updated)

#### Horizontal Scaling (Enhanced)
- Use load balancer (nginx, HAProxy)
- Deploy multiple application instances
- Implement Redis for session storage
- Use database connection pooling
- **Distribute YouTube API calls across instances to manage quotas** (NEW)

#### Vertical Scaling (Enhanced)
- Monitor resource usage including YouTube API call overhead
- Upgrade server specifications as needed
- Optimize database queries including YouTube table queries
- Implement caching strategies for YouTube data
- **Consider YouTube API quota scaling with Google** (NEW)

#### YouTube-Specific Scaling (NEW)
- **Quota Management**: Distribute calls across multiple API keys if needed
- **Caching Strategy**: Cache YouTube data for 24 hours to reduce API calls
- **Batch Processing**: Process YouTube requests in optimal batch sizes
- **Geographic Distribution**: Consider regional YouTube API endpoints

### Troubleshooting Common Issues (Updated)

#### Application Won't Start
```bash
# Check logs including YouTube integration
docker-compose logs app

# Check environment variables including YouTube
docker-compose exec app env | grep YOUTUBE

# Check database connection and YouTube schema
docker-compose exec app python -c "from config.database import init_db, check_youtube_migration_needed; init_db(); print('YouTube migration needed:', check_youtube_migration_needed())"
```

#### High Memory Usage
```bash
# Monitor memory usage
docker stats

# Check for memory leaks in logs including YouTube operations
docker-compose logs app | grep -i -E "(memory|youtube)"
```

#### YouTube API Issues (NEW)
```bash
# Check YouTube API configuration
curl http://localhost:5000/api/youtube/stats

# Test YouTube connectivity
python cli.py test-youtube "test artist"

# Check quota status
curl http://localhost:5000/api/status | jq '.youtube_integration'

# Monitor YouTube API errors
docker-compose logs app | grep -i "youtube.*error"
```

#### Rate Limit Issues (Enhanced)
```bash
# Check rate limit status including YouTube
curl http://localhost:5000/api/status

# Check YouTube quota specifically
curl http://localhost:5000/api/youtube/stats

# Adjust batch sizes for YouTube processing
python cli.py bulk file.csv --batch-size 5 --delay 2 --include-youtube
```

#### Database Connection Issues (Updated)
```bash
# Check database container
docker-compose logs db

# Test database connection and YouTube schema
docker-compose exec app python -c "from config.database import DatabaseManager, check_youtube_migration_needed; db = DatabaseManager(); print('DB connected, YouTube migration needed:', check_youtube_migration_needed())"

# Run YouTube migration if needed
docker-compose exec app python cli.py migrate-youtube
```

### Updating the Application (Enhanced)

```bash
# Pull latest code
git pull origin main

# Check for YouTube schema updates
python cli.py youtube-status

# Run any new YouTube migrations
python cli.py migrate-youtube

# Rebuild and restart
docker-compose build
docker-compose up -d

# Check health after update including YouTube
curl http://localhost/api/health
curl http://localhost/api/youtube/stats
```

### Support and Maintenance (Updated)

For ongoing support:
1. Monitor application logs regularly including YouTube API errors
2. Keep dependencies updated including YouTube client libraries
3. Backup data regularly including YouTube schema
4. **Monitor YouTube API usage and costs** (NEW)
5. Review and update security settings including YouTube API restrictions
6. **Plan for YouTube quota scaling as usage grows** (NEW)

#### YouTube-Specific Maintenance Tasks (NEW)
- **Daily**: Check YouTube quota usage
- **Weekly**: Review YouTube data quality and coverage
- **Monthly**: Analyze YouTube opportunity identification accuracy
- **Quarterly**: Review YouTube API costs and consider optimization

#### Emergency Procedures (NEW)
- **YouTube Quota Exhausted**: Switch to processing without YouTube until reset
- **YouTube API Down**: Continue processing other data sources
- **YouTube Rate Limit Hit**: Implement exponential backoff and retry logic

---

## Production Checklist

### Pre-Deployment (Updated)
- [ ] All API keys configured including YouTube
- [ ] Environment variables set for production
- [ ] Database migration completed including YouTube schema
- [ ] SSL certificates configured
- [ ] Backup strategy implemented
- [ ] Monitoring setup including YouTube quota tracking
- [ ] **YouTube API key restrictions configured** (NEW)
- [ ] **YouTube quota alerts configured** (NEW)

### Post-Deployment (Updated)
- [ ] Health check passes including YouTube status
- [ ] All API integrations working including YouTube
- [ ] Database queries optimized including YouTube tables
- [ ] Backup restoration tested
- [ ] Monitoring alerts working including YouTube quota warnings
- [ ] **YouTube data collection verified** (NEW)
- [ ] **YouTube opportunity detection tested** (NEW)

### Ongoing Maintenance (Updated)
- [ ] Regular security updates
- [ ] Performance monitoring including YouTube metrics
- [ ] Backup verification
- [ ] API key rotation including YouTube
- [ ] **YouTube quota usage analysis** (NEW)
- [ ] **YouTube data quality assessment** (NEW)

---

This deployment guide now includes comprehensive YouTube integration support, ensuring your production deployment can take full advantage of the enhanced lead generation capabilities with YouTube data.