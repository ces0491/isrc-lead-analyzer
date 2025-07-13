"""
API client imports and utility functions for music lead generation.
Restructured to completely avoid circular imports.
"""

# Import the base class from the separate module
from .base_api import BaseAPIClient

# Global client variables - will be initialized lazily
musicbrainz_client = None
spotify_client = None
lastfm_client = None
youtube_client = None

def _initialize_clients():
    """Initialize all API clients"""
    global musicbrainz_client, spotify_client, lastfm_client, youtube_client
    
    if musicbrainz_client is not None:
        return  # Already initialized
    
    # Create fallback client class
    class FallbackClient:
        """Fallback client that returns None for all methods"""
        def __init__(self, client_name):
            self.client_name = client_name
            print(f"⚠️  Using fallback client for {client_name}")
        
        def __getattr__(self, name):
            def fallback_method(*args, **kwargs):
                print(f"⚠️  {self.client_name} client not available, returning None")
                return None
            return fallback_method
    
    # Import and initialize each client
    try:
        from .musicbrainz import MusicBrainzClient
        musicbrainz_client = MusicBrainzClient()
        print("✅ MusicBrainz client imported successfully")
    except ImportError as e:
        print(f"⚠️  MusicBrainz client import failed: {e}")
        musicbrainz_client = FallbackClient("MusicBrainz")

    try:
        from .spotify import SpotifyClient
        spotify_client = SpotifyClient()
        print("✅ Spotify client imported successfully")
    except ImportError as e:
        print(f"⚠️  Spotify client import failed: {e}")
        spotify_client = FallbackClient("Spotify")

    try:
        from .lastfm import LastFmClient
        lastfm_client = LastFmClient()
        print("✅ Last.fm client imported successfully")
    except ImportError as e:
        print(f"⚠️  Last.fm client import failed: {e}")
        lastfm_client = FallbackClient("Last.fm")

    try:
        from .youtube import YouTubeClient
        youtube_client = YouTubeClient()
        print("✅ YouTube client imported successfully")
        from config.settings import settings
        if settings.apis['youtube'].api_key:
            print("🎥 YouTube integration: ENABLED with API key")
        else:
            print("🎥 YouTube integration: AVAILABLE but no API key configured")
    except ImportError as e:
        print(f"❌ YouTube client import failed: {e}")
        print("YouTube integration will be disabled")
        youtube_client = FallbackClient("YouTube")
    except Exception as e:
        print(f"⚠️  YouTube client initialization warning: {e}")
        youtube_client = FallbackClient("YouTube")

# Lazy getters for clients
def get_musicbrainz_client():
    _initialize_clients()
    return musicbrainz_client

def get_spotify_client():
    _initialize_clients()
    return spotify_client

def get_lastfm_client():
    _initialize_clients()
    return lastfm_client

def get_youtube_client():
    _initialize_clients()
    return youtube_client

# For backward compatibility, create proxy objects
class LazyClient:
    def __init__(self, getter_func):
        self._getter = getter_func
        self._client = None
    
    def __getattr__(self, name):
        if self._client is None:
            self._client = self._getter()
        return getattr(self._client, name)

# Initialize lazy clients
musicbrainz_client = LazyClient(get_musicbrainz_client)
spotify_client = LazyClient(get_spotify_client)
lastfm_client = LazyClient(get_lastfm_client)
youtube_client = LazyClient(get_youtube_client)

def check_client_availability():
    """Check which clients are available and properly configured"""
    _initialize_clients()  # Ensure clients are initialized
    
    # Get the actual client instances
    mb_client = get_musicbrainz_client()
    sp_client = get_spotify_client()
    lf_client = get_lastfm_client()
    yt_client = get_youtube_client()
    
    status = {
        'musicbrainz': mb_client.__class__.__name__ != 'FallbackClient',
        'spotify': sp_client.__class__.__name__ != 'FallbackClient',
        'lastfm': lf_client.__class__.__name__ != 'FallbackClient',
        'youtube': yt_client.__class__.__name__ != 'FallbackClient'
    }
    
    print("\n📊 API Client Availability:")
    for client, available in status.items():
        icon = "✅" if available else "❌"
        print(f"  {icon} {client.title()}: {'Available' if available else 'Not available'}")
    
    return status

def get_integration_summary():
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

def test_all_integrations():
    """Test all API integrations to ensure they're working"""
    print("\n🧪 Testing API Integrations...")
    
    results = {}
    
    # Test MusicBrainz
    try:
        mb_client = get_musicbrainz_client()
        if mb_client.__class__.__name__ != 'FallbackClient':
            test_result = mb_client.lookup_by_isrc("USRC17607839")
            results['musicbrainz'] = 'working' if test_result is not None else 'api_error'
        else:
            results['musicbrainz'] = 'not_available'
    except Exception as e:
        results['musicbrainz'] = f'error: {str(e)}'
    
    # Test Spotify
    try:
        sp_client = get_spotify_client()
        if sp_client.__class__.__name__ != 'FallbackClient':
            test_result = sp_client.search_artist("test")
            results['spotify'] = 'working' if test_result is not None else 'api_error'
        else:
            results['spotify'] = 'not_available'
    except Exception as e:
        results['spotify'] = f'error: {str(e)}'
    
    # Test Last.fm
    try:
        lf_client = get_lastfm_client()
        if lf_client.__class__.__name__ != 'FallbackClient':
            test_result = lf_client.get_artist_info("test")
            results['lastfm'] = 'working' if test_result is not None else 'api_error'
        else:
            results['lastfm'] = 'not_available'
    except Exception as e:
        results['lastfm'] = f'error: {str(e)}'
    
    # Test YouTube
    try:
        yt_client = get_youtube_client()
        if yt_client.__class__.__name__ != 'FallbackClient':
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

print("✅ Base API client module loaded (lazy initialization)")