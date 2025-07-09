# 🎵 Precise Digital Lead Generation Tool - Complete Setup Guide

## What You're Getting

A complete, production-ready lead generation system specifically designed for Precise Digital's music services business, featuring:

### ✅ Core Features
- **ISRC Processing Pipeline** - Automatically analyzes music tracks using MusicBrainz, Spotify, and Last.fm
- **Advanced Lead Scoring** - Multi-factor algorithm scoring independence, opportunity, and geographic relevance
- **Contact Discovery** - Finds artist contact information from websites and social media
- **REST API** - Comprehensive endpoints for frontend integration
- **Database Management** - Complete artist and track data models
- **Rate Limiting** - Respects all external API limits automatically

### ✅ Tools & Interfaces
- **Command-line Interface** - Perfect for testing, administration, and batch processing
- **Web API** - Ready for frontend integration
- **Bulk Processing** - Handle thousands of ISRCs efficiently
- **CSV Export** - Export leads directly to your CRM

### ✅ Production Ready
- **Complete Test Suite** - Comprehensive testing coverage
- **Docker Deployment** - One-command deployment with Docker Compose
- **Production Scripts** - Automated deployment and backup scripts
- **Comprehensive Documentation** - API docs, development guides, and deployment instructions

---

## 🚀 Quick Start (30 Minutes to Working System)

### Step 1: Get Your API Keys (10 minutes)

#### 🎵 Spotify Web API (REQUIRED)

