"""
API integration modules for music data sources
"""

from .base_client import musicbrainz_client, spotify_client, lastfm_client

__all__ = [
    'musicbrainz_client',
    'spotify_client', 
    'lastfm_client'
]