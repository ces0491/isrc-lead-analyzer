"""
Complete base API client with YouTube integration for music lead generation.
Precise Digital - Music Services Lead Generation Tool

This module provides the base class for all API clients and imports
all specific client implementations including YouTube for full integration.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote
from src.core.rate_limiter import rate_limiter
from config.settings import settings


class BaseAPIClient:
    """Base class for API clients with common functionality"""
    
    def __init__(self, api_name: str):
        self.api_name = api_name
        self.rate_limiter = rate_limiter
    
    def _normalize_country_code(self, country: Optional[str]) -> Optional[str]:
        """Normalize country codes and names"""
        if not country:
            return None
        
        country = country.upper().strip()
        
        # Map common variations to standard codes
        country_mappings = {
            'NEW ZEALAND': 'NZ',
            'AUSTRALIA': 'AU',
            'UNITED STATES': 'US',
            'UNITED KINGDOM': 'GB',
            'CANADA': 'CA'
        }
        
        return country_mappings.get(country, country)
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats"""
        if not date_str:
            return None
        
        # Common date formats
        formats = [
            '%Y-%m-%d',
            '%Y-%m',
            '%Y',
            '%d-%m-%Y',
            '%m/%d/%Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None

    def _parse_number(self, value) -> int:
        """Parse numeric strings to integers"""
        if not value:
            return 0
        
        try:
            # Handle comma-separated numbers
            if isinstance(value, str):
                value = value.replace(',', '')
            return int(value)
        except (ValueError, TypeError):
            return 0


# Import all client implementations for complete integration
try:
    from .musicbrainz import MusicBrainzClient, musicbrainz_client
    print("✅ MusicBrainz client imported successfully")
except ImportError as e:
    print(f"⚠️  MusicBrainz client import failed: {e}")
    musicbrainz_client = None

try:
    from .spotify import SpotifyClient, spotify_client
    print("✅ Spotify client imported successfully")
except ImportError as e:
    print(f"⚠️  Spotify client import failed: {e}")
    spotify_client = None

try:
    from .lastfm import LastFmClient, lastfm_client
    print("✅ Last.fm client imported successfully")
except ImportError as e:
    print(f"⚠️  Last.fm client import failed: {e}")
    lastfm_client = None

try:
    from .youtube import YouTubeClient, youtube_client
    print("✅ YouTube client imported successfully")
    if settings.apis['youtube'].api_key:
        print("🎥 YouTube integration: ENABLED with API key")
    else:
        print("🎥 YouTube integration: AVAILABLE but no API key configured")
except ImportError as e:
    print(f"❌ YouTube client import failed: {e}")
    print("YouTube integration will be disabled")
    youtube_client = None
except Exception as e:
    print(f"⚠️  YouTube client initialization warning: {e}")
    youtube_client = None

# Create fallback clients if imports failed
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

# Ensure we always have client objects (even if they're fallbacks)
if musicbrainz_client is None:
    musicbrainz_client = FallbackClient("MusicBrainz")

if spotify_client is None:
    spotify_client = FallbackClient("Spotify")

if lastfm_client is None:
    lastfm_client = FallbackClient("Last.fm")

if youtube_client is None:
    youtube_client = FallbackClient("YouTube")

# Function to check client availability
def check_client_availability():
    """Check which clients are available and properly configured"""
    status = {
        'musicbrainz': musicbrainz_client.__class__.__name__ != 'FallbackClient',
        'spotify': spotify_client.__class__.__name__ != 'FallbackClient',
        'lastfm': lastfm_client.__class__.__name__ != 'FallbackClient',
        'youtube': youtube_client.__class__.__name__ != 'FallbackClient'
    }
    
    print("\n📊 API Client Availability:")
    for client, available in status.items():
        icon = "✅" if available else "❌"
        print(f"  {icon} {client.title()}: {'Available' if available else 'Not available'}")
    
    return status

# Function to get integration summary
def get_integration_summary():
    """Get a summary of all integrations for dashboard/status"""
    from config.settings import settings
    
    summary = {
        'musicbrainz': {
            'available': musicbrainz_client.__class__.__name__ != 'FallbackClient',
            'api_key_required': False,
            'api_key_configured': True,  # MusicBrainz doesn't require API key
            'description': 'Free music metadata database'
        },
        'spotify': {
            'available': spotify_client.__class__.__name__ != 'FallbackClient',
            'api_key_required': True,
            'api_key_configured': bool(settings.spotify_client_id and settings.spotify_client_secret),
            'description': 'Music streaming platform with artist/track data'
        },
        'lastfm': {
            'available': lastfm_client.__class__.__name__ != 'FallbackClient',
            'api_key_required': True,
            'api_key_configured': bool(settings.apis['lastfm'].api_key),
            'description': 'Social music platform with listening data'
        },
        'youtube': {
            'available': youtube_client.__class__.__name__ != 'FallbackClient',
            'api_key_required': True,
            'api_key_configured': bool(settings.apis['youtube'].api_key),
            'description': 'Video platform with channel analytics and engagement data'
        }
    }
    
    return summary

# Test function for all integrations
def test_all_integrations():
    """Test all API integrations to ensure they're working"""
    print("\n🧪 Testing API Integrations...")
    
    results = {}
    
    # Test MusicBrainz
    try:
        if musicbrainz_client.__class__.__name__ != 'FallbackClient':
            # Test with a simple lookup
            test_result = musicbrainz_client.lookup_by_isrc("USRC17607839")
            results['musicbrainz'] = 'working' if test_result is not None else 'api_error'
        else:
            results['musicbrainz'] = 'not_available'
    except Exception as e:
        results['musicbrainz'] = f'error: {str(e)}'
    
    # Test Spotify
    try:
        if spotify_client.__class__.__name__ != 'FallbackClient':
            # Test with a simple search
            test_result = spotify_client.search_artist("test")
            results['spotify'] = 'working' if test_result is not None else 'api_error'
        else:
            results['spotify'] = 'not_available'
    except Exception as e:
        results['spotify'] = f'error: {str(e)}'
    
    # Test Last.fm
    try:
        if lastfm_client.__class__.__name__ != 'FallbackClient':
            # Test with a simple artist lookup
            test_result = lastfm_client.get_artist_info("test")
            results['lastfm'] = 'working' if test_result is not None else 'api_error'
        else:
            results['lastfm'] = 'not_available'
    except Exception as e:
        results['lastfm'] = f'error: {str(e)}'
    
    # Test YouTube
    try:
        if youtube_client.__class__.__name__ != 'FallbackClient':
            # Test with a simple channel search
            test_result = youtube_client.search_artist_channel("test")
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

# Auto-check availability on import
try:
    check_client_availability()
except Exception as e:
    print(f"⚠️  Client availability check failed: {e}")

# Export everything for backward compatibility
__all__ = [
    'BaseAPIClient',
    'MusicBrainzClient',
    'SpotifyClient', 
    'LastFmClient',
    'YouTubeClient',
    'musicbrainz_client',
    'spotify_client',
    'lastfm_client',
    'youtube_client',
    'check_client_availability',
    'get_integration_summary',
    'test_all_integrations'
]

# Print integration status on import
print("\n🎯 Integration Status Summary:")
try:
    summary = get_integration_summary()
    for api, info in summary.items():
        status_icon = "✅" if (info['available'] and info['api_key_configured']) else "⚠️" if info['available'] else "❌"
        config_status = "configured" if info['api_key_configured'] else "not configured" if info['api_key_required'] else "no key required"
        print(f"  {status_icon} {api.title()}: {config_status}")
except Exception as e:
    print(f"⚠️  Could not generate integration summary: {e}")

print("✅ Base API client initialization complete with YouTube integration")