1. **Go to Spotify for Developers**
   - Visit: [https://developer.spotify.com/dashboard/](https://developer.spotify.com/dashboard/)
   - Log in with your Spotify account (create one if needed)

2. **Create Your App**
   - Click "Create App"
   - Fill out the form with these **exact** settings:
   ```
   App name: Precise Digital Lead Gen
   App description: Lead generation tool for music industry
   Website: https://localhost:5000
   Redirect URI: https://developer.spotify.com/callback
   ```
   ⚠️ **CRITICAL**: Use `https://developer.spotify.com/callback` - HTTP URLs won't save!

3. **Get Your Credentials**
   - Accept terms and click "Save"
   - Copy your **Client ID**
   - Click "Show Client Secret" and copy your **Client Secret**

#### 🎧 Last.fm API (RECOMMENDED)

1. **Create Account & Application**
   - Visit: [https://www.last.fm/api/account/create](https://www.last.fm/api/account/create)
   - Fill out:
   ```
   Application name: Precise Digital Lead Gen
   Application description: Music industry lead generation tool
   Application homepage: http://localhost:5000
   Application type: Web
   ```

2. **Get Your API Key**
   - Submit the form
   - Copy your **API Key** from the confirmation page

#### 📺 YouTube Data API (OPTIONAL)

1. **Google Cloud Console Setup**
   - Visit: [https://console.cloud.google.com/](https://console.cloud.google.com/)
   - Create a new project or select existing

2. **Enable & Configure**
   - Go to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3" and enable it
   - Go to "Credentials" > "Create Credentials" > "API key"
   - Copy the generated key

### Step 2: Environment Setup (10 minutes)

#### Install the System

```bash
# 1. Create project directory
mkdir precise-digital-leads
cd precise-digital-leads

# 2. Set up Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Create requirements.txt
cat > requirements.txt << 'EOF'
Flask==2.3.3
Flask-CORS==4.0.0
python-dotenv==1.0.0
SQLAlchemy==2.0.21
requests==2.31.0
aiohttp==3.8.6
redis==5.0.0
pandas==2.1.1
python-dateutil==2.8.2
asyncio-throttle==1.0.2
pytest==7.4.2
pytest-asyncio==0.21.1
black==23.7.0
flake8==6.0.0
spotipy==2.23.0
beautifulsoup4==4.12.2
Werkzeug==2.3.7
click==8.1.7
tabulate==0.9.0
EOF

# 4. Install dependencies
pip install -r requirements.txt
```

#### Configure Environment

Create your `.env` file with your API keys:

```bash
cat > .env << 'EOF'
# ====================
# API CREDENTIALS
# ====================

# Spotify API (REQUIRED) - Get from https://developer.spotify.com/dashboard/
SPOTIFY_CLIENT_ID=your_actual_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_actual_spotify_client_secret_here

# Last.fm API (RECOMMENDED) - Get from https://www.last.fm/api/account/create
LASTFM_API_KEY=your_actual_lastfm_api_key_here

# YouTube Data API (OPTIONAL) - Get from https://console.cloud.google.com/
YOUTUBE_API_KEY=your_actual_youtube_api_key_here

# ====================
# APPLICATION CONFIG
# ====================

# Database
DATABASE_URL=sqlite:///data/leads.db
DATABASE_ECHO=false

# Flask
FLASK_ENV=development
FLASK_DEBUG=true
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SECRET_KEY=change-this-secret-key-in-production

# Redis (optional - for advanced rate limiting)
REDIS_URL=redis://localhost:6379/0
EOF
```

**Now edit the `.env` file and replace the placeholder values with your actual API keys!**

### Step 3: Install the Application Code (5 minutes)

You'll need to create all the application files. The complete file structure is:

```
precise-digital-leads/
├── run.py                          # Main entry point
├── cli.py                          # Command line interface
├── requirements.txt                # ✅ Already created
├── .env                           # ✅ Already created
├── config/
│   ├── __init__.py
│   ├── settings.py                # Configuration management
│   └── database.py                # Database setup and models
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py              # Flask API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── pipeline.py            # Main processing pipeline
│   │   ├── scoring.py             # Lead scoring engine
│   │   └── rate_limiter.py        # API rate limiting
│   ├── integrations/
│   │   ├── __init__.py
│   │   └── base_client.py         # API clients (MusicBrainz, Spotify, Last.fm)
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py            # Database models (empty - uses config/database.py)
│   └── services/
│       ├── __init__.py
│       └── contact_discovery.py   # Contact discovery service
└── data/                          # Database files (created automatically)
```

**Important**: You'll need to copy all the code files from the original project documentation. Each file contains specific functionality that makes the system work.

### Step 4: Initialize and Test (5 minutes)

```bash
# Create necessary directories
mkdir -p config src/api src/core src/integrations src/models src/services data

# Initialize database
python cli.py init

# Test API connections
python cli.py status

# Test with a sample ISRC
python cli.py analyze USRC17607839 --no-save --verbose

# Start the web server (in another terminal)
python run.py
```

Visit `http://localhost:5000/api/health` to confirm the web interface is working.

---

## 🧪 Testing Your Setup

### Verify API Connections

```bash
# Check all API integrations
python -c "from src.integrations.base_client import test_clients; test_clients()"

# Check system status
python cli.py status
```

### Process Your First Leads

```bash
# Create test file with sample ISRCs
cat > test_isrcs.txt << 'EOF'
USRC17607839
GBUM71505078
AUUM71801234
EOF

# Process them
python cli.py bulk test_isrcs.txt --batch-size 3

# View results
python cli.py leads --tier A --limit 10

# Get statistics
python cli.py stats

# Export to CSV
python cli.py leads --tier A --export high_priority_leads.csv
```

### Test Web API

```bash
# Health check
curl http://localhost:5000/api/health

# Analyze single ISRC
curl -X POST http://localhost:5000/api/analyze-isrc \
  -H "Content-Type: application/json" \
  -d '{"isrc": "USRC17607839", "save_to_db": false}'

# Get leads list
curl "http://localhost:5000/api/leads?tier=A&limit=5"

# System status
curl http://localhost:5000/api/status
```

---

## 📊 Understanding the System

### Lead Scoring Algorithm

The system scores artists on three factors:

#### 1. Independence Score (40% weight)
- **Self-Released**: 40 points
- **Indie Label**: 25 points  
- **Small Distributor**: 15 points
- **Major Label**: 0 points

#### 2. Opportunity Score (40% weight)
- **Missing Platforms**: 20 points (not on Spotify, Apple Music, etc.)
- **Basic Distribution**: 15 points (only on major streaming)
- **No Publishing Admin**: 10 points
- **Growing Streams**: 15 points (10K-500K listeners)
- **Recent Activity**: 10 points (released in last 12 months)
- **Low Professional Presence**: 10 points (missing website, social media)

#### 3. Geographic Score (20% weight)
- **New Zealand**: 30 points
- **Australia**: 25 points
- **Pacific Islands**: 20 points
- **Other English-speaking**: 10 points
- **Other**: 5 points

#### Lead Tiers
- **Tier A**: 70+ points (High priority)
- **Tier B**: 50-69 points (Medium priority)
- **Tier C**: 30-49 points (Low priority)
- **Tier D**: <30 points (Very low priority)

### Sample Usage Examples

```bash
# Find high-priority New Zealand artists
python cli.py leads --tier A --region new_zealand

# Find recently active artists
python cli.py leads --min-score 60 --limit 20

# Process playlist ISRCs
echo "USRC17607839" > playlist_isrcs.txt
echo "GBUM71505078" >> playlist_isrcs.txt
python cli.py bulk playlist_isrcs.txt

# Export for CRM
python cli.py leads --tier A --tier B --export leads_for_crm.csv
```

---

## 🎯 Practical Usage for Precise Digital

### Daily Lead Generation Workflow

```bash
# 1. Process new ISRCs discovered from industry sources
python cli.py bulk new_isrcs_today.csv --batch-size 20

# 2. Review high-priority leads
python cli.py leads --tier A --region new_zealand --region australia

# 3. Export for outreach team
python cli.py leads --tier A --export daily_leads_$(date +%Y%m%d).csv

# 4. Check system health
python cli.py stats
```

### Finding Specific Types of Artists

```bash
# Self-released artists in target regions
python cli.py leads --tier A --tier B --region new_zealand --region australia

# Growing artists missing professional services
python cli.py leads --min-score 50 --limit 50

# Recently active independent artists
python cli.py leads --tier A --export active_independent_artists.csv
```

### Integration with Your CRM

The CSV exports include all necessary fields:
- Artist Name, Country, Region, Genre
- Comprehensive scoring breakdown
- Contact information (email, website, social media)
- Outreach status tracking
- Monthly listeners and engagement metrics

```bash
# Generate CRM-ready export
python cli.py leads --tier A --tier B --export $(date +%Y%m%d)_crm_leads.csv
```

---

## 🚀 Production Deployment

### Option 1: Docker Deployment (Recommended)

```bash
# 1. Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=sqlite:///data/leads.db
      - FLASK_ENV=production
    env_file:
      - .env
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app
    restart: unless-stopped
EOF

# 2. Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p data

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

CMD ["python", "run.py"]
EOF

# 3. Deploy
docker-compose up -d
```

### Option 2: Traditional Server

```bash
# Install on Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip nginx postgresql

# Deploy to /opt/precise-digital-leads
sudo git clone <your-repo> /opt/precise-digital-leads
cd /opt/precise-digital-leads

# Set up virtual environment
sudo python3 -m venv venv
sudo chown -R www-data:www-data .

# Install and configure
sudo -u www-data venv/bin/pip install -r requirements.txt
sudo -u www-data cp .env.example .env
# Edit .env with production values

# Create systemd service
sudo tee /etc/systemd/system/precise-digital.service > /dev/null << 'EOF'
[Unit]
Description=Precise Digital Lead Generation
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/precise-digital-leads
ExecStart=/opt/precise-digital-leads/venv/bin/python run.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable precise-digital
sudo systemctl start precise-digital
```

---

## 🔧 Extending the System

### Adding New APIs

```python
# 1. Create new client in src/integrations/
class NewAPIClient(BaseAPIClient):
    def __init__(self):
        super().__init__('new_api')
    
    def get_artist_data(self, artist_name):
        # Implementation here
        pass

# 2. Add to config/settings.py
'new_api': APIConfig(
    name='new_api',
    base_url='https://api.newservice.com/',
    requests_per_minute=100,
    api_key=os.getenv('NEW_API_KEY')
)

# 3. Integrate in src/core/pipeline.py
new_data = new_api_client.get_artist_data(artist_name)
```

### Customizing Scoring

```python
# Modify weights in config/settings.py
self.scoring_weights = {
    'independence': {
        'self_released': 50,        # Increase from 40
        'indie_label': 30,          # Increase from 25
        # ... etc
    }
}
```

### Adding New Endpoints

```python
# Add to src/api/routes.py
@app.route('/api/custom-endpoint', methods=['GET'])
def custom_endpoint():
    # Your implementation
    return jsonify({'result': 'success'})
```

---

## 📊 Monitoring & Maintenance

### Daily Operations

```bash
# Morning routine
python cli.py status           # Check API health
python cli.py stats            # Review overnight processing
python cli.py leads --tier A   # Check high-priority leads

# Evening routine
./scripts/backup.sh            # Backup database
python cli.py stats            # Daily processing summary
```

### Performance Monitoring

```bash
# Check API rate limits
curl http://localhost:5000/api/status

# Monitor processing performance
python cli.py stats

# Database health
ls -la data/leads.db           # Check database size
python -c "from config.database import DatabaseManager; db = DatabaseManager(); print(f'Artists: {db.session.query(db.Artist).count()}')"
```

### Troubleshooting

#### Common Issues

**Spotify Authentication Fails**
```bash
# Check credentials
python -c "from config.settings import settings; print('Client ID configured:', bool(settings.spotify_client_id))"

# Test authentication
python -c "from src.integrations.base_client import spotify_client; print('Token:', bool(spotify_client.access_token))"
```

**Database Issues**
```bash
# Reset database (WARNING: Deletes all data)
python cli.py reset

# Check database integrity
python -c "from config.database import DatabaseManager; DatabaseManager()"
```

**Rate Limiting Issues**
```bash
# Check current status
python cli.py status

# Reduce batch sizes
python cli.py bulk file.csv --batch-size 5 --delay 2
```

---

## 🎯 Success Metrics

### Technical Metrics
- **API Success Rate**: >95% (check with `python cli.py status`)
- **Processing Speed**: ~20-30 seconds per ISRC
- **Data Accuracy**: Spot-check results manually
- **System Uptime**: Monitor with health checks

### Business Metrics
- **Lead Quality**: Review Tier A leads manually
- **Contact Discovery**: >70% of leads should have contact info
- **Geographic Targeting**: >80% should be in target regions (NZ/AU/Pacific)
- **False Positive Rate**: <20% of Tier A leads should be unsuitable

### Weekly Review

```bash
# Generate weekly report
python cli.py stats
python cli.py leads --tier A --export weekly_tier_a_leads.csv
python cli.py leads --region new_zealand --export weekly_nz_leads.csv

# Review contact discovery effectiveness
python cli.py leads --tier A --limit 20 | grep -E "contact_email|website"
```

---

## 📞 Support & Resources

### Getting Help

1. **Check System Status**: `python cli.py status`
2. **Review Logs**: Check console output for errors
3. **Test Components**: Use CLI commands to isolate issues
4. **Documentation**: See `/docs` folder for detailed guides

### API Rate Limits

| API | Free Tier | Daily Capacity | Notes |
|-----|-----------|----------------|-------|
| Spotify | 100/minute | ~144,000/day | Excellent for high volume |
| Last.fm | 5/second | ~432,000/day | Very generous limits |
| YouTube | 10,000/day | 10,000/day | Good for supplementary data |
| MusicBrainz | 1/second | ~86,400/day | Be respectful, it's free |

### Best Practices

1. **API Key Security**: Never commit `.env` files, rotate keys regularly
2. **Rate Limiting**: The system handles this automatically
3. **Data Quality**: Regularly review Tier A leads manually
4. **Backup Strategy**: Daily database backups with `./scripts/backup.sh`
5. **Monitoring**: Set up alerts for processing failures

---

## 🎉 You're Ready!

Your Precise Digital Lead Generation Tool is now:

✅ **Fully Configured** - All APIs connected and tested  
✅ **Processing ISRCs** - Turning music identifiers into qualified leads  
✅ **Scoring Accurately** - Prioritizing independent artists in your target regions  
✅ **Finding Contacts** - Discovering email addresses and social media handles  
✅ **Export Ready** - Generating CRM-ready lead lists  
✅ **Production Capable** - Ready to scale with Docker deployment  

### Immediate Next Steps

1. **Process Your First Real Batch**: Get ISRCs from industry sources and run them through the system
2. **Review Tier A Leads**: Manually validate the quality of high-scoring leads
3. **Export to CRM**: Generate your first lead export for the outreach team
4. **Monitor Performance**: Check `python cli.py stats` daily to track progress

### Contact for Support

- **Technical Issues**: Review documentation in `/docs` folder
- **Feature Requests**: Consider extending the system using the provided patterns
- **Business Questions**: Use the lead exports to validate system effectiveness

**The system is designed to continuously improve Precise Digital's lead generation process, helping you identify and prioritize independent artists who are most likely to benefit from your music services.**