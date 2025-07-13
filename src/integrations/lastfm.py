"""
Last.fm API client for social listening data.
Extracted from existing base_client.py implementation.
"""

from typing import Dict, List, Optional
from .base_api import BaseAPIClient
from config.settings import settings


class LastFmClient(BaseAPIClient):
    """Last.fm API client for social listening data"""
    
    def __init__(self):
        super().__init__('lastfm')
    
    def get_artist_info(self, artist_name: str) -> Optional[Dict]:
        """Get artist information from Last.fm"""
        if not settings.apis['lastfm'].api_key:
            return None
        
        params = {
            'method': 'artist.getinfo',
            'artist': artist_name,
            'autocorrect': 1
        }
        
        response = self.rate_limiter.make_request(self.api_name, '', params=params)
        
        if not response or 'error' in response:
            return None
        
        artist = response.get('artist', {})
        
        return {
            'name': artist.get('name'),
            'mbid': artist.get('mbid'),  # MusicBrainz ID
            'listeners': self._parse_number(artist.get('stats', {}).get('listeners')),
            'playcount': self._parse_number(artist.get('stats', {}).get('playcount')),
            'tags': [tag['name'] for tag in artist.get('tags', {}).get('tag', [])[:5]],
            'bio': artist.get('bio', {}).get('summary', ''),
            'similar_artists': [
                similar['name'] for similar in artist.get('similar', {}).get('artist', [])[:5]
            ]
        }
    
    def get_track_info(self, artist_name: str, track_title: str) -> Optional[Dict]:
        """Get track information from Last.fm"""
        if not settings.apis['lastfm'].api_key:
            return None
        
        params = {
            'method': 'track.getinfo',
            'artist': artist_name,
            'track': track_title,
            'autocorrect': 1
        }
        
        response = self.rate_limiter.make_request(self.api_name, '', params=params)
        
        if not response or 'error' in response:
            return None
        
        track = response.get('track', {})
        
        return {
            'name': track.get('name'),
            'artist': track.get('artist', {}).get('name'),
            'mbid': track.get('mbid'),
            'playcount': self._parse_number(track.get('playcount')),
            'listeners': self._parse_number(track.get('listeners')),
            'tags': [tag['name'] for tag in track.get('toptags', {}).get('tag', [])[:5]],
            'duration': track.get('duration')
        }


# Create global instance for easy access
lastfm_client = LastFmClient()