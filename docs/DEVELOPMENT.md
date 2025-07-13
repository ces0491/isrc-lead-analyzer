# Development Guide

## Setting Up Development Environment

### Prerequisites
- Python 3.8 or higher
- Git
- Text editor/IDE (VS Code recommended)
- **YouTube Data API access** (NEW)

### Installation Steps

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

3. **Install dependencies (now includes YouTube client)**
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

4. **Set up environment variables with YouTube**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys including YouTube Data API key
   ```

5. **Initialize database (includes YouTube schema)**
   ```bash
   python cli.py init
   
   # Verify YouTube migration is applied
   python cli.py youtube-status
   ```

## Project Structure (Updated)

```
precise-digital-leads/
├── src/                    # Main source code
│   ├── api/               # Flask API routes (YouTube endpoints added)
│   ├── core/              # Core business logic (YouTube scoring added)
│   ├── integrations/      # External API clients (YouTube client added)
│   ├── models/            # Database models (YouTube fields added)
│   ├── services/          # Business services (YouTube contact discovery)
│   └── utils/             # Utility functions
├── config/                # Configuration files (YouTube settings added)
├── tests/                 # Test suite (YouTube tests added)
├── docs/                  # Documentation (YouTube features documented)
├── scripts/               # Deployment/utility scripts (YouTube monitoring)
└── data/                  # SQLite database (YouTube tables included)
```

## Development Workflow

### Running the Application
```bash
# Start development server (includes YouTube integration)
python run.py

# Or use the CLI
python cli.py serve
```

### Running Tests (Updated)
```bash
# Run all tests including YouTube integration tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run YouTube-specific tests
pytest tests/test_youtube_integration.py

# Run with coverage including YouTube code
pytest --cov=src tests/

# Run tests in verbose mode
pytest -v
```

### **NEW: YouTube Development Commands**
```bash
# Test YouTube API connectivity
python cli.py test-youtube "Artist Name"

# Check YouTube integration status
python cli.py youtube-status

# Find YouTube opportunities
python cli.py youtube-opportunities --limit 10

# Refresh YouTube data for artist
python cli.py refresh-youtube-data 123

# Run YouTube migration
python cli.py migrate-youtube

# Test YouTube scoring specifically
python -c "from src.core.scoring import test_youtube_scoring; test_youtube_scoring()"
```

### Code Quality

#### Formatting
```bash
# Format code with Black (includes YouTube modules)
black src/ tests/

# Check formatting
black --check src/ tests/
```

#### Linting
```bash
# Lint with flake8 (includes YouTube code)
flake8 src/ tests/

# Fix common issues
autopep8 --in-place --recursive src/
```

#### Type Checking (Optional)
```bash
# Install mypy
pip install mypy

# Run type checking including YouTube types
mypy src/ --ignore-missing-imports
```

### Database Management (Updated)

#### Using CLI Commands
```bash
# Initialize database with YouTube schema
python cli.py init

# Reset database (WARNING: Deletes all data including YouTube data)
python cli.py reset

# Run YouTube schema migration
python cli.py migrate-youtube

# Check if YouTube migration is needed
python -c "from config.database import check_youtube_migration_needed; print(check_youtube_migration_needed())"

# View statistics including YouTube metrics
python cli.py stats

# Check system status including YouTube
python cli.py status
```

#### Database Migrations
When modifying database models including YouTube fields:

1. Update models in `config/database.py`
2. Create migration function if needed (see `migrate_youtube_fields()` example)
3. Test changes with a fresh database:
   ```bash
   python cli.py reset
   python cli.py init
   ```
4. Update any affected tests including YouTube-related tests

### Adding New Features

#### Adding a New API Endpoint
1. Add route function in `src/api/routes.py`
2. Add corresponding tests in `tests/test_api.py`
3. Update API documentation in `docs/API.md`

**Example: Adding YouTube-specific endpoint**
```python
# In src/api/routes.py
@app.route('/api/youtube/custom-analysis', methods=['POST'])
def custom_youtube_analysis():
    """Custom YouTube analysis endpoint"""
    data = request.get_json()
    artist_name = data.get('artist_name')
    
    from src.integrations.youtube import youtube_client
    result = youtube_client.search_artist_channel(artist_name)
    
    return jsonify({
        'artist_name': artist_name,
        'youtube_data': result,
        'analysis': 'custom analysis here'
    })

