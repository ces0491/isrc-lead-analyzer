# docs/DEPLOYMENT.md

# Deployment Guide

## Production Deployment Options

### Option 1: Docker Deployment (Recommended)

#### Prerequisites
- Docker and Docker Compose installed
- Domain name configured (optional)
- SSL certificates (for HTTPS)

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
   
   # Create production environment file
   cp .env.example .env
   # Edit .env with production values
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
   
   # Run deployment
   ./scripts/deploy.sh
   ```

5. **Verify deployment**
   ```bash
   # Check application health
   curl http://localhost/api/health
   
   # Check logs
   docker-compose logs app
   ```

#### Production Environment Variables

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

# Redis
REDIS_URL=redis://redis:6379/0

# Security
CORS_ORIGINS=https://yourdomain.com
```

### Option 2: Traditional Server Deployment

#### Prerequisites
- Ubuntu 20.04+ or similar Linux distribution
- Python 3.8+
- PostgreSQL (recommended for production)
- Nginx
- Redis (optional, for rate limiting)

#### Installation Steps

1. **Install system dependencies**
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server
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
   
   # Activate environment and install dependencies
   sudo -u www-data venv/bin/pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   sudo -u www-data cp .env.example .env
   # Edit .env with production settings
   sudo -u www-data nano .env
   ```

5. **Initialize database**
   ```bash
   sudo -u www-data venv/bin/python cli.py init
   ```

6. **Set up systemd service**
   ```bash
   sudo cp scripts/precise-digital.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable precise-digital
   sudo systemctl start precise-digital
   ```

7. **Configure Nginx**
   ```bash
   sudo cp scripts/nginx-site.conf /etc/nginx/sites-available/precise-digital
   sudo ln -s /etc/nginx/sites-available/precise-digital /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### Option 3: Cloud Platform Deployment

#### Heroku Deployment

1. **Install Heroku CLI**
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Prepare application**
   ```bash
   # Create Procfile
   echo "web: python run.py" > Procfile
   
   # Create runtime.txt
   echo "python-3.11.0" > runtime.txt
   ```

3. **Deploy to Heroku**
   ```bash
   heroku create your-app-name
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set SPOTIFY_CLIENT_ID=your-id
   heroku config:set SPOTIFY_CLIENT_SECRET=your-secret
   
   git push heroku main
   
   # Initialize database
   heroku run python cli.py init
   ```

#### Railway Deployment

1. **Connect repository to Railway**
   - Go to railway.app
   - Connect your GitHub repository
   - Configure environment variables

2. **Set environment variables**
   ```
   FLASK_ENV=production
   SECRET_KEY=your-secret-key
   SPOTIFY_CLIENT_ID=your-id
   SPOTIFY_CLIENT_SECRET=your-secret
   ```

## Monitoring and Maintenance

### Health Monitoring

```bash
# Check application health
curl https://yourdomain.com/api/health

# Monitor logs
docker-compose logs -f app

# Check system status
curl https://yourdomain.com/api/status
```

### Backup Strategy

```bash
# Automated backup script
chmod +x scripts/backup.sh

# Set up daily backup cron job
echo "0 2 * * * /opt/precise-digital-leads/scripts/backup.sh" | sudo crontab -
```

### Performance Monitoring

#### Key Metrics to Monitor
- Response times for API endpoints
- Database query performance
- Rate limit usage for external APIs
- Memory and CPU usage
- Error rates

#### Tools
- **Application Performance Monitoring**: New Relic, DataDog
- **Infrastructure Monitoring**: Prometheus + Grafana
- **Log Management**: ELK Stack, Splunk

### Security Considerations

#### Environment Security
- Use strong, unique passwords
- Keep API keys secure and rotate regularly
- Use HTTPS in production
- Implement proper CORS settings
- Keep dependencies updated

#### Database Security
- Use connection pooling
- Implement proper backup encryption
- Regular security updates
- Monitor for unusual activity

### Scaling Considerations

#### Horizontal Scaling
- Use load balancer (nginx, HAProxy)
- Deploy multiple application instances
- Implement Redis for session storage
- Use database connection pooling

#### Vertical Scaling
- Monitor resource usage
- Upgrade server specifications as needed
- Optimize database queries
- Implement caching strategies

### Troubleshooting Common Issues

#### Application Won't Start
```bash
# Check logs
docker-compose logs app

# Check environment variables
docker-compose exec app env

# Check database connection
docker-compose exec app python -c "from config.database import init_db; init_db()"
```

#### High Memory Usage
```bash
# Monitor memory usage
docker stats

# Check for memory leaks in logs
docker-compose logs app | grep -i memory
```

#### API Rate Limit Issues
```bash
# Check rate limit status
curl http://localhost:5000/api/status

# Adjust batch sizes in processing
```

#### Database Connection Issues
```bash
# Check database container
docker-compose logs db

# Test database connection
docker-compose exec app python -c "from src.models.database import DatabaseManager; db = DatabaseManager()"
```

### Updating the Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose build
docker-compose up -d

# Check health after update
curl http://localhost/api/health
```

### Support and Maintenance

For ongoing support:
1. Monitor application logs regularly
2. Keep dependencies updated
3. Backup data regularly
4. Monitor API usage and costs
5. Review and update security settings

---