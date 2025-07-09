# tests/conftest.py
"""
Test configuration and fixtures
"""
import pytest
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.database import Base, Artist, Track
from src.core.rate_limiter import RateLimitManager
from config.settings import settings

@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    # Create engine and tables
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    yield session
    
    # Cleanup
    session.close()
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def sample_artist_data():
    """Sample artist data for testing"""
    return {
        'name': 'Test Artist',
        'country': 'NZ',
        'region': 'new_zealand',
        'genre': 'indie pop',
        'monthly_listeners': 25000,
        'musicbrainz_id': 'test-mb-id-123',
        'spotify_id': 'test-spotify-id-456'
    }

@pytest.fixture
def sample_track_data():
    """Sample track data for testing"""
    return {
        'isrc': 'TEST12345678',
        'title': 'Test Track',
        'label': 'Self-Released',
        'release_date': '2024-01-15',
        'duration_ms': 180000,
        'spotify_popularity': 45
    }

@pytest.fixture
def rate_limiter():
    """Rate limiter instance for testing"""
    return RateLimitManager()