# In tests/test_api.py
def test_custom_youtube_analysis(client):
    """Test custom YouTube analysis endpoint"""
    response = client.post('/api/youtube/custom-analysis',
                          json={'artist_name': 'Test Artist'},
                          content_type='application/json')
    assert response.status_code == 200
```

#### Adding a New API Integration
1. Create client class in `src/integrations/`
2. Follow the pattern from existing clients (especially `youtube.py`)
3. Add rate limiting configuration in `config/settings.py`
4. Add tests in `tests/test_integrations.py`

**Example: New music platform integration**
```python
# src/integrations/new_platform.py
from .base_api import BaseAPIClient

class NewPlatformClient(BaseAPIClient):
    def __init__(self):
        super().__init__('new_platform')
    
    def get_artist_data(self, artist_name):
        # Implementation similar to YouTube client
        pass

# config/settings.py
'new_platform': APIConfig(
    name='new_platform',
    base_url='https://api.newplatform.com/',
    requests_per_minute=100,
    api_key=os.getenv('NEW_PLATFORM_API_KEY')
)
```

#### Modifying Scoring Algorithm (YouTube Enhanced)
1. Update `src/core/scoring.py`
2. Add/modify tests in `tests/test_scoring.py`
3. Test with sample data using CLI:
   ```bash
   python cli.py test-scoring "Sample Artist"
   ```

**Example: Extending YouTube opportunity scoring**
```python
# In src/core/scoring.py
def _assess_youtube_opportunities(self, youtube_data: Dict, spotify_data: Dict) -> int:
    """Extended YouTube opportunity assessment"""
    if not youtube_data:
        return 15  # No YouTube presence
    
    score = 0
    channel = youtube_data.get('channel', {})
    
    # Your custom YouTube scoring logic
    subscriber_count = self._safe_int(channel.get('statistics', {}).get('subscriber_count', 0))
    spotify_followers = self._safe_int(spotify_data.get('followers', 0))
    
    # Custom opportunity detection
    if spotify_followers > 50000 and subscriber_count < spotify_followers * 0.2:
        score += 10  # Major underperformance
    
    return score
```

### Debugging

#### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# YouTube-specific logging
logging.getLogger('src.integrations.youtube').setLevel(logging.DEBUG)
```

#### Database Debugging
```bash
# Enable SQL query logging including YouTube tables
export DATABASE_ECHO=true

# Check YouTube schema specifically
python -c "from config.database import check_youtube_migration_needed; print('Migration needed:', check_youtube_migration_needed())"
```

#### API Debugging
```bash
# Test individual endpoints including YouTube
curl -X POST http://localhost:5000/api/analyze-isrc \
  -H "Content-Type: application/json" \
  -d '{"isrc": "USRC17607839", "save_to_db": false, "include_youtube": true}'

# Test YouTube endpoints specifically
curl -X POST http://localhost:5000/api/youtube/test \
  -H "Content-Type: application/json" \
  -d '{"artist_name": "Test Artist"}'
```

#### **NEW: YouTube-Specific Debugging**
```bash
# Test YouTube API connectivity
python cli.py test-youtube "Billie Eilish"

# Check YouTube quota usage
curl http://localhost:5000/api/youtube/stats

# Debug YouTube client directly
python -c "
from src.integrations.youtube import youtube_client;
result = youtube_client.search_artist_channel('test');
print('Result:', result)
"

# Check YouTube rate limiting
python -c "
from src.core.rate_limiter import rate_limiter;
status = rate_limiter.get_rate_limit_status();
print('YouTube status:', status.get('youtube'))
"
```

### Performance Optimization

#### Database Optimization (Enhanced for YouTube)
- Add indexes for frequently queried fields including YouTube fields
- Use pagination for large result sets
- Consider using database connection pooling for high load
- **Optimize YouTube table queries with proper indexing** (NEW)

```sql
-- Example YouTube-specific indexes
CREATE INDEX idx_artists_youtube_channel_id ON artists(youtube_channel_id);
CREATE INDEX idx_artists_youtube_subscribers ON artists(youtube_subscribers);
CREATE INDEX idx_artists_youtube_growth_potential ON artists(youtube_growth_potential);
```

#### API Rate Limiting (Enhanced)
- Monitor rate limit status with `/api/status` including YouTube quotas
- Adjust batch sizes based on API limits including YouTube daily quotas
- Implement exponential backoff for failed requests
- **Plan YouTube API usage to stay within daily quotas** (NEW)

