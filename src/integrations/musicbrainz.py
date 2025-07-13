"""
MusicBrainz API client for track and artist metadata.
Extracted from the existing base_client.py implementation.
"""

from typing import Dict, List, Optional, Tuple
from urllib.parse import quote
from .base_api import BaseAPIClient


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


# Create global instance for easy access
musicbrainz_client = MusicBrainzClient()