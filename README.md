# Precise Digital Lead Generation Tool

A comprehensive lead generation system for Precise Digital, designed to identify and score independent artists who could benefit from music services, featuring **YouTube integration** for enhanced opportunity assessment.

## 🎯 Overview

This tool analyzes artists using ISRC identifiers and aggregates data from multiple free APIs to:
- Score artists based on independence level, service opportunities, and geographic location
- **Assess YouTube presence and growth potential** (NEW)
- Discover contact information for outreach including YouTube channels
- Export qualified leads for CRM integration
- Focus on independent artists in NZ/Australia/Pacific region

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Spotify API credentials (required)
- **YouTube Data API key (recommended for full functionality)**
- Last.fm API key (optional but recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd precise-digital-leads
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys including YouTube API key
   ```

5. **Initialize database**
   ```bash
   python cli.py init
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

The application will be available at `http://localhost:5000`

## 📊 API Endpoints

### Core Functionality
- `POST /api/analyze-isrc` - Analyze single ISRC with YouTube integration
- `POST /api/analyze-bulk` - Analyze multiple ISRCs with YouTube data
- `POST /api/upload-isrcs` - Upload CSV/TXT file with ISRCs
- `GET /api/leads` - Get filtered lead list (now with YouTube filters)
- `POST /api/export` - Export leads to CSV with YouTube metrics

### **NEW: YouTube Integration Endpoints**
- `POST /api/youtube/test` - Test YouTube API integration for specific artist
- `GET /api/youtube/opportunities` - Get artists with YouTube opportunities
- `POST /api/artist/{id}/youtube/refresh` - Refresh YouTube data for artist
- `GET /api/youtube/stats` - Get overall YouTube integration statistics

### System Endpoints
- `GET /api/health` - Health check with YouTube status
- `GET /api/status` - System status including YouTube API quotas
- `GET /api/dashboard/stats` - Dashboard statistics with YouTube metrics

## 🎵 How It Works

### 1. Data Collection
- **MusicBrainz**: Track metadata, artist info, release details
- **Spotify Web API**: Popularity metrics, streaming data, follower counts
- **Last.fm**: Social listening data, play counts
- **🎥 YouTube Data API**: Channel analytics, subscriber counts, video performance (NEW)**

### 2. Lead Scoring Algorithm
Artists are scored on three factors with **enhanced YouTube opportunity assessment**:

**Independence Score (40% weight)**
- Self-released: 40 points
- Indie label: 25 points  
- Small distributor: 15 points
- Major label: 0 points

**Opportunity Score (40% weight) - Now includes YouTube assessment**
- Missing from major platforms: 20 points
- Basic distribution only: 15 points
- No publishing admin: 10 points
- Growing streams (10K-500K listeners): 15 points
- Recent activity: 10 points
- **🎥 YouTube opportunities: Up to 15 points**
  - No YouTube presence: 15 points
  - Underperforming YouTube vs Spotify: 5 points
  - Low upload frequency: 5 points
  - Poor optimization: 3 points

**Geographic Score (20% weight)**
- New Zealand: 30 points
- Australia: 25 points
- Pacific Islands: 20 points
- Other English-speaking: 10 points
- Other: 5 points

### 3. Lead Tiers
- **Tier A**: 70+ points (High priority)
- **Tier B**: 50-69 points (Medium priority)
- **Tier C**: 30-49 points (Low priority)
- **Tier D**: <30 points (Very low priority)

### 4. **NEW: YouTube Opportunity Detection**
The system now identifies:
- Artists with Spotify following but no YouTube presence
- YouTube channels underperforming relative to streaming metrics
- Channels with inconsistent upload schedules
- High growth potential channels needing optimization

## 🛠️ Development

### Project Structure
```
precise-digital-leads/
├── src/
│   ├── api/           # Flask API routes (updated with YouTube endpoints)
│   ├── core/          # Main pipeline and scoring (YouTube-enhanced)
│   ├── integrations/  # API clients (including YouTube client)
│   ├── models/        # Database models (YouTube fields added)
│   └── services/      # Business logic (YouTube contact discovery)
├── config/            # Configuration management
├── tests/             # Test suite
└── data/              # SQLite database
```

### Running Tests
```bash
pytest tests/
```

### **NEW: YouTube-Specific Testing**
```bash
# Test YouTube API integration
python cli.py test-youtube "Artist Name"

# Check YouTube integration status
python cli.py youtube-status

# Find YouTube opportunities
python cli.py youtube-opportunities

# Analyze with YouTube data
python cli.py analyze ISRC123456789 --include-youtube
```

## 📈 Usage Examples

### Analyze Single ISRC with YouTube
```bash
curl -X POST http://localhost:5000/api/analyze-isrc \
  -H "Content-Type: application/json" \
  -d '{"isrc": "USRC17607839", "include_youtube": true}'
```

### Get YouTube Opportunities
```bash
curl "http://localhost:5000/api/youtube/opportunities?limit=20"
```

### Filter Leads by YouTube Status
```bash
# Artists with no YouTube presence
curl "http://localhost:5000/api/leads?youtube_filter=no_channel"

# Artists with underperforming YouTube
curl "http://localhost:5000/api/leads?youtube_filter=underperforming"

# Artists with high YouTube potential
curl "http://localhost:5000/api/leads?youtube_filter=high_potential"
```

## 🔧 Configuration

Key environment variables (updated with YouTube):
- `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` - Required for Spotify API
- **`YOUTUBE_API_KEY` - Required for YouTube integration (NEW)**
- `LASTFM_API_KEY` - Optional, improves data quality
- `DATABASE_URL` - Database connection string
- `REDIS_URL` - Redis for rate limiting (optional)

## 📝 Rate Limits

The tool respects all API rate limits:
- MusicBrainz: 1 request/second
- Spotify: 100 requests/minute
- Last.fm: 5 requests/second
- **🎥 YouTube: 100 requests/minute, 10,000/day (NEW)**

## 🎯 Practical Usage for Precise Digital

### Daily Lead Generation Workflow (Updated)

```bash
# 1. Process new ISRCs with YouTube integration
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

### **NEW: YouTube Opportunity Workflows**

```bash
# Find artists missing YouTube presence
python cli.py leads --youtube-filter no_channel --min-score 60

# Find underperforming YouTube channels
python cli.py leads --youtube-filter underperforming --tier A --tier B

# Refresh YouTube data for specific artist
python cli.py refresh-youtube-data 123

# Export YouTube metrics for analysis
python cli.py leads --export youtube_analysis.csv --include-youtube-data
```

## 🚀 Production Deployment

### Docker Deployment (Updated)
The Docker deployment now includes YouTube API configuration:

```yaml
# docker-compose.yml includes YouTube environment variables
services:
  app:
    environment:
      - YOUTUBE_API_KEY=${YOUTUBE_API_KEY}
      - YOUTUBE_DAILY_QUOTA=10000
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### **NEW: Contributing to YouTube Integration**
When working on YouTube features:
- Test with the YouTube API sandbox when possible
- Respect rate limits during development
- Include YouTube fields in database migrations
- Update scoring algorithms that use YouTube data

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🆘 Support

For support and questions:
- Email: cest@precise.digital
- Documentation: See `/docs` folder for detailed guides
- Issues: GitHub Issues page

## 🎥 YouTube Integration Highlights

- **Channel Discovery**: Automatically finds artist YouTube channels
- **Performance Analytics**: Subscriber counts, view metrics, engagement rates
- **Opportunity Assessment**: Identifies underperforming or missing YouTube presence
- **Growth Potential Scoring**: Evaluates upload frequency and channel optimization
- **Contact Discovery**: Includes YouTube channels as contact methods
- **Export Integration**: YouTube metrics included in all lead exports

---

**Version**: 1.1.0 with YouTube Integration  
**Last Updated**: July 2025