#### Caching (Enhanced)
- Cache API responses for repeated requests including YouTube data
- Use Redis for session storage in production
- Cache expensive calculations including YouTube analytics
- **Cache YouTube data for 24 hours to reduce API calls** (NEW)

```python
# Example YouTube caching strategy
import time
from functools import wraps

def cache_youtube_data(expiry_hours=24):
    def decorator(func):
        cache = {}
        @wraps(func)
        def wrapper(artist_name):
            now = time.time()
            if artist_name in cache:
                data, timestamp = cache[artist_name]
                if now - timestamp < expiry_hours * 3600:
                    return data
            
            result = func(artist_name)
            cache[artist_name] = (result, now)
            return result
        return wrapper
    return decorator

@cache_youtube_data(24)
def get_youtube_data_cached(artist_name):
    from src.integrations.youtube import youtube_client
    return youtube_client.search_artist_channel(artist_name)
```

### Testing Strategy

#### Unit Tests (Updated)
- Test individual functions and classes including YouTube components
- Mock external API calls including YouTube API
- Test edge cases and error conditions including YouTube API failures

**Example: YouTube unit test**
```python
# tests/test_youtube_integration.py
import pytest
from unittest.mock import Mock, patch
from src.integrations.youtube import YouTubeClient

@patch('src.integrations.youtube.youtube_client.rate_limiter')
def test_youtube_search_artist_channel(mock_rate_limiter):
    """Test YouTube artist channel search"""
    mock_response = {
        'items': [{
            'snippet': {
                'channelId': 'UC123456789',
                'title': 'Test Artist',
                'description': 'Test Description'
            }
        }]
    }
    mock_rate_limiter.make_request.return_value = mock_response
    
    client = YouTubeClient()
    result = client.search_artist_channel('Test Artist')
    
    assert result is not None
    assert result['channel_id'] == 'UC123456789'
    assert result['title'] == 'Test Artist'
```

#### Integration Tests (Enhanced)
- Test API endpoints end-to-end including YouTube endpoints
- Test database operations including YouTube schema
- Test external API integrations with mocks including YouTube

#### Performance Tests (Enhanced)
```bash
# Test bulk processing performance with YouTube
python cli.py bulk sample_isrcs.csv --batch-size 5 --include-youtube

# Test YouTube API performance
time python cli.py test-youtube "Popular Artist"

# Monitor YouTube quota usage during testing
python -c "
from src.core.rate_limiter import rate_limiter;
import time;
for i in range(5):
    status = rate_limiter.get_rate_limit_status();
    print(f'YouTube quota: {status.get(\"youtube\", {}).get(\"requests_today\", 0)}');
    time.sleep(1)
"
```

### Git Workflow

#### Branch Naming (Updated)
- `feature/description` - New features including YouTube features
- `feature/youtube-enhancement` - YouTube-specific features
- `bugfix/description` - Bug fixes including YouTube-related bugs
- `hotfix/description` - Critical fixes

#### Commit Messages (Updated)
Follow conventional commits format:
```
feat: add YouTube channel discovery
feat(youtube): implement growth potential scoring
fix: handle YouTube API rate limiting gracefully
fix(youtube): resolve quota exhaustion error handling
docs: update API documentation with YouTube endpoints
test: add YouTube integration tests
```

#### Pull Request Process (Updated)
1. Create feature branch from main
2. Implement changes with tests including YouTube tests
3. Update documentation if needed including YouTube features
4. Ensure all tests pass including YouTube integration tests
5. Submit pull request with description including YouTube impact

### Environment-Specific Configurations

#### Development (Updated)
```env
FLASK_ENV=development
FLASK_DEBUG=true
DATABASE_ECHO=true
YOUTUBE_API_KEY=your_dev_youtube_key
YOUTUBE_DAILY_QUOTA=1000  # Lower quota for dev
```

#### Testing (Updated)
```env
FLASK_ENV=testing
FLASK_DEBUG=false
DATABASE_URL=sqlite:///test.db
YOUTUBE_API_KEY=test_key_or_mock
MOCK_YOUTUBE_RESPONSES=true
```

#### Production (Updated)
```env
FLASK_ENV=production
FLASK_DEBUG=false
DATABASE_URL=postgresql://user:pass@host/db
YOUTUBE_API_KEY=your_prod_youtube_key
YOUTUBE_DAILY_QUOTA=10000
YOUTUBE_QUOTA_WARNING_THRESHOLD=8000
```

## **NEW: YouTube Development Guidelines**

### YouTube API Best Practices
1. **Quota Management**: Always check quota before making batch requests
2. **Error Handling**: Implement proper handling for quota exhaustion and rate limits
3. **Caching**: Cache YouTube data to minimize API calls
4. **Testing**: Use mock responses for testing to avoid quota usage
5. **Monitoring**: Log YouTube API usage for debugging and optimization

### YouTube Data Quality
1. **Channel Matching**: Implement fuzzy matching for artist names
2. **Data Validation**: Validate YouTube statistics before storing
3. **Update Frequency**: Refresh YouTube data based on channel activity
4. **Edge Cases**: Handle channels with private statistics or restricted access

### YouTube Scoring Development
1. **A/B Testing**: Test scoring algorithm changes with known artists
2. **Threshold Tuning**: Adjust opportunity thresholds based on business goals
3. **Feedback Loop**: Use outreach success rates to refine scoring
4. **Documentation**: Document all YouTube scoring factors clearly

### YouTube Testing Strategies
```python
# Example mock for YouTube testing
@pytest.fixture
def mock_youtube_response():
    return {
        'channel': {
            'channel_id': 'UC123456789',
            'title': 'Test Artist Official',
            'statistics': {
                'subscriber_count': 15000,
                'view_count': 500000,
                'video_count': 25
            }
        },
        'analytics': {
            'recent_activity': {
                'upload_frequency': 'active'
            },
            'growth_potential': 'high_potential'
        }
    }

def test_youtube_scoring_with_mock(mock_youtube_response):
    """Test YouTube scoring with mocked data"""
    from src.core.scoring import LeadScoringEngine
    
    engine = LeadScoringEngine()
    artist_data = {
        'youtube_data': mock_youtube_response,
        'spotify_data': {'followers': 50000},
        # ... other test data
    }
    
    scores = engine.calculate_scores(artist_data)
    assert 'youtube' in str(scores['scoring_breakdown']['opportunity']['factors'])
```

## Development Troubleshooting

### Common YouTube Development Issues

**YouTube API Key Issues**
```bash
# Check API key configuration
python -c "from config.settings import settings; print('YouTube key configured:', bool(settings.apis['youtube'].api_key))"

# Test API key validity
python cli.py youtube-status
```

**YouTube Quota Exhaustion During Development**
```bash
# Check current quota usage
curl http://localhost:5000/api/youtube/stats

# Switch to mock mode for testing
export MOCK_YOUTUBE_RESPONSES=true
```

**YouTube Data Schema Issues**
```bash
# Check if YouTube migration is needed
python -c "from config.database import check_youtube_migration_needed; print('Migration needed:', check_youtube_migration_needed())"

# Run migration
python cli.py migrate-youtube

# Verify schema
python -c "from config.database import Artist; print([col.name for col in Artist.__table__.columns if 'youtube' in col.name])"
```

### Debugging YouTube Integration
```python
# Debug YouTube client step by step
from src.integrations.youtube import youtube_client
from config.settings import settings

print("API Key configured:", bool(settings.apis['youtube'].api_key))

# Test basic search
result = youtube_client.search_artist_channel("test")
print("Search result:", result)

# Check rate limiter
from src.core.rate_limiter import rate_limiter
status = rate_limiter.get_rate_limit_status()
print("YouTube rate limit status:", status.get('youtube'))
```

## Contributing YouTube Features

When contributing YouTube-related features:

1. **Follow Existing Patterns**: Use the same structure as other API integrations
2. **Add Comprehensive Tests**: Include unit tests, integration tests, and mock responses
3. **Document Everything**: Update all relevant documentation
4. **Consider Quotas**: Design features to be quota-efficient
5. **Handle Errors Gracefully**: Implement proper error handling for API failures
6. **Test Edge Cases**: Test with artists who have no YouTube presence, private channels, etc.

### Example Contribution Checklist
- [ ] Feature implemented following existing patterns
- [ ] Unit tests added with mocks
- [ ] Integration tests added
- [ ] Documentation updated (API docs, README, etc.)
- [ ] Error handling implemented
- [ ] Quota usage optimized
- [ ] Edge cases tested
- [ ] CLI commands added if applicable
- [ ] Database migrations created if needed
- [ ] Performance impact assessed

---

This development guide now provides comprehensive coverage of YouTube integration development, ensuring contributors can effectively work with the enhanced system while following best practices for API usage, testing, and code quality.