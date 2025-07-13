"""
API integration modules for music data sources
"""

# Don't import clients directly to avoid circular imports
__all__ = [
    'musicbrainz_client',
    'spotify_client', 
    'lastfm_client',
    'youtube_client'
]

def get_clients():
    """Get all API clients (lazy import)"""
    from .base_client import musicbrainz_client, spotify_client, lastfm_client, youtube_client
    return {
        'musicbrainz': musicbrainz_client,
        'spotify': spotify_client,
        'lastfm': lastfm_client,
        'youtube': youtube_client
    }
