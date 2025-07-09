# tests/test_pipeline.py
"""
Test main processing pipeline
"""
import pytest
from unittest.mock import Mock, patch

from src.core.pipeline import LeadAggregationPipeline
from src.core.rate_limiter import RateLimitManager

@pytest.fixture
def pipeline():
    """Pipeline instance for testing"""
    rate_manager = RateLimitManager()
    return LeadAggregationPipeline(rate_manager)

def test_pipeline_initialization(pipeline):
    """Test pipeline initialization"""
    assert pipeline.rate_manager is not None
    assert pipeline.scoring_engine is not None
    assert pipeline.db_manager is not None

@patch('src.integrations.musicbrainz.musicbrainz_client.lookup_by_isrc')
def test_pipeline_isrc_not_found(mock_lookup, pipeline):
    """Test pipeline handling when ISRC is not found"""
    mock_lookup.return_value = None
    
    result = pipeline.process_isrc('INVALID123456', save_to_db=False)
    
    assert result['status'] == 'failed'
    assert 'ISRC not found' in str(result['errors'])

@patch('src.integrations.musicbrainz.musicbrainz_client.lookup_by_isrc')
@patch('src.integrations.spotify.spotify_client.search_artist')
def test_pipeline_successful_processing(mock_spotify, mock_mb, pipeline):
    """Test successful pipeline processing"""
    # Mock MusicBrainz response
    mock_mb.return_value = {
        'track': {'title': 'Test Track', 'musicbrainz_recording_id': 'test-id'},
        'artist': {'name': 'Test Artist', 'musicbrainz_artist_id': 'artist-id'},
        'release': {'release_date': '2024-01-01', 'label': 'Test Label'}
    }
    
    # Mock Spotify response
    mock_spotify.return_value = {
        'spotify_id': 'spotify-test-id',
        'name': 'Test Artist',
        'popularity': 45,
        'followers': 25000
    }
    
    result = pipeline.process_isrc('TEST12345678', save_to_db=False)
    
    assert result['status'] == 'completed'
    assert result['artist_data']['name'] == 'Test Artist'
    assert result['track_data']['title'] == 'Test Track'
    assert 'scores' in result
    assert result['scores']['total_score'] > 0

def test_bulk_processing_validation(pipeline):
    """Test bulk processing validation"""
    # Too many ISRCs
    too_many_isrcs = ['TEST1234567' + str(i) for i in range(1001)]
    result = pipeline.process_bulk(too_many_isrcs)
    
    assert 'error' in result
    assert 'Too many ISRCs' in result['error']

def test_processing_stats(pipeline):
    """Test processing statistics tracking"""
    stats = pipeline.get_processing_stats()
    
    assert 'processed' in stats
    assert 'successful' in stats
    assert 'failed' in stats
    assert 'elapsed_time' in stats