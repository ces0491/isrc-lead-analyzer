# docs/DEVELOPMENT.md

# Development Guide

## Setting Up Development Environment

### Prerequisites
- Python 3.8 or higher
- Git
- Text editor/IDE (VS Code recommended)

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

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Initialize database**
   ```bash
   python cli.py init
   ```

## Project Structure

```
precise-digital-leads/
├── src/                    # Main source code
│   ├── api/               # Flask API routes
│   ├── core/              # Core business logic
│   ├── integrations/      # External API clients
│   ├── models/            # Database models
│   ├── services/          # Business services
│   └── utils/             # Utility functions
├── config/                # Configuration files
├── tests/                 # Test suite
├── docs/                  # Documentation
├── scripts/               # Deployment/utility scripts
└── data/                  # SQLite database (created at runtime)
```

## Development Workflow

### Running the Application
```bash
# Start development server
python run.py

# Or use the CLI
python cli.py serve
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=src tests/

# Run tests in verbose mode
pytest -v
```

### Code Quality

#### Formatting
```bash
# Format code with Black
black src/ tests/

# Check formatting
black --check src/ tests/
```

#### Linting
```bash
# Lint with flake8
flake8 src/ tests/

# Fix common issues
autopep8 --in-place --recursive src/
```

#### Type Checking (Optional)
```bash
# Install mypy
pip install mypy

# Run type checking
mypy src/
```

### Database Management

#### Using CLI Commands
```bash
# Initialize database
python cli.py init

# Reset database (WARNING: Deletes all data)
python cli.py reset

# View statistics
python cli.py stats

# Check system status
python cli.py status
```

#### Database Migrations
When modifying database models:

1. Update models in `src/models/database.py`
2. Test changes with a fresh database:
   ```bash
   python cli.py reset
   python cli.py init
   ```
3. Update any affected tests

### Adding New Features

#### Adding a New API Endpoint
1. Add route function in `src/api/routes.py`
2. Add corresponding tests in `tests/test_api.py`
3. Update API documentation in `docs/API.md`

#### Adding a New API Integration
1. Create client class in `src/integrations/`
2. Follow the pattern from existing clients
3. Add rate limiting configuration in `config/settings.py`
4. Add tests in `tests/test_integrations.py`

#### Modifying Scoring Algorithm
1. Update `src/core/scoring.py`
2. Add/modify tests in `tests/test_scoring.py`
3. Test with sample data using CLI:
   ```bash
   python cli.py test-scoring "Sample Artist"
   ```

### Debugging

#### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Database Debugging
```bash
# Enable SQL query logging
export DATABASE_ECHO=true
```

#### API Debugging
```bash
# Test individual endpoints
curl -X POST http://localhost:5000/api/analyze-isrc \
  -H "Content-Type: application/json" \
  -d '{"isrc": "USRC17607839", "save_to_db": false}'
```

### Performance Optimization

#### Database Optimization
- Add indexes for frequently queried fields
- Use pagination for large result sets
- Consider using database connection pooling for high load

#### API Rate Limiting
- Monitor rate limit status with `/api/status`
- Adjust batch sizes based on API limits
- Implement exponential backoff for failed requests

#### Caching
- Cache API responses for repeated requests
- Use Redis for session storage in production
- Cache expensive calculations

### Testing Strategy

#### Unit Tests
- Test individual functions and classes
- Mock external API calls
- Test edge cases and error conditions

#### Integration Tests
- Test API endpoints end-to-end
- Test database operations
- Test external API integrations (with mocks)

#### Performance Tests
```bash
# Test bulk processing performance
python cli.py bulk sample_isrcs.csv --batch-size 5
```

### Git Workflow

#### Branch Naming
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical fixes

#### Commit Messages
Follow conventional commits format:
```
feat: add contact discovery service
fix: handle missing artist data gracefully
docs: update API documentation
test: add scoring algorithm tests
```

#### Pull Request Process
1. Create feature branch from main
2. Implement changes with tests
3. Update documentation if needed
4. Ensure all tests pass
5. Submit pull request with description

### Environment-Specific Configurations

#### Development
```env
FLASK_ENV=development
FLASK_DEBUG=true
DATABASE_ECHO=true
```

#### Testing
```env
FLASK_ENV=testing
FLASK_DEBUG=false
DATABASE_URL=sqlite:///test.db
```

#### Production
```env
FLASK_ENV=production
FLASK_DEBUG=false
DATABASE_URL=postgresql://user:pass@host/db
```

---