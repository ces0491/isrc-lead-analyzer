# Precise Digital Lead Generation Tool

A comprehensive lead generation system for Precise Digital, designed to identify and score independent artists who could benefit from music services.

## 🎯 Overview

This tool analyzes artists using ISRC identifiers and aggregates data from multiple free APIs to:
- Score artists based on independence level, service opportunities, and geographic location
- Discover contact information for outreach
- Export qualified leads for CRM integration
- Focus on independent artists in NZ/Australia/Pacific region

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Spotify API credentials (required)
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
   # Edit .env with your API keys
   ```

5. **Initialize database**
   ```bash
   python -c "from config.database import init_db; init_db()"
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

The application will be available at `http://localhost:5000`

## 📊 API Endpoints

### Core Functionality
- `POST /api/analyze-isrc` - Analyze single ISRC
- `POST /api/analyze-bulk` - Analyze multiple ISRCs
- `POST /api/upload-isrcs` - Upload CSV/TXT file with ISRCs
- `GET /api/leads` - Get filtered lead list
- `POST /api/export` - Export leads to CSV

### System Endpoints
- `GET /api/health` - Health check
- `GET /api/status` - System status and rate limits
- `GET /api/dashboard/stats` - Dashboard statistics

## 🎵 How It Works

### 1. Data Collection
- **MusicBrainz**: Track metadata, artist info, release details
- **Spotify Web API**: Popularity metrics, streaming data, follower counts
- **Last.fm**: Social listening data, play counts

### 2. Lead Scoring Algorithm
Artists are scored on three factors:

**Independence Score (40% weight)**
- Self-released: 40 points
- Indie label: 25 points  
- Small distributor: 15 points
- Major label: 0 points

**Opportunity Score (40% weight)**
- Missing from major platforms: 20 points
- Basic distribution only: 15 points
- No publishing admin: 10 points
- Growing streams (10K-500K listeners): 15 points
- Recent activity: 10 points
- Low professional presence: 10 points

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

## 🛠️ Development

### Project Structure
```
precise-digital-leads/
├── src/
│   ├── api/           # Flask API routes
│   ├── core/          # Main pipeline and scoring
│   ├── integrations/  # API clients
│   ├── models/        # Database models
│   └── services/      # Business logic
├── config/            # Configuration management
├── tests/             # Test suite
└── data/              # SQLite database
```

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/ tests/
flake8 src/ tests/
```

## 📈 Usage Examples

### Analyze Single ISRC
```bash
curl -X POST http://localhost:5000/api/analyze-isrc \
  -H "Content-Type: application/json" \
  -d '{"isrc": "USRC17607839"}'
```

### Bulk Analysis
```bash
curl -X POST http://localhost:5000/api/analyze-bulk \
  -H "Content-Type: application/json" \
  -d '{"isrcs": ["USRC17607839", "GBUM71505078"]}'
```

### Get High-Priority NZ Leads
```bash
curl "http://localhost:5000/api/leads?tier=A&region=new_zealand&limit=20"
```

## 🔧 Configuration

Key environment variables:
- `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` - Required for Spotify API
- `LASTFM_API_KEY` - Optional, improves data quality
- `DATABASE_URL` - Database connection string
- `REDIS_URL` - Redis for rate limiting (optional)

## 📝 Rate Limits

The tool respects all API rate limits:
- MusicBrainz: 1 request/second
- Spotify: 100 requests/minute
- Last.fm: 5 requests/second
- YouTube: 10,000 requests/day

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🆘 Support

For support and questions:
- Email: cest@precise.digital
- Documentation: See `/docs` folder
- Issues: GitHub Issues page

---