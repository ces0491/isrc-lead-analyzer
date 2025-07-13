"""
Spotify Web API client extracted from existing base_client.py implementation.
"""

import base64
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote
from .base_api import BaseAPIClient
from config.settings import settings


class SpotifyClient(BaseAPIClient):
    """Spotify Web API client"""
    
    def __init__(self):
        super().__init__('spotify')
        self.access_token = None
        self.token_expires_at = None
        self._authenticate()
    
    def _authenticate(self):
        """Get access token using client credentials flow"""
        if not settings.spotify_client_id or not settings.spotify_client_secret:
            print("Warning: Spotify credentials not configured")
            return
        
        auth_string = f"{settings.spotify_client_id}:{settings.spotify_client_secret}"
        auth_base64 = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {auth_base64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {'grant_type': 'client_credentials'}
        
        # Make direct request for authentication (bypass rate limiter)
        response = requests.post(
            'https://accounts.spotify.com/api/token',
            headers=headers,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            # Set expiration time (usually 3600 seconds)
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)  # 1 min buffer
            print("Spotify authentication successful")
        else:
            print(f"Spotify authentication failed: {response.status_code}")
    
    def _ensure_authenticated(self):
        """Ensure we have a valid access token"""
        if not self.access_token or (self.token_expires_at and datetime.now() >= self.token_expires_at):
            self._authenticate()
    
    def search_artist(self, artist_name: str) -> Optional[Dict]:
        """Search for artist by name"""
        self._ensure_authenticated()
        if not self.access_token:
            return None
        
        query = quote(artist_name)
        endpoint = f"search?q={query}&type=artist&limit=1"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        response = self.rate_limiter.make_request(self.api_name, endpoint, headers=headers)
        
        if not response or not response.get('artists', {}).get('items'):
            return None
        
        artist = response['artists']['items'][0]
        
        return {
            'spotify_id': artist.get('id'),
            'name': artist.get('name'),
            'popularity': artist.get('popularity'),
            'followers': artist.get('followers', {}).get('total', 0),
            'genres': artist.get('genres', []),
            'external_urls': artist.get('external_urls', {}),
            'images': artist.get('images', [])
        }
    
    def get_artist_details(self, spotify_id: str) -> Optional[Dict]:
        """Get detailed artist information"""
        self._ensure_authenticated()
        if not self.access_token or not spotify_id:
            return None
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        # Get artist info
        artist_response = self.rate_limiter.make_request(
            self.api_name, f"artists/{spotify_id}", headers=headers
        )
        
        if not artist_response:
            return None
        
        # Get top tracks to analyze recent activity
        tracks_response = self.rate_limiter.make_request(
            self.api_name, f"artists/{spotify_id}/top-tracks?market=US", headers=headers
        )
        
        # Get albums for release analysis
        albums_response = self.rate_limiter.make_request(
            self.api_name, f"artists/{spotify_id}/albums?market=US&include_groups=album,single&limit=20", 
            headers=headers
        )
        
        result = {
            'spotify_id': spotify_id,
            'name': artist_response.get('name'),
            'popularity': artist_response.get('popularity'),
            'followers': artist_response.get('followers', {}).get('total', 0),
            'genres': artist_response.get('genres', [])
        }
        
        # Analyze top tracks
        if tracks_response and tracks_response.get('tracks'):
            tracks = tracks_response['tracks']
            result['top_tracks_count'] = len(tracks)
            result['average_popularity'] = sum(t.get('popularity', 0) for t in tracks) / len(tracks)
        
        # Analyze releases
        if albums_response and albums_response.get('items'):
            albums = albums_response['items']
            result['release_count'] = len(albums)
            
            # Find most recent release
            recent_releases = [a for a in albums if a.get('release_date')]
            if recent_releases:
                recent_releases.sort(key=lambda x: x['release_date'], reverse=True)
                result['last_release_date'] = recent_releases[0]['release_date']
        
        return result
    
    def search_track(self, artist_name: str, track_title: str) -> Optional[Dict]:
        """Search for specific track"""
        self._ensure_authenticated()
        if not self.access_token:
            return None
        
        query = quote(f"artist:{artist_name} track:{track_title}")
        endpoint = f"search?q={query}&type=track&limit=1"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        response = self.rate_limiter.make_request(self.api_name, endpoint, headers=headers)
        
        if not response or not response.get('tracks', {}).get('items'):
            return None
        
        track = response['tracks']['items'][0]
        
        return {
            'spotify_track_id': track.get('id'),
            'name': track.get('name'),
            'popularity': track.get('popularity'),
            'duration_ms': track.get('duration_ms'),
            'explicit': track.get('explicit'),
            'preview_url': track.get('preview_url'),
            'external_urls': track.get('external_urls', {}),
            'album': {
                'name': track.get('album', {}).get('name'),
                'release_date': track.get('album', {}).get('release_date'),
                'album_type': track.get('album', {}).get('album_type')
            }
        }


# Create global instance for easy access
spotify_client = SpotifyClient()