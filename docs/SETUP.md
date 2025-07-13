# 🎵 Precise Digital Lead Generation Tool - Complete Setup Guide

## What You're Getting

A complete, production-ready lead generation system specifically designed for Precise Digital's music services business, featuring:

### ✅ Core Features
- **ISRC Processing Pipeline** - Automatically analyzes music tracks using MusicBrainz, Spotify, Last.fm, and **YouTube**
- **Advanced Lead Scoring** - Multi-factor algorithm scoring independence, opportunity, and geographic relevance **with YouTube opportunity assessment**
- **Contact Discovery** - Finds artist contact information from websites, social media, **and YouTube channels**
- **REST API** - Comprehensive endpoints for frontend integration **including YouTube-specific endpoints**
- **Database Management** - Complete artist and track data models **with YouTube metrics**
- **Rate Limiting** - Respects all external API limits automatically **including YouTube's daily quotas**

### ✅ **NEW: YouTube Integration Features**
- **Channel Discovery** - Automatically finds artist YouTube channels
- **Performance Analytics** - Subscriber counts, view metrics, engagement rates
- **Opportunity Assessment** - Identifies underperforming or missing YouTube presence
- **Growth Potential Scoring** - Evaluates upload frequency and channel optimization
- **Contact Discovery** - Includes YouTube channels as contact methods
- **Export Integration** - YouTube metrics included in all lead exports

### ✅ Tools & Interfaces
- **Command-line Interface** - Perfect for testing, administration, and batch processing **with YouTube commands**
- **Web API** - Ready for frontend integration **with YouTube endpoints**
- **Bulk Processing** - Handle thousands of ISRCs efficiently **with YouTube data collection**
- **CSV Export** - Export leads directly to your CRM **with YouTube metrics**

### ✅ Production Ready
- **Complete Test Suite** - Comprehensive testing coverage **including YouTube integration tests**
- **Docker Deployment** - One-command deployment with Docker Compose **with YouTube configuration**
- **Production Scripts** - Automated deployment and backup scripts
- **Comprehensive Documentation** - API docs, development guides, and deployment instructions **updated for YouTube**

---

## 🚀 Quick Start (30 Minutes to Working System)

### Step 1: Get Your API Keys (15 minutes)

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

#### 🎥 YouTube Data API (RECOMMENDED - NEW!)

1. **Go to Google Cloud Console**
   - Visit: [https://console.cloud.google.com/](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable YouTube Data API v3**
   - Go to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click on it and press "Enable"

3. **Create API Key**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API key"
   - Copy the generated key
   - **RECOMMENDED**: Click "Restrict Key" and limit to "YouTube Data API v3" for security

4. **Set Quotas (Optional)**
   - Go to "APIs & Services" > "Quotas"
   - Find "YouTube Data API v3"
   - Default quota is 10,000 units/day (sufficient for most use cases)

#### 🎧 Last.fm API (RECOMMENDED)

1. **Create Account & Application**
   - Visit: [https://www.last.fm/api/account/create](https://www.last.fm/api/account/create)
   - Fill out:
   ```
   Application name: Precise Digital Lead Gen
   Application description: Music industry lead generation tool with YouTube integration
   Application homepage: http://localhost:5000
   Application type: Web
   ```

2. **Get Your API Key**
   - Submit the form
   - Copy your **API Key** from the confirmation page

### Step 2: Environment Setup (10 minutes)

#### Install the System

```bash
# 1. Create project directory
mkdir precise-digital-leads
cd precise-digital-leads

# 2. Set up Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Create requirements.txt (now includes YouTube dependencies)
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
google-api-python-client==2.108.0
google-auth-httplib2==0.1.1
google-auth-oauthlib==1.1.0
lxml==4.9.3
colorama==0.4.6
tqdm==4.66.1
numpy==1.24.3
matplotlib==3.7.2
seaborn==0.12.2
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

# YouTube Data API (RECOMMENDED - NEW!) - Get from https://console.cloud.google.com/
YOUTUBE_API_KEY=your_actual_youtube_api_key_here

# Last.fm API (RECOMMENDED) - Get from https://www.last.fm/api/account/create
LASTFM_API_KEY=your_actual_lastfm_api_key_here

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

# YouTube Configuration (NEW!)
YOUTUBE_DAILY_QUOTA=10000
YOUTUBE_REQUESTS_PER_MINUTE=100

# Redis (optional - for advanced rate limiting)
REDIS_URL=redis://localhost:6379/0
EOF
```

**Now edit the `.env` file and replace the placeholder values with your actual API keys!**

### Step 3: Install the Application Code (5 minutes)

You'll need to create all the application files. The complete file structure is:

```
precise-digital-leads/
├── run.py                          # Main entry point (updated with YouTube status)
├── cli.py                          # Command line interface (YouTube commands added)
├── requirements.txt                # ✅ Already created (includes YouTube deps)
├── .env                           # ✅ Already created (includes YouTube config)
├── config/
│   ├── __init__.py
│   ├── settings.py                # Configuration management (YouTube config added)
│   └── database.py                # Database setup and models (YouTube fields added)
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py              # Flask API endpoints (YouTube endpoints added)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── pipeline.py            # Main processing pipeline (YouTube integration)
│   │   ├── scoring.py             # Lead scoring engine (YouTube opportunity scoring)
│   │   └── rate_limiter.py        # API rate limiting (YouTube quotas)
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── base_client.py         # API clients base
│   │   ├── musicbrainz.py         # MusicBrainz client
│   │   ├── spotify.py             # Spotify client
│   │   ├── lastfm.py              # Last.fm client
│   │   └── youtube.py             # YouTube client (NEW!)
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py            # Database models
│   └── services/
│       ├── __init__.py
│       └── contact_discovery.py   # Contact discovery service (YouTube contacts added)
└── data/                          # Database files (created automatically)
```

**Important**: You'll need to copy all the code files from the original project documentation. Each file contains specific functionality that makes the system work, including the new YouTube integration.

### Step 4: Initialize and Test (10 minutes)

```bash
# Create necessary directories
mkdir -p config src/api src/core src/integrations src/models src/services data

# Initialize database (now includes YouTube schema)
python cli.py init

# Test API connections including YouTube
python cli.py status

# Test YouTube integration specifically
python cli.py youtube-status

# Test with a sample ISRC including YouTube data
python cli.py analyze USRC17607839 --no-save --verbose --include-youtube

# Start the web server (in another terminal)
python run.py
```

Visit `http://localhost:5000/api/health` to confirm the web interface is working.

---

## 🧪 Testing Your Setup

### Verify API Connections

```bash
# Check all API integrations including YouTube
python cli.py status

# Test YouTube specifically
python cli.py test-youtube "Billie Eilish"

# Check YouTube API configuration
python cli.py youtube-status
```

### Process Your First Leads with YouTube

```bash
# Create test file with sample ISRCs
cat > test_isrcs.txt << 'EOF'
USRC17607839
GBUM71505078
AUUM71801234
EOF

# Process them with YouTube integration
python cli.py bulk test_isrcs.txt --batch-size 3 --include-youtube

# View results with YouTube data
python cli.py leads --tier A --limit 10

# Check YouTube opportunities specifically
python cli.py youtube-opportunities --limit 20

# Get statistics including YouTube metrics
python cli.py stats

# Export to CSV with YouTube data
python cli.py leads --tier A --export high_priority_leads.csv
```

### Test Web API with YouTube

```bash
# Health check (now shows YouTube status)
curl http://localhost:5000/api/health

# Analyze single ISRC with YouTube
curl -X POST http://localhost:5000/api/analyze-isrc \
  -H "Content-Type: application/json" \
  -d '{"isrc": "USRC17607839", "save_to_db": false, "include_youtube": true}'

# Get leads with YouTube filtering
curl "http://localhost:5000/api/leads?youtube_filter=no_channel&limit=5"

# Test YouTube opportunities endpoint
curl "http://localhost:5000/api/youtube/opportunities?limit=10"

# System status with YouTube quotas
curl http://localhost:5000/api/status
```

---

## 📊 Understanding the Enhanced System

### Lead Scoring Algorithm (Updated with YouTube)

The system scores artists on three factors with **enhanced YouTube opportunity assessment**:

#### 1. Independence Score (40% weight)
- **Self-Released**: 40 points
- **Indie Label**: 25 points  
- **Small Distributor**: 15 points
- **Major Label**: 0 points

#### 2. Opportunity Score (40% weight) - **Now includes YouTube assessment**
- **Missing Platforms**: 20 points (not on Spotify, Apple Music, etc.)
- **Basic Distribution**: 15 points (only on major streaming)
- **No Publishing Admin**: 10 points
- **Growing Streams**: 15 points (10K-500K listeners)
- **Recent Activity**: 10 points (released in last 12 months)
- **Low Professional Presence**: 10 points (missing website, social media)
- **🎥 YouTube Opportunities**: Up to 15 points (NEW!)
  - No YouTube presence: 15 points
  - Underperforming YouTube vs Spotify: 5 points
  - Low upload frequency but good following: 5 points
  - Poor video optimization: 3 points
  - High growth potential but small size: 2 points

#### 3. Geographic Score (20% weight)
- **New Zealand**: 30 points
- **Australia**: 25 points
- **Pacific Islands**: 20 points
- **Other English-speaking**: 10 points
- **Other**: 5 points

#### Lead Tiers (Enhanced with YouTube data)
- **Tier A**: 70+ points (High priority) - May include YouTube optimization opportunities
- **Tier B**: 50-69 points (Medium priority) - Often good YouTube growth candidates
- **Tier C**: 30-49 points (Low priority) - May benefit from YouTube presence
- **Tier D**: <30 points (Very low priority)

### **NEW: YouTube Opportunity Types**

The system now identifies these specific YouTube opportunities:

1. **No YouTube Presence** (15 points)
   - Artists with significant Spotify following but no YouTube channel
   - High-value opportunity for channel creation and optimization

2. **Underperforming YouTube** (5 points)
   - YouTube subscribers < 30% of Spotify followers
   - Indicates poor YouTube strategy or optimization

3. **Inconsistent Uploads** (5 points)
   - Good subscriber base but low upload frequency
   - Opportunity for content strategy improvement

4. **Poor Optimization** (3 points)
   - Low view-to-subscriber ratio
   - Suggests need for video optimization services

5. **High Potential Emerging** (2 points)
   - Small but fast-growing channels
   - Early-stage optimization opportunities

### Sample Usage Examples (Updated)

```bash
# Find high-priority New Zealand artists with YouTube opportunities
python cli.py leads --tier A --region new_zealand --youtube-filter no_channel

# Find artists with underperforming YouTube channels
python cli.py leads --youtube-filter underperforming --min-score 60

# Process playlist ISRCs with YouTube data
echo "USRC17607839" > playlist_isrcs.txt
echo "GBUM71505078" >> playlist_isrcs.txt
python cli.py bulk playlist_isrcs.txt --include-youtube

# Export for CRM with YouTube metrics
python cli.py leads --tier A --tier B --export leads_for_crm.csv

# Test YouTube integration for specific artist
python cli.py test-youtube "Lorde"

# Refresh YouTube data for artist ID 123
python cli.py refresh-youtube-data 123
```

---

## 🎯 Practical Usage for Precise Digital

### Daily Lead Generation Workflow (Enhanced)

```bash
# 1. Process new ISRCs discovered from industry sources with YouTube
python cli.py bulk new_isrcs_today.csv --batch-size 20 --include-youtube

# 2. Review high-priority leads including YouTube opportunities
python cli.py leads --tier A --region new_zealand --region australia

# 3. Check YouTube-specific opportunities
python cli.py youtube-opportunities --limit 50

# 4. Export for outreach team with YouTube metrics
python cli.py leads --tier A --export daily_leads_$(date +%Y%m%d).csv

# 5. Check system health including YouTube quotas
python cli.py stats
```

### Finding Specific Types of Artists (Updated)

```bash
# Self-released artists in target regions with no YouTube
python cli.py leads --tier A --tier B --region new_zealand --region australia --youtube-filter no_channel

# Growing artists missing professional services including YouTube optimization
python cli.py leads --min-score 50 --youtube-filter underperforming --limit 50

# Recently active independent artists with YouTube potential
python cli.py leads --tier A --youtube-filter high_potential --export active_independent_artists.csv

# Artists with good Spotify following but missing YouTube presence
python cli.py leads --min-score 60 --youtube-filter no_channel --export youtube_opportunities.csv
```

### Integration with Your CRM (Enhanced)

The CSV exports now include comprehensive YouTube fields:
- Artist Name, Country, Region, Genre
- Comprehensive scoring breakdown including YouTube opportunity assessment
- Contact information (email, website, social media, **YouTube channels**)
- Outreach status tracking
- Monthly listeners and engagement metrics
- **YouTube metrics**: subscribers, total views, video count, upload frequency, growth potential

```bash
# Generate CRM-ready export with YouTube data
python cli.py leads --tier A --tier B --export $(date +%Y%m%d)_crm_leads.csv

# Export YouTube opportunities specifically
python cli.py youtube-opportunities --export youtube_outreach_$(date +%Y%m%d).csv
```

---

## 🚀 Production Deployment

### Option 1: Docker Deployment (Recommended)

```bash
# 1. Create docker-compose.yml (updated with YouTube)
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
      - YOUTUBE_API_KEY=${YOUTUBE_API_KEY}
      - YOUTUBE_DAILY_QUOTA=10000
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

# 2. Create Dockerfile (updated)
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
# Install on Ubuntu/Debian (updated with Python 3.11 for better YouTube API support)
sudo apt update
sudo apt install -y python3.11 python3.11-pip python3.11-venv nginx postgresql

# Deploy to /opt/precise-digital-leads
sudo git clone <your-repo> /opt/precise-digital-leads
cd /opt/precise-digital-leads

# Set up virtual environment
sudo python3.11 -m venv venv
sudo chown -R www-data:www-data .

# Install and configure (includes YouTube dependencies)
sudo -u www-data venv/bin/pip install -r requirements.txt
sudo -u www-data cp .env.example .env
# Edit .env with production values including YouTube API key

# Create systemd service (updated with YouTube status check)
sudo tee /etc/systemd/system/precise-digital.service > /dev/null << 'EOF'
[Unit]
Description=Precise Digital Lead Generation with YouTube Integration
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/precise-digital-leads
ExecStart=/opt/precise-digital-leads/venv/bin/python run.py
Restart=on-failure
RestartSec=5

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

### Customizing YouTube Scoring

```python
# Modify YouTube opportunity weights in src/core/scoring.py
def _assess_youtube_opportunities(self, youtube_data: Dict, spotify_data: Dict) -> int:
    if not youtube_data:
        return 20  # Increased from 15 for higher priority
    
    # Custom scoring logic here
    score = 0
    
    # Your custom YouTube opportunity detection
    # ...
    
    return score
```

### Adding New Endpoints

```python
# Add to src/api/routes.py
@app.route('/api/custom-youtube-endpoint', methods=['GET'])
def custom_youtube_endpoint():
    # Your YouTube-specific implementation
    return jsonify({'result': 'success'})
```

---

## 📊 Monitoring & Maintenance

### Daily Operations (Updated)

```bash
# Morning routine (now includes YouTube status)
python cli.py status           # Check API health including YouTube quotas
python cli.py youtube-status   # Check YouTube-specific status
python cli.py stats            # Review overnight processing with YouTube metrics
python cli.py leads --tier A   # Check high-priority leads
python cli.py youtube-opportunities --limit 20  # Check YouTube opportunities

# Evening routine
./scripts/backup.sh            # Backup database
python cli.py stats            # Daily processing summary with YouTube stats
```

### Performance Monitoring (Enhanced)

```bash
# Check API rate limits including YouTube quotas
curl http://localhost:5000/api/status

# Monitor processing performance
python cli.py stats

# YouTube-specific monitoring
curl http://localhost:5000/api/youtube/stats

# Database health
ls -la data/leads.db           # Check database size
python -c "from config.database import DatabaseManager; db = DatabaseManager(); print(f'Artists: {db.session.query(db.Artist).count()}')"
```

### Troubleshooting (Updated)

#### Common Issues

**YouTube API Issues**
```bash
# Check YouTube configuration
python cli.py youtube-status

# Test YouTube connectivity
python cli.py test-youtube "test artist"

# Check quotas
curl http://localhost:5000/api/status | grep youtube
```

**Spotify Authentication Fails**
```bash
# Check credentials
python -c "from config.settings import settings; print('Client ID configured:', bool(settings.spotify_client_id))"

# Test authentication
python -c "from src.integrations.spotify import spotify_client; print('Token:', bool(spotify_client.access_token))"
```

**Database Issues (Updated Schema)**
```bash
# Check if YouTube migration is needed
python -c "from config.database import check_youtube_migration_needed; print('Migration needed:', check_youtube_migration_needed())"

# Run YouTube migration if needed
python cli.py migrate-youtube

# Reset database (WARNING: Deletes all data)
python cli.py reset
```

**Rate Limiting Issues**
```bash
# Check current status including YouTube
python cli.py status

# Reduce batch sizes
python cli.py bulk file.csv --batch-size 5 --delay 2
```

---

## 🎯 Success Metrics

### Technical Metrics (Updated)
- **API Success Rate**: >95% (check with `python cli.py status`)
- **Processing Speed**: ~25-35 seconds per ISRC (increased due to YouTube data)
- **Data Accuracy**: Spot-check results manually
- **System Uptime**: Monitor with health checks
- **YouTube Coverage**: >60% of artists should have YouTube data when available

### Business Metrics (Enhanced)
- **Lead Quality**: Review Tier A leads manually including YouTube opportunities
- **Contact Discovery**: >70% of leads should have contact info (now including YouTube)
- **Geographic Targeting**: >80% should be in target regions (NZ/AU/Pacific)
- **False Positive Rate**: <20% of Tier A leads should be unsuitable
- **YouTube Opportunity Accuracy**: >85% of identified YouTube opportunities should be valid

### Weekly Review (Updated)

```bash
# Generate weekly report with YouTube metrics
python cli.py stats
python cli.py leads --tier A --export weekly_tier_a_leads.csv
python cli.py leads --region new_zealand --export weekly_nz_leads.csv
python cli.py youtube-opportunities --export weekly_youtube_opportunities.csv

# Review contact discovery effectiveness including YouTube
python cli.py leads --tier A --limit 20 | grep -E "contact_email|website|youtube"

# Review YouTube integration effectiveness
python cli.py youtube-stats
```

---

## 📞 Support & Resources

### Getting Help

1. **Check System Status**: `python cli.py status` and `python cli.py youtube-status`
2. **Review Logs**: Check console output for errors
3. **Test Components**: Use CLI commands to isolate issues
4. **Documentation**: See `/docs` folder for detailed guides

### API Rate Limits (Updated)

| API | Free Tier | Daily Capacity | Notes |
|-----|-----------|----------------|-------|
| Spotify | 100/minute | ~144,000/day | Excellent for high volume |
| **YouTube** | **100/minute** | **10,000/day** | **Good for supplementary data** |
| Last.fm | 5/second | ~432,000/day | Very generous limits |
| MusicBrainz | 1/second | ~86,400/day | Be respectful, it's free |

### Best Practices (Updated)

1. **API Key Security**: Never commit `.env` files, rotate keys regularly including YouTube
2. **Rate Limiting**: The system handles this automatically including YouTube quotas
3. **Data Quality**: Regularly review Tier A leads manually including YouTube opportunities
4. **Backup Strategy**: Daily database backups with `./scripts/backup.sh`
5. **Monitoring**: Set up alerts for processing failures and YouTube quota exhaustion
6. **YouTube Quotas**: Monitor daily usage and plan batch processing accordingly

---

## 🎉 You're Ready!

Your Precise Digital Lead Generation Tool with YouTube Integration is now:

✅ **Fully Configured** - All APIs connected and tested including YouTube  
✅ **Processing ISRCs** - Turning music identifiers into qualified leads with YouTube data  
✅ **Scoring Accurately** - Prioritizing independent artists with YouTube opportunity assessment  
✅ **Finding Contacts** - Discovering email addresses, social media handles, and YouTube channels  
✅ **Export Ready** - Generating CRM-ready lead lists with comprehensive YouTube metrics  
✅ **Production Capable** - Ready to scale with Docker deployment  
✅ **🎥 YouTube Enhanced** - Complete YouTube integration for enhanced lead qualification

### Immediate Next Steps

1. **Process Your First Real Batch with YouTube**: Get ISRCs from industry sources and run them through the system with YouTube integration enabled
2. **Review Tier A Leads and YouTube Opportunities**: Manually validate the quality of high-scoring leads and YouTube opportunities
3. **Export to CRM with YouTube Data**: Generate your first lead export with YouTube metrics for the outreach team
4. **Monitor Performance**: Check `python cli.py stats` and `python cli.py youtube-stats` daily to track progress

### Contact for Support

- **Technical Issues**: Review documentation in `/docs` folder
- **Feature Requests**: Consider extending the system using the provided patterns
- **Business Questions**: Use the lead exports to validate system effectiveness
- **YouTube Integration**: Check `python cli.py youtube-status` for API-specific issues

**The system is designed to continuously improve Precise Digital's lead generation process, helping you identify and prioritize independent artists who are most likely to benefit from your music services, with enhanced focus on YouTube growth opportunities.**

---

**🎥 YouTube Integration adds a powerful new dimension to lead qualification by identifying artists who could benefit from YouTube optimization, channel development, and video marketing services - a rapidly growing area in the music industry.**