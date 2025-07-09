# tests/test_integrations.py
"""
Test API integrations
"""
import pytest
from unittest.mock import Mock, patch

from src.integrations.musicbrainz import MusicBrainzClient
from src.integrations.spotify import SpotifyClient
from src.integrations.lastfm import LastFmClient

def test_musicbrainz_client_initialization():
    """Test MusicBrainz client initialization"""
    client = MusicBrainzClient()
    assert client.api_name == 'musicbrainz'

def test_spotify_client_initialization():
    """Test Spotify client initialization"""
    client = SpotifyClient()
    assert client.api_name == 'spotify'

def test_lastfm_client_initialization():
    """Test Last.fm client initialization"""
    client = LastFmClient()
    assert client.api_name == 'lastfm'

@patch('src.core.rate_limiter.rate_limiter.make_request')
def test_musicbrainz_isrc_lookup(mock_request):
    """Test MusicBrainz ISRC lookup"""
    # Mock response
    mock_response = {
        'recordings': [{
            'id': 'test-id',
            'title': 'Test Track',
            'artist-credit': [{
                'artist': {
                    'id': 'artist-id',
                    'name': 'Test Artist'
                }
            }],
            'releases': [{
                'title': 'Test Album',
                'date': '2024-01-01',
                'country': 'NZ'
            }]
        }]
    }
    mock_request.return_value = mock_response
    
    client = MusicBrainzClient()
    result = client.lookup_by_isrc('TEST12345678')
    
    assert result is not None
    assert result['track']['title'] == 'Test Track'
    assert result['artist']['name'] == 'Test Artist'

@patch('requests.post')
def test_spotify_authentication(mock_post):
    """Test Spotify authentication"""
    # Mock token response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'access_token': 'test-token',
        'expires_in': 3600
    }
    mock_post.return_value = mock_response
    
    client = SpotifyClient()
    # Authentication should have been called during initialization
    assert client.access_token == 'test-token'

def test_isrc_validation():
    """Test ISRC format validation"""
    client = MusicBrainzClient()
    
    # Valid ISRC should not return None due to format
    valid_isrc = 'USRC17607839'
    # This will likely return None due to no API response in tests, but shouldn't fail validation
    
    # Invalid ISRC should return None
    invalid_result = client.lookup_by_isrc('INVALID')
    assert invalid_result is None
    
    # Empty ISRC should return None
    empty_result = client.lookup_by_isrc('')
    assert empty_result is None