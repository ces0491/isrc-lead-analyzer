"""
API client imports and utility functions for music lead generation.
Fixed version with proper type hints to resolve Pylance errors.
"""

from typing import Any, Protocol, Dict, Optional, Union
from .base_api import BaseAPIClient

# Define protocols for type safety
class MusicBrainzClientProtocol(Protocol):
    def lookup_by_isrc(self, isrc: str) -> Optional[Dict[str, Any]]: ...
    def get_artist_details(self, musicbrainz_id: str) -> Optional[Dict[str, Any]]: ...

class SpotifyClientProtocol(Protocol):
    def search_artist(self, artist_name: str) -> Optional[Dict[str, Any]]: ...
    def get_artist_details(self, spotify_id: str) -> Optional[Dict[str, Any]]: ...
    def search_track(self, artist_name: str, track_title: str) -> Optional[Dict[str, Any]]: ...

class LastFmClientProtocol(Protocol):
    def get_artist_info(self, artist_name: str) -> Optional[Dict[str, Any]]: ...
    def get_track_info(self, artist_name: str, track_title: str) -> Optional[Dict[str, Any]]: ...

class YouTubeClientProtocol(Protocol):
    def search_artist_channel(self, artist_name: str) -> Optional[Dict[str, Any]]: ...
    def search_artist_videos(self, artist_name: str, max_results: int) -> list: ...
    def get_channel_analytics(self, channel_id: str) -> Optional[Dict[str, Any]]: ...

# Type alias for any client
ClientType = Union[MusicBrainzClientProtocol, SpotifyClientProtocol, LastFmClientProtocol, YouTubeClientProtocol, 'FallbackClient']

class FallbackClient:
    """Fallback client that returns None for all methods"""
    def __init__(self, client_name: str):
        self.client_name = client_name
        print(f"⚠️  Using fallback client for {client_name}")
    
    def __getattr__(self, name: str) -> Any:
        def fallback_method(*args: Any, **kwargs: Any) -> None:
            print(f"⚠️  {self.client_name} client not available, returning None")
            return None
        return fallback_method

# Global client variables - will be initialized lazily
_musicbrainz_client: Optional[Union[MusicBrainzClientProtocol, FallbackClient]] = None
_spotify_client: Optional[Union[SpotifyClientProtocol, FallbackClient]] = None
_lastfm_client: Optional[Union[LastFmClientProtocol, FallbackClient]] = None
_youtube_client: Optional[Union[YouTubeClientProtocol, FallbackClient]] = None

def _initialize_clients() -> None:
    """Initialize all API clients with guaranteed non-None return values"""
    global _musicbrainz_client, _spotify_client, _lastfm_client, _youtube_client
    
    if _musicbrainz_client is not None:
        return  # Already initialized
    
    # Import and initialize each client with guaranteed fallback
    try:
        from .musicbrainz import MusicBrainzClient
        _musicbrainz_client = MusicBrainzClient()
        print("✅ MusicBrainz client imported successfully")
    except ImportError as e:
        print(f"⚠️  MusicBrainz client import failed: {e}")
        _musicbrainz_client = FallbackClient("MusicBrainz")
    except Exception as e:
        print(f"⚠️  MusicBrainz client initialization error: {e}")
        _musicbrainz_client = FallbackClient("MusicBrainz")

    try:
        from .spotify import SpotifyClient
        _spotify_client = SpotifyClient()
        print("✅ Spotify client imported successfully")
    except ImportError as e:
        print(f"⚠️  Spotify client import failed: {e}")
        _spotify_client = FallbackClient("Spotify")
    except Exception as e:
        print(f"⚠️  Spotify client initialization error: {e}")
        _spotify_client = FallbackClient("Spotify")

    try:
        from .lastfm import LastFmClient
        _lastfm_client = LastFmClient()
        print("✅ Last.fm client imported successfully")
    except ImportError as e:
        print(f"⚠️  Last.fm client import failed: {e}")
        _lastfm_client = FallbackClient("Last.fm")
    except Exception as e:
        print(f"⚠️  Last.fm client initialization error: {e}")
        _lastfm_client = FallbackClient("Last.fm")

    try:
        from .youtube import YouTubeClient
        _youtube_client = YouTubeClient()
        print("✅ YouTube client imported successfully")
        from config.settings import settings
        if settings.apis['youtube'].api_key:
            print("🎥 YouTube integration: ENABLED with API key")
        else:
            print("🎥 YouTube integration: AVAILABLE but no API key configured")
    except ImportError as e:
        print(f"❌ YouTube client import failed: {e}")
        print("YouTube integration will be disabled")
        _youtube_client = FallbackClient("YouTube")
    except Exception as e:
        print(f"⚠️  YouTube client initialization warning: {e}")
        _youtube_client = FallbackClient("YouTube")

# Typed getters that guarantee non-None returns
def get_musicbrainz_client() -> Union[MusicBrainzClientProtocol, FallbackClient]:
    """Get MusicBrainz client - guaranteed to return a client object"""
    _initialize_clients()
    assert _musicbrainz_client is not None, "Client should never be None after initialization"
    return _musicbrainz_client

def get_spotify_client() -> Union[SpotifyClientProtocol, FallbackClient]:
    """Get Spotify client - guaranteed to return a client object"""
    _initialize_clients()
    assert _spotify_client is not None, "Client should never be None after initialization"
    return _spotify_client

def get_lastfm_client() -> Union[LastFmClientProtocol, FallbackClient]:
    """Get Last.fm client - guaranteed to return a client object"""
    _initialize_clients()
    assert _lastfm_client is not None, "Client should never be None after initialization"
    return _lastfm_client

def get_youtube_client() -> Union[YouTubeClientProtocol, FallbackClient]:
    """Get YouTube client - guaranteed to return a client object"""
    _initialize_clients()
    assert _youtube_client is not None, "Client should never be None after initialization"
    return _youtube_client

class LazyClient:
    """Type-safe lazy client wrapper that guarantees proper method access"""
    
    def __init__(self, getter_func: Any, client_type: str):
        self._getter = getter_func
        self._client: Optional[ClientType] = None
        self._client_type = client_type
    
    def __getattr__(self, name: str) -> Any:
        if self._client is None:
            self._client = self._getter()
        
        # This assertion helps Pylance understand the client is never None
        assert self._client is not None, f"{self._client_type} client should never be None"
        
        return getattr(self._client, name)

# Create typed lazy clients that Pylance can understand
musicbrainz_client: Union[MusicBrainzClientProtocol, FallbackClient] = LazyClient(get_musicbrainz_client, "MusicBrainz")  # type: ignore
spotify_client: Union[SpotifyClientProtocol, FallbackClient] = LazyClient(get_spotify_client, "Spotify")  # type: ignore
lastfm_client: Union[LastFmClientProtocol, FallbackClient] = LazyClient(get_lastfm_client, "Last.fm")  # type: ignore
youtube_client: Union[YouTubeClientProtocol, FallbackClient] = LazyClient(get_youtube_client, "YouTube")  # type: ignore

def check_client_availability() -> Dict[str, bool]:
    """Check which clients are available and properly configured"""
    _initialize_clients()  # Ensure clients are initialized
    
    # Get the actual client instances (guaranteed non-None)
    mb_client = get_musicbrainz_client()
    sp_client = get_spotify_client()
    lf_client = get_lastfm_client()
    yt_client = get_youtube_client()
    
    status = {
        'musicbrainz': not isinstance(mb_client, FallbackClient),
        'spotify': not isinstance(sp_client, FallbackClient),
        'lastfm': not isinstance(lf_client, FallbackClient),
        'youtube': not isinstance(yt_client, FallbackClient)
    }
    
    print("\n📊 API Client Availability:")
    for client, available in status.items():
        icon = "✅" if available else "❌"
        print(f"  {icon} {client.title()}: {'Available' if available else 'Not available'}")
    
    return status

def get_integration_summary() -> Dict[str, Dict[str, Any]]:
    """Get a summary of all integrations for dashboard/status"""
    from config.settings import settings
    
    summary = {
        'musicbrainz': {
            'available': True,  # Always available
            'api_key_required': False,
            'api_key_configured': True,
            'description': 'Free music metadata database'
        },
        'spotify': {
            'available': True,
            'api_key_required': True,
            'api_key_configured': bool(settings.spotify_client_id and settings.spotify_client_secret),
            'description': 'Music streaming platform with artist/track data'
        },
        'lastfm': {
            'available': True,
            'api_key_required': True,
            'api_key_configured': bool(settings.apis['lastfm'].api_key),
            'description': 'Social music platform with listening data'
        },
        'youtube': {
            'available': True,
            'api_key_required': True,
            'api_key_configured': bool(settings.apis['youtube'].api_key),
            'description': 'Video platform with channel analytics and engagement data'
        }
    }
    
    return summary

def test_all_integrations() -> Dict[str, str]:
    """Test all API integrations to ensure they're working"""
    print("\n🧪 Testing API Integrations...")
    
    results: Dict[str, str] = {}
    
    # Test MusicBrainz (guaranteed non-None)
    try:
        mb_client = get_musicbrainz_client()
        if not isinstance(mb_client, FallbackClient):
            test_result = mb_client.lookup_by_isrc("USRC17607839")
            results['musicbrainz'] = 'working' if test_result is not None else 'api_error'
        else:
            results['musicbrainz'] = 'not_available'
    except Exception as e:
        results['musicbrainz'] = f'error: {str(e)}'
    
    # Test Spotify (guaranteed non-None)
    try:
        sp_client = get_spotify_client()
        if not isinstance(sp_client, FallbackClient):
            test_result = sp_client.search_artist("test")
            results['spotify'] = 'working' if test_result is not None else 'api_error'
        else:
            results['spotify'] = 'not_available'
    except Exception as e:
        results['spotify'] = f'error: {str(e)}'
    
    # Test Last.fm (guaranteed non-None)
    try:
        lf_client = get_lastfm_client()
        if not isinstance(lf_client, FallbackClient):
            test_result = lf_client.get_artist_info("test")
            results['lastfm'] = 'working' if test_result is not None else 'api_error'
        else:
            results['lastfm'] = 'not_available'
    except Exception as e:
        results['lastfm'] = f'error: {str(e)}'
    
    # Test YouTube (guaranteed non-None)
    try:
        yt_client = get_youtube_client()
        if not isinstance(yt_client, FallbackClient):
            test_result = yt_client.search_artist_channel("test")
            results['youtube'] = 'working' if test_result is not None else 'api_error'
        else:
            results['youtube'] = 'not_available'
    except Exception as e:
        results['youtube'] = f'error: {str(e)}'
    
    # Print results
    for api, status in results.items():
        if status == 'working':
            print(f"  ✅ {api.title()}: Working")
        elif status == 'not_available':
            print(f"  ❌ {api.title()}: Not available")
        elif status == 'api_error':
            print(f"  ⚠️  {api.title()}: API error (check configuration)")
        else:
            print(f"  ❌ {api.title()}: {status}")
    
    return results

# Export everything for backward compatibility
__all__ = [
    'BaseAPIClient',
    'musicbrainz_client',
    'spotify_client',
    'lastfm_client',
    'youtube_client',
    'check_client_availability',
    'get_integration_summary',
    'test_all_integrations'
]

print("✅ Base API client module loaded with type safety")