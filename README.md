# 🎵 Prism Analytics Engine

> **Transforming Music Data into Actionable Insights**

A comprehensive lead generation tool for independent music services, built by **Precise Digital**. The Prism Analytics Engine analyzes music metadata via ISRCs and other identifiers to identify independent artists who could benefit from professional music services.

---

## 🎯 **Project Overview**

**Precise Digital** (precise.digital) is a New Zealand-based independent music services company founded in 2017, offering:
- Distribution & Publishing
- Rights Management
- Content Creation & YouTube Optimization
- Label Services & Marketing
- Playlist Pitching

The **Prism Analytics Engine** automates the lead generation process by:
- Analyzing audio assets via ISRCs
- Aggregating data from multiple music platforms
- Scoring leads based on independence and opportunity factors
- Discovering contact information for outreach
- Providing YouTube analytics and optimization opportunities

---

## ✨ **Key Features**

### 🔍 **Multi-Source Data Aggregation**
- **MusicBrainz**: Comprehensive music metadata (always available)
- **Spotify Web API**: Streaming data and artist metrics
- **YouTube Data API**: Video analytics and channel insights
- **Last.fm API**: Social listening data and trends

### 📊 **Advanced Lead Scoring**
- **Independence Score** (40%): Self-released vs major label
- **Opportunity Score** (40%): Service gaps and growth potential
- **Geographic Score** (20%): Regional targeting (NZ/AU/Pacific focus)
- **YouTube Opportunities**: Channel optimization potential

### 🎥 **YouTube Integration**
- Channel discovery and analytics
- Subscriber and engagement metrics
- Upload frequency analysis
- Growth potential assessment
- Optimization opportunity identification

### 📈 **Comprehensive Analytics**
- Real-time dashboard with key metrics
- Export capabilities (CSV, Excel, JSON, PDF)
- Contact discovery and CRM integration
- Geographic and genre distribution analysis

### 🔒 **Production-Ready**
- Rate limiting for API protection
- Database persistence with SQLAlchemy
- Docker containerization
- Environment-based configuration
- Comprehensive error handling

---

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+ (3.11 recommended)
- Git
- Modern web browser

### **1. Clone Repository**
```bash
git clone https://github.com/precise-digital/prism-analytics.git
cd prism-analytics
```

### **2. Environment Setup**
```bash
# Copy environment template
cp .env.example .env

# Edit configuration (see Configuration section below)
nano .env
```

### **3. Install Dependencies**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### **4. Database Setup**
```bash
# Initialize database
python -c "from config.database import init_db; init_db()"
```

### **5. Run Application**
```bash
# Development server
python run.py

# Or with validation
python run.py --validate-only  # Check setup
python run.py                  # Start server
```

### **6. Access Application**
- **API Base**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health
- **API Status**: http://localhost:5000/api/status

---

## ⚙️ **Configuration**

### **Required Environment Variables**
```bash
# Security
SECRET_KEY=your-super-secret-key-32-chars-minimum

# API Keys (get from respective platforms)
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
YOUTUBE_API_KEY=your_youtube_api_key        # Optional but recommended
LASTFM_API_KEY=your_lastfm_api_key         # Optional
```

### **API Key Setup**

#### **Spotify Web API** (Required)
1. Visit [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create new app
3. Copy Client ID and Client Secret to `.env`

#### **YouTube Data API** (Recommended)
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Enable YouTube Data API v3
3. Create API key
4. Copy to `.env` as `YOUTUBE_API_KEY`

#### **Last.fm API** (Optional)
1. Visit [Last.fm API](https://www.last.fm/api/account/create)
2. Create API account
3. Copy API key to `.env`

### **Database Configuration**
```bash
# Development (default)
DATABASE_URL=sqlite:///data/precise_leads.db

# Production (PostgreSQL recommended)
DATABASE_URL=postgresql://user:password@localhost:5432/precise_leads
```

---

## 🐳 **Docker Deployment**

### **Quick Start with Docker Compose**
```bash
# Copy environment file
cp .env.example .env

# Configure API keys in .env
nano .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### **Services Included**
- **app**: Main Prism Analytics Engine
- **postgres**: PostgreSQL database
- **redis**: Caching and session storage
- **nginx**: Reverse proxy (optional)
- **worker**: Background processing (optional)
- **monitoring**: Prometheus + Grafana (optional)

### **Production Deployment**
```bash
# Production with monitoring
docker-compose --profile production --profile monitoring up -d

# Scale workers
docker-compose up --scale worker=3 -d
```

---

## 🔌 **API Documentation**

### **Core Endpoints**

#### **Health & Status**
```http
GET /api/health          # System health check
GET /api/status          # Detailed system status
GET /                    # Welcome message with integration status
```

#### **ISRC Analysis**
```http
POST /api/analyze-isrc   # Analyze single ISRC
POST /api/analyze-bulk   # Analyze multiple ISRCs
POST /api/upload-isrcs   # Upload CSV/TXT file with ISRCs
```

#### **Lead Management**
```http
GET  /api/leads                    # Get filtered leads list
GET  /api/artist/{id}              # Get detailed artist info
PUT  /api/artist/{id}/outreach     # Update outreach status
POST /api/export                   # Export leads to various formats
```

#### **YouTube Integration**
```http
POST /api/youtube/test                        # Test YouTube integration
GET  /api/youtube/opportunities               # Get YouTube opportunities
GET  /api/youtube/stats                       # YouTube integration statistics
POST /api/artist/{id}/youtube/refresh         # Refresh artist YouTube data
```

#### **Dashboard & Analytics**
```http
GET /api/dashboard/stats           # Dashboard statistics
```

### **Example API Calls**

#### **Analyze Single ISRC**
```json
POST /api/analyze-isrc
{
  "isrc": "USRC17607839",
  "save_to_db": true,
  "include_youtube": true,
  "force_refresh": false
}
```

#### **Bulk Analysis**
```json
POST /api/analyze-bulk
{
  "isrcs": ["USRC17607839", "GBUM71505078"],
  "batch_size": 10
}
```

#### **Export Leads**
```json
POST /api/export
{
  "filters": {
    "tier": "A",
    "region": "new_zealand",
    "min_score": 70,
    "youtube_filter": "has_channel"
  },
  "format": "excel",
  "include_youtube": true
}
```

---

## 📊 **Lead Scoring System**

### **Scoring Components**

#### **Independence Score (40% weight)**
- **Self-Released** (40 points): Artist releases own music
- **Small Distributor** (35 points): Uses indie distributors
- **Indie Label** (25 points): Small independent label
- **Major Distributed** (0 points): Major label distribution

#### **Opportunity Score (40% weight)**
- **Missing Platforms** (20 points): Not on major streaming services
- **Basic Distribution** (15 points): Limited platform presence
- **No Publishing Admin** (10 points): No publishing representation
- **Growing Streams** (15 points): Increasing listener base
- **Recent Activity** (10 points): Recent releases
- **YouTube Opportunities** (15 points): Optimization potential

#### **Geographic Score (20% weight)**
- **New Zealand** (30 points): Primary target market
- **Australia** (25 points): Secondary target market
- **Pacific Islands** (20 points): Regional expansion
- **Other** (5 points): Lower priority regions

### **Lead Tiers**
- **Tier A** (70+ points): High priority, immediate outreach
- **Tier B** (50-69 points): Medium priority, schedule follow-up
- **Tier C** (30-49 points): Low priority, periodic review
- **Tier D** (<30 points): Very low priority, monitor only

---

## 🎥 **YouTube Integration Features**

### **Channel Discovery**
- Automatic channel identification
- Subscriber and view count analysis
- Upload frequency assessment
- Content strategy evaluation

### **Opportunity Identification**
- **No YouTube Presence**: Artists with Spotify following but no YouTube
- **Underperforming Channels**: Low subscribers relative to streaming success
- **Inconsistent Uploaders**: Channels with good following but poor content strategy
- **High Growth Potential**: Emerging channels with optimization opportunities

### **Analytics & Insights**
- Channel growth trends
- Engagement rate analysis
- Content performance metrics
- Optimization recommendations

---

## 🗂️ **Project Structure**

```
prism-analytics/
├── 📁 src/                          # Main source code
│   ├── 📁 api/                      # Flask API routes
│   │   ├── __init__.py
│   │   └── routes.py                # Main API endpoints
│   ├── 📁 core/                     # Core business logic
│   │   ├── __init__.py
│   │   ├── pipeline.py              # Main processing pipeline
│   │   ├── rate_limiter.py          # API rate limiting
│   │   └── scoring.py               # Lead scoring engine
│   ├── 📁 integrations/             # External API clients
│   │   ├── __init__.py
│   │   ├── base_api.py              # Base API client
│   │   ├── base_client.py           # Client management
│   │   ├── musicbrainz.py           # MusicBrainz client
│   │   ├── spotify.py               # Spotify client
│   │   ├── lastfm.py                # Last.fm client
│   │   └── youtube.py               # YouTube client
│   ├── 📁 services/                 # Business services
│   │   ├── __init__.py
│   │   ├── contact_discovery.py     # Contact information discovery
│   │   ├── data_processor.py        # Data processing utilities
│   │   └── export_service.py        # Data export functionality
│   └── 📁 utils/                    # Utility functions
│       ├── __init__.py
│       ├── helpers.py               # Common utilities
│       ├── startup_validation.py    # System validation
│       └── validators.py            # Input validation
├── 📁 config/                       # Configuration
│   ├── __init__.py
│   ├── database.py                  # Database models & management
│   └── settings.py                  # Application settings
├── 📁 data/                         # Data storage (auto-created)
├── 📁 logs/                         # Application logs (auto-created)
├── 📁 exports/                      # Export files (auto-created)
├── 📁 monitoring/                   # Monitoring configurations
├── 📁 nginx/                        # Nginx configurations
├── run.py                           # Application entry point
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Container configuration
├── docker-compose.yml               # Multi-service setup
├── .env.example                     # Environment template
└── README.md                        # This file
```

---

## 🛠️ **Development**

### **Setup Development Environment**
```bash
# Clone repository
git clone https://github.com/precise-digital/prism-analytics.git
cd prism-analytics

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies including development tools
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Configure API keys
nano .env

# Run validation tests
python src/utils/startup_validation.py --validate-only

# Start development server
python run.py
```

### **Testing**
```bash
# Run comprehensive validation
python run.py test

# Test individual components
python src/core/pipeline.py          # Test pipeline
python src/core/scoring.py           # Test scoring engine
python src/services/export_service.py # Test export functionality
python src/utils/startup_validation.py # Test system validation
```

### **Code Quality**
```bash
# Install development dependencies
pip install black flake8 mypy

# Format code
black src/

# Check code quality
flake8 src/
mypy src/
```

---

## 📈 **Monitoring & Analytics**

### **Built-in Monitoring**
- Health check endpoints
- API rate limit tracking
- Processing statistics
- Database connection monitoring

### **Dashboard Metrics**
- Total leads processed
- Lead tier distribution
- Geographic distribution
- YouTube coverage statistics
- API usage statistics
- Processing performance

### **Optional Monitoring Stack**
```bash
# Start with monitoring
docker-compose --profile monitoring up -d

# Access Grafana dashboard
open http://localhost:3000
# Default: admin/admin

# Access Prometheus
open http://localhost:9090
```

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **API Keys Not Working**
```bash
# Verify API key configuration
python -c "from config.settings import settings; print(settings.validate_configuration())"

# Test specific API
curl "http://localhost:5000/api/youtube/test" -X POST -H "Content-Type: application/json" -d '{"artist_name": "test"}'
```

#### **Database Connection Issues**
```bash
# Check database status
python -c "from config.database import DatabaseManager; dm = DatabaseManager(); print('DB connected')"

# Reset database
rm data/precise_leads.db
python -c "from config.database import init_db; init_db()"
```

#### **Rate Limiting Issues**
```bash
# Check rate limit status
curl http://localhost:5000/api/status

# Reset rate limits (development only)
python -c "from src.core.rate_limiter import rate_limiter; rate_limiter.reset_counters()"
```

### **Debug Mode**
```bash
# Enable debug mode
export FLASK_DEBUG=true
python run.py

# Enable API call debugging
export DEBUG_API_CALLS=true
python run.py
```

### **Performance Issues**
- **Slow API responses**: Check rate limiting and API key quotas
- **High memory usage**: Reduce batch sizes in bulk processing
- **Database slow**: Consider upgrading to PostgreSQL for production

---

## 🚀 **Deployment**

### **Production Checklist**

#### **Environment Configuration**
- [ ] Set strong `SECRET_KEY` (32+ characters)
- [ ] Configure production database (PostgreSQL)
- [ ] Set `FLASK_DEBUG=false`
- [ ] Configure proper `CORS_ORIGINS`
- [ ] Set up monitoring and logging

#### **Security**
- [ ] Use HTTPS in production
- [ ] Secure API keys and rotate regularly
- [ ] Enable proper CORS configuration
- [ ] Set up firewall rules
- [ ] Configure backup strategy

#### **Performance**
- [ ] Use PostgreSQL for database
- [ ] Enable Redis for caching
- [ ] Configure proper worker scaling
- [ ] Set up CDN for static assets
- [ ] Monitor API rate limits

### **Deployment Options**

#### **Docker (Recommended)**
```bash
# Production deployment
docker-compose --profile production up -d
```

#### **Traditional Server**
```bash
# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 "src.api.routes:app"
```

#### **Cloud Platforms**
- **Render**: Use `render.yaml` for easy deployment
- **Heroku**: Includes `Procfile` for Heroku deployment
- **DigitalOcean**: Use Docker deployment
- **AWS/GCP/Azure**: Use container services

---

## 📚 **API Rate Limits**

### **Free Tier Limitations**
- **MusicBrainz**: 1 request/second (be respectful)
- **Spotify**: 100 requests/minute
- **YouTube**: 10,000 quota units/day
- **Last.fm**: 5 requests/second

### **Rate Limiting Strategy**
The system automatically manages rate limits with:
- Request queuing and retry logic
- Exponential backoff for failures
- Distributed rate limiting across APIs
- Graceful degradation when limits reached

---

## 🤝 **Contributing**

### **Development Guidelines**
1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** Pull Request

### **Code Standards**
- Follow PEP 8 Python style guide
- Use type hints where appropriate
- Write comprehensive docstrings
- Include tests for new features
- Update documentation

### **Issue Reporting**
When reporting issues, please include:
- Operating system and Python version
- Complete error messages and stack traces
- Steps to reproduce the issue
- API configuration (without exposing keys)

---

## 📄 **License**

This project is proprietary software owned by **Precise Digital Ltd**.

**All Rights Reserved** - This software is confidential and proprietary to Precise Digital. Unauthorized copying, distribution, or use is strictly prohibited.

For licensing inquiries, contact: [licensing@precise.digital](mailto:licensing@precise.digital)

---

## 📞 **Support & Contact**

### **Precise Digital**
- **Website**: [precise.digital](https://precise.digital)
- **Email**: [contact@precise.digital](mailto:contact@precise.digital)
- **Support**: [support@precise.digital](mailto:support@precise.digital)

### **Technical Support**
- **Documentation**: See this README and inline code documentation
- **API Questions**: [api@precise.digital](mailto:api@precise.digital)
- **Bug Reports**: [bugs@precise.digital](mailto:bugs@precise.digital)

### **Business Inquiries**
- **Partnerships**: [partnerships@precise.digital](mailto:partnerships@precise.digital)
- **Licensing**: [licensing@precise.digital](mailto:licensing@precise.digital)
- **Sales**: [sales@precise.digital](mailto:sales@precise.digital)

---

## 🎵 **About Precise Digital**

**Precise Digital** is New Zealand's premier independent music services company, founded in 2017. We specialize in empowering independent artists and small labels with professional-grade music industry services.

### **Our Services**
- **Digital Distribution** to 200+ streaming platforms
- **Publishing Administration** and rights management
- **YouTube Optimization** and content strategy
- **Marketing & Promotion** campaigns
- **Playlist Pitching** to curated playlists
- **Label Services** for emerging imprints
- **Data Analytics** and performance insights

### **Our Mission**
*Democratizing access to professional music industry services for independent artists worldwide, with a special focus on the New Zealand, Australian, and Pacific music communities.*

---

**Built with ❤️ by the Precise Digital team in New Zealand**

*The Prism Analytics Engine represents our commitment to using technology to discover and support emerging musical talent. Every lead generated helps connect independent artists with the professional services they need to succeed in the modern music industry.*

---

*© 2024 Precise Digital Ltd. All rights reserved. Prism Analytics Engine is a trademark of Precise Digital.*