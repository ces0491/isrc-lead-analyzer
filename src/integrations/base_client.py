"""
API integrations for music data sources
Each client handles a specific API with proper error handling and data normalization
"""
import base64
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote
from src.core.rate_limiter import rate_limiter
from config.settings import settings

class BaseAPIClient:
    """Base class for API clients with common functionality"""
    
    def __init__(self, api_name: str):
        self.api_name = api_name
        self.rate_limiter = rate_limiter
    
    def _normalize_country_code(self, country: str) -> str:
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

class MusicBrainzClient(BaseAPIClient):
    """MusicBrainz API client for track and artist metadata"""
    
    def __init__(self):
        super().__init__('musicbrainz')
    
    def lookup_by_isrc(self, isrc: str) -> Optional[Dict]:
        """Look up track and artist info by ISRC"""
        if not isrc or len(isrc) != 12:
            return None
        
        # Clean ISRC
        isrc = isrc.upper().replace('-', '').replace(' ', '')
        
        # Search for recording by ISRC
        endpoint = f"recording?query=isrc:{isrc}&fmt=json&inc=artist-credits+releases+labels"
        response = self.rate_limiter.make_request(self.api_name, endpoint)
        
        if not response or not response.get('recordings'):
            return None
        
        recording = response['recordings'][0]  # Take first match
        
        # Extract track info
        track_data = {
            'isrc': isrc,
            'title': recording.get('title'),
            'musicbrainz_recording_id': recording.get('id'),
            'length_ms': recording.get('length'),
            'disambiguation': recording.get('disambiguation')
        }
        
        # Extract artist info
        artist_credits = recording.get('artist-credit', [])
        if artist_credits:
            artist = artist_credits[0].get('artist', {})
            artist_data = {
                'name': artist.get('name'),
                'musicbrainz_artist_id': artist.get('id'),
                'sort_name': artist.get('sort-name'),
                'disambiguation': artist.get('disambiguation')
            }
            
            # Get detailed artist info
            detailed_artist = self.get_artist_details(artist_data['musicbrainz_artist_id'])
            if detailed_artist:
                artist_data.update(detailed_artist)
        else:
            artist_data = {}
        
        # Extract release/label info
        releases = recording.get('releases', [])
        release_data = {}
        if releases:
            release = releases[0]  # Take first release
            release_data = {
                'release_title': release.get('title'),
                'release_date': release.get('date'),
                'country': self._normalize_country_code(release.get('country')),
                'barcode': release.get('barcode')
            }
            
            # Extract label info
            label_info = release.get('label-info', [])
            if label_info:
                label = label_info[0].get('label', {})
                release_data['label'] = label.get('name')
                release_data['label_code'] = label.get('label-code')
        
        return {
            'track': track_data,
            'artist': artist_data,
            'release': release_data
        }
    
    def get_artist_details(self, musicbrainz_id: str) -> Optional[Dict]:
        """Get detailed artist information"""
        if not musicbrainz_id:
            return None
        
        endpoint = f"artist/{musicbrainz_id}?fmt=json&inc=url-rels+tags+genres"
        response = self.rate_limiter.make_request(self.api_name, endpoint)
        
        if not response:
            return None
        
        artist_details = {
            'type': response.get('type'),
            'gender': response.get('gender'),
            'country': self._normalize_country_code(response.get('country')),
            'life_span': response.get('life-span', {})
        }
        
        # Extract genres/tags
        tags = response.get('tags', [])
        genres = response.get('genres', [])
        
        if tags:
            artist_details['tags'] = [tag['name'] for tag in tags[:5]]  # Top 5 tags
        if genres:
            artist_details['genres'] = [genre['name'] for genre in genres[:3]]  # Top 3 genres
        
        # Extract URLs (social media, websites)
        relations = response.get('relations', [])
        urls = {}
        for relation in relations:
            if relation.get('type') == 'social network':
                url = relation.get('url', {}).get('resource', '')
                if 'twitter.com' in url:
                    urls['twitter'] = url.split('/')[-1]
                elif 'instagram.com' in url:
                    urls['instagram'] = url.split('/')[-1]
                elif 'facebook.com' in url:
                    urls['facebook'] = url.split('/')[-1]
            elif relation.get('type') == 'official homepage':
                urls['website'] = relation.get('url', {}).get('resource')
        
        if urls:
            artist_details['urls'] = urls
        
        return artist_details

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
        import requests
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

# Client instances
musicbrainz_client = MusicBrainzClient()
spotify_client = SpotifyClient()
lastfm_client = LastFmClient()

# Utility function for testing
def test_clients():
    """Test all API clients with sample data"""
    print("Testing API clients...")
    
    # Test ISRC: "USRC17607839" (example)
    test_isrc = "USRC17607839"
    
    print(f"\n1. Testing MusicBrainz with ISRC: {test_isrc}")
    mb_result = musicbrainz_client.lookup_by_isrc(test_isrc)
    if mb_result:
        print(f"   Found: {mb_result['artist']['name']} - {mb_result['track']['title']}")
    else:
        print("   No results found")
    
    print(f"\n2. Testing Spotify search for: Lorde")
    spotify_result = spotify_client.search_artist("Lorde")
    if spotify_result:
        print(f"   Found: {spotify_result['name']} (Popularity: {spotify_result['popularity']})")
    else:
        print("   No results found")
    
    print(f"\n3. Testing Last.fm for: Lorde")
    lastfm_result = lastfm_client.get_artist_info("Lorde")
    if lastfm_result:
        print(f"   Found: {lastfm_result['name']} (Listeners: {lastfm_result['listeners']})")
    else:
        print("   No results found")

if __name__ == "__main__":
    test_clients()