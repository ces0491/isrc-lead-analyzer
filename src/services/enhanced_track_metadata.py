"""
Enhanced Track Metadata Service Integration
Add this to: src/services/enhanced_track_metadata.py
"""

import os
import re
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import requests
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

@dataclass
class TrackCredits:
    """Structured track credits information"""
    composers: List[Dict[str, str]]
    lyricists: List[Dict[str, str]]
    producers: List[Dict[str, str]]
    performers: List[Dict[str, str]]
    engineers: List[Dict[str, str]]
    other_credits: List[Dict[str, str]]

@dataclass
class TrackMetadata:
    """Comprehensive track metadata"""
    # Basic Information
    isrc: str
    title: str
    artist: str
    album: str
    duration_ms: int
    release_date: Optional[datetime]
    
    # Credits
    credits: TrackCredits
    
    # Content
    lyrics: Optional[str]
    lyrics_language: Optional[str]
    lyrics_copyright: Optional[str]
    
    # Technical Details
    key: Optional[str]
    tempo_bpm: Optional[int]
    time_signature: Optional[str]
    energy: Optional[float]
    valence: Optional[float]
    danceability: Optional[float]
    acousticness: Optional[float]
    instrumentalness: Optional[float]
    speechiness: Optional[float]
    loudness: Optional[float]
    
    # Publishing & Rights
    publisher: Optional[str]
    record_label: str
    copyright_info: Dict[str, str]
    publishing_splits: List[Dict[str, Any]]
    
    # Platform Information
    platform_availability: Dict[str, bool]
    platform_ids: Dict[str, str]
    
    # Additional Metadata
    genre: List[str]
    tags: List[str]
    recording_location: Optional[str]
    recording_date: Optional[datetime]
    
    # Sources and Confidence
    data_sources: List[str]
    confidence_score: float
    last_updated: datetime

class EnhancedTrackMetadataCollector:
    """
    Enhanced metadata collector focusing on comprehensive track information
    """
    
    def __init__(self, rate_limiter):
        self.rate_limiter = rate_limiter
        self.setup_lyrics_apis()
        
    def setup_lyrics_apis(self):
        """Setup lyrics API configurations"""
        self.lyrics_apis = {
            'genius': {
                'api_key': os.getenv('GENIUS_API_KEY'),
                'base_url': 'https://api.genius.com',
                'enabled': bool(os.getenv('GENIUS_API_KEY'))
            },
            'lyricfind': {
                'api_key': os.getenv('LYRICFIND_API_KEY'),
                'base_url': 'https://api.lyricfind.com',
                'enabled': bool(os.getenv('LYRICFIND_API_KEY'))
            },
            'musixmatch': {
                'api_key': os.getenv('MUSIXMATCH_API_KEY'),
                'base_url': 'https://api.musixmatch.com/ws/1.1',
                'enabled': bool(os.getenv('MUSIXMATCH_API_KEY'))
            }
        }
    
    def collect_comprehensive_track_data(self, isrc: str) -> TrackMetadata:
        """
        Collect comprehensive track metadata from all available sources
        """
        logger.info(f"Collecting comprehensive metadata for ISRC: {isrc}")
        
        # Initialize data collection from multiple sources
        musicbrainz_data = self.get_musicbrainz_track_data(isrc)
        spotify_data = self.get_spotify_track_data(isrc)
        discogs_data = self.get_discogs_track_data(isrc, musicbrainz_data)
        lastfm_data = self.get_lastfm_track_data(isrc, musicbrainz_data)
        
        # Get lyrics from multiple sources
        lyrics_data = self.get_comprehensive_lyrics(musicbrainz_data, spotify_data)
        
        # Aggregate and normalize all data
        track_metadata = self.aggregate_track_metadata(
            isrc=isrc,
            musicbrainz_data=musicbrainz_data,
            spotify_data=spotify_data,
            discogs_data=discogs_data,
            lastfm_data=lastfm_data,
            lyrics_data=lyrics_data
        )
        
        return track_metadata
    
    def get_musicbrainz_track_data(self, isrc: str) -> Dict[str, Any]:
        """
        Get comprehensive track data from MusicBrainz including detailed credits
        """
        logger.info(f"Fetching MusicBrainz data for ISRC: {isrc}")
        
        try:
            # Search for recording by ISRC
            recording_data = self.rate_limiter.make_request(
                'musicbrainz',
                'recording',
                params={
                    'query': f'isrc:{isrc}',
                    'inc': 'artist-credits+releases+release-groups+tags+ratings+genres+isrcs+artist-rels+work-rels+recording-rels',
                    'fmt': 'json'
                }
            )
            
            if not recording_data or not recording_data.get('recordings'):
                return {}
            
            recording = recording_data['recordings'][0]
            recording_id = recording['id']
            
            # Get detailed recording relationships for credits
            detailed_recording = self.rate_limiter.make_request(
                'musicbrainz',
                f'recording/{recording_id}',
                params={
                    'inc': 'artist-credits+releases+release-groups+tags+ratings+genres+isrcs+artist-rels+work-rels+recording-rels+url-rels',
                    'fmt': 'json'
                }
            )
            
            # Get work relationships for composition credits
            work_data = None
            if detailed_recording.get('relations'):
                for rel in detailed_recording['relations']:
                    if rel.get('type') == 'performance' and rel.get('work'):
                        work_id = rel['work']['id']
                        work_data = self.rate_limiter.make_request(
                            'musicbrainz',
                            f'work/{work_id}',
                            params={
                                'inc': 'artist-rels+work-rels+tags+genres',
                                'fmt': 'json'
                            }
                        )
                        break
            
            # Get release information for additional metadata
            releases_data = []
            if recording.get('releases'):
                for release in recording['releases'][:3]:  # Limit to first 3 releases
                    release_id = release['id']
                    release_detail = self.rate_limiter.make_request(
                        'musicbrainz',
                        f'release/{release_id}',
                        params={
                            'inc': 'artist-credits+labels+recordings+release-groups+media+discids+artist-rels+label-rels+recording-rels+release-rel+url-rels',
                            'fmt': 'json'
                        }
                    )
                    if release_detail:
                        releases_data.append(release_detail)
            
            return {
                'recording': detailed_recording,
                'work': work_data,
                'releases': releases_data,
                'source': 'musicbrainz'
            }
            
        except Exception as e:
            logger.error(f"Error fetching MusicBrainz data: {e}")
            return {}
    
    def get_spotify_track_data(self, isrc: str) -> Dict[str, Any]:
        """
        Get Spotify track data including audio features and credits
        """
        logger.info(f"Fetching Spotify data for ISRC: {isrc}")
        
        try:
            # Search for track by ISRC
            search_result = self.rate_limiter.make_request(
                'spotify',
                'search',
                params={
                    'q': f'isrc:{isrc}',
                    'type': 'track',
                    'limit': 1
                }
            )
            
            if not search_result or not search_result.get('tracks', {}).get('items'):
                return {}
            
            track = search_result['tracks']['items'][0]
            track_id = track['id']
            
            # Get audio features
            audio_features = self.rate_limiter.make_request(
                'spotify',
                f'audio-features/{track_id}'
            )
            
            # Get album information for additional context
            album_id = track['album']['id']
            album_data = self.rate_limiter.make_request(
                'spotify',
                f'albums/{album_id}'
            )
            
            return {
                'track': track,
                'audio_features': audio_features,
                'album': album_data,
                'source': 'spotify'
            }
            
        except Exception as e:
            logger.error(f"Error fetching Spotify data: {e}")
            return {}
    
    def get_discogs_track_data(self, isrc: str, musicbrainz_data: Dict) -> Dict[str, Any]:
        """
        Get Discogs release data for detailed credits and production information
        """
        logger.info(f"Fetching Discogs data for ISRC: {isrc}")
        
        try:
            # Extract artist and release info from MusicBrainz to search Discogs
            if not musicbrainz_data.get('recording'):
                return {}
            
            recording = musicbrainz_data['recording']
            artist_name = recording['artist-credit'][0]['artist']['name']
            title = recording['title']
            
            # Search Discogs by artist and title
            search_params = {
                'q': f'{artist_name} {title}',
                'type': 'release',
                'format': 'track'
            }
            
            search_result = self.rate_limiter.make_request(
                'discogs',
                'database/search',
                params=search_params
            )
            
            if not search_result or not search_result.get('results'):
                return {}
            
            # Get detailed release information for the best match
            release_id = search_result['results'][0]['id']
            release_data = self.rate_limiter.make_request(
                'discogs',
                f'releases/{release_id}'
            )
            
            return {
                'release': release_data,
                'search_results': search_result,
                'source': 'discogs'
            }
            
        except Exception as e:
            logger.error(f"Error fetching Discogs data: {e}")
            return {}
    
    def get_lastfm_track_data(self, isrc: str, musicbrainz_data: Dict) -> Dict[str, Any]:
        """
        Get Last.fm track data for additional metadata and tags
        """
        logger.info(f"Fetching Last.fm data for ISRC: {isrc}")
        
        try:
            if not musicbrainz_data.get('recording'):
                return {}
            
            recording = musicbrainz_data['recording']
            artist_name = recording['artist-credit'][0]['artist']['name']
            title = recording['title']
            
            # Get track info
            track_info = self.rate_limiter.make_request(
                'lastfm',
                '',
                params={
                    'method': 'track.getinfo',
                    'artist': artist_name,
                    'track': title,
                    'autocorrect': 1
                }
            )
            
            return {
                'track_info': track_info,
                'source': 'lastfm'
            }
            
        except Exception as e:
            logger.error(f"Error fetching Last.fm data: {e}")
            return {}
    
    def get_comprehensive_lyrics(self, musicbrainz_data: Dict, spotify_data: Dict) -> Dict[str, Any]:
        """
        Get lyrics from multiple sources with quality scoring
        """
        if not musicbrainz_data.get('recording'):
            return {}
        
        recording = musicbrainz_data['recording']
        artist_name = recording['artist-credit'][0]['artist']['name']
        title = recording['title']
        
        lyrics_results = {}
        
        # Try Genius API (if available)
        if self.lyrics_apis['genius']['enabled']:
            genius_lyrics = self.get_genius_lyrics(artist_name, title)
            if genius_lyrics:
                lyrics_results['genius'] = genius_lyrics
        
        # Try Musixmatch API (if available)
        if self.lyrics_apis['musixmatch']['enabled']:
            musixmatch_lyrics = self.get_musixmatch_lyrics(artist_name, title)
            if musixmatch_lyrics:
                lyrics_results['musixmatch'] = musixmatch_lyrics
        
        return lyrics_results
    
    def get_genius_lyrics(self, artist_name: str, title: str) -> Optional[Dict[str, Any]]:
        """Get lyrics from Genius API"""
        try:
            api_key = self.lyrics_apis['genius']['api_key']
            headers = {'Authorization': f'Bearer {api_key}'}
            
            # Search for song
            search_url = f"{self.lyrics_apis['genius']['base_url']}/search"
            params = {'q': f'{artist_name} {title}'}
            
            response = requests.get(search_url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('response', {}).get('hits'):
                    song_data = data['response']['hits'][0]['result']
                    
                    return {
                        'song_id': song_data.get('id'),
                        'url': song_data.get('url'),
                        'title': song_data.get('title'),
                        'artist': song_data.get('primary_artist', {}).get('name'),
                        'has_lyrics': True,
                        'source': 'genius'
                    }
            
        except Exception as e:
            logger.error(f"Error fetching Genius lyrics: {e}")
        
        return None
    
    def get_musixmatch_lyrics(self, artist_name: str, title: str) -> Optional[Dict[str, Any]]:
        """Get lyrics from Musixmatch API"""
        try:
            api_key = self.lyrics_apis['musixmatch']['api_key']
            base_url = self.lyrics_apis['musixmatch']['base_url']
            
            # Search for track
            search_url = f"{base_url}/track.search"
            params = {
                'apikey': api_key,
                'q_artist': artist_name,
                'q_track': title,
                'page_size': 1,
                'format': 'json'
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('message', {}).get('body', {}).get('track_list'):
                    track = data['message']['body']['track_list'][0]['track']
                    track_id = track['track_id']
                    
                    # Get lyrics
                    lyrics_url = f"{base_url}/track.lyrics.get"
                    lyrics_params = {
                        'apikey': api_key,
                        'track_id': track_id,
                        'format': 'json'
                    }
                    
                    lyrics_response = requests.get(lyrics_url, params=lyrics_params, timeout=10)
                    if lyrics_response.status_code == 200:
                        lyrics_data = lyrics_response.json()
                        lyrics_body = lyrics_data.get('message', {}).get('body', {}).get('lyrics', {})
                        
                        return {
                            'track_id': track_id,
                            'lyrics': lyrics_body.get('lyrics_body'),
                            'language': lyrics_body.get('lyrics_language'),
                            'copyright': lyrics_body.get('lyrics_copyright'),
                            'has_lyrics': bool(lyrics_body.get('lyrics_body')),
                            'source': 'musixmatch'
                        }
            
        except Exception as e:
            logger.error(f"Error fetching Musixmatch lyrics: {e}")
        
        return None
    
    def aggregate_track_metadata(self, 
                                isrc: str,
                                musicbrainz_data: Dict,
                                spotify_data: Dict,
                                discogs_data: Dict,
                                lastfm_data: Dict,
                                lyrics_data: Dict) -> TrackMetadata:
        """
        Aggregate and normalize track metadata from all sources
        """
        logger.info(f"Aggregating metadata for ISRC: {isrc}")
        
        # Extract basic track information
        basic_info = self.extract_basic_track_info(musicbrainz_data, spotify_data)
        
        # Extract comprehensive credits
        credits = self.extract_track_credits(musicbrainz_data, discogs_data)
        
        # Extract lyrics and content
        lyrics_info = self.extract_lyrics_info(lyrics_data)
        
        # Extract technical details
        technical_info = self.extract_technical_details(spotify_data, musicbrainz_data)
        
        # Extract publishing and rights information
        rights_info = self.extract_rights_info(musicbrainz_data, discogs_data)
        
        # Extract platform availability
        platform_info = self.extract_platform_info(spotify_data, musicbrainz_data)
        
        # Calculate confidence score
        confidence_score = self.calculate_confidence_score(
            musicbrainz_data, spotify_data, discogs_data, lastfm_data, lyrics_data
        )
        
        return TrackMetadata(
            isrc=isrc,
            title=basic_info.get('title', ''),
            artist=basic_info.get('artist', ''),
            album=basic_info.get('album', ''),
            duration_ms=basic_info.get('duration_ms', 0),
            release_date=basic_info.get('release_date'),
            credits=credits,
            lyrics=lyrics_info.get('lyrics'),
            lyrics_language=lyrics_info.get('language'),
            lyrics_copyright=lyrics_info.get('copyright'),
            key=technical_info.get('key'),
            tempo_bpm=technical_info.get('tempo_bpm'),
            time_signature=technical_info.get('time_signature'),
            energy=technical_info.get('energy'),
            valence=technical_info.get('valence'),
            danceability=technical_info.get('danceability'),
            acousticness=technical_info.get('acousticness'),
            instrumentalness=technical_info.get('instrumentalness'),
            speechiness=technical_info.get('speechiness'),
            loudness=technical_info.get('loudness'),
            publisher=rights_info.get('publisher'),
            record_label=rights_info.get('record_label', ''),
            copyright_info=rights_info.get('copyright_info', {}),
            publishing_splits=rights_info.get('publishing_splits', []),
            platform_availability=platform_info.get('availability', {}),
            platform_ids=platform_info.get('ids', {}),
            genre=basic_info.get('genres', []),
            tags=basic_info.get('tags', []),
            recording_location=basic_info.get('recording_location'),
            recording_date=basic_info.get('recording_date'),
            data_sources=[k for k, v in {
                'musicbrainz': musicbrainz_data,
                'spotify': spotify_data,
                'discogs': discogs_data,
                'lastfm': lastfm_data,
                'lyrics': lyrics_data
            }.items() if v],
            confidence_score=confidence_score,
            last_updated=datetime.utcnow()
        )
    
    def extract_basic_track_info(self, musicbrainz_data: Dict, spotify_data: Dict) -> Dict[str, Any]:
        """Extract basic track information"""
        info = {}
        
        # Title (prioritize MusicBrainz for accuracy)
        if musicbrainz_data.get('recording'):
            info['title'] = musicbrainz_data['recording'].get('title', '')
            
            # Artist name
            if musicbrainz_data['recording'].get('artist-credit'):
                artist_credits = musicbrainz_data['recording']['artist-credit']
                artists = [credit['artist']['name'] for credit in artist_credits if isinstance(credit, dict)]
                info['artist'] = ', '.join(artists)
            
            # Duration
            if musicbrainz_data['recording'].get('length'):
                info['duration_ms'] = int(musicbrainz_data['recording']['length'])
        
        # Supplement with Spotify data
        if spotify_data.get('track'):
            track = spotify_data['track']
            if not info.get('title'):
                info['title'] = track.get('name', '')
            if not info.get('artist'):
                artists = [artist['name'] for artist in track.get('artists', [])]
                info['artist'] = ', '.join(artists)
            if not info.get('duration_ms'):
                info['duration_ms'] = track.get('duration_ms', 0)
            
            # Album information
            if track.get('album'):
                info['album'] = track['album'].get('name', '')
                if track['album'].get('release_date'):
                    try:
                        info['release_date'] = datetime.strptime(
                            track['album']['release_date'], '%Y-%m-%d'
                        )
                    except ValueError:
                        pass
        
        # Extract genres and tags
        info['genres'] = []
        info['tags'] = []
        
        if musicbrainz_data.get('recording', {}).get('tags'):
            info['tags'] = [tag['name'] for tag in musicbrainz_data['recording']['tags']]
        
        if spotify_data.get('album', {}).get('genres'):
            info['genres'] = spotify_data['album']['genres']
        
        return info
    
    def extract_track_credits(self, musicbrainz_data: Dict, discogs_data: Dict) -> TrackCredits:
        """Extract comprehensive track credits"""
        composers = []
        lyricists = []
        producers = []
        performers = []
        engineers = []
        other_credits = []
        
        # Extract from MusicBrainz relationships
        if musicbrainz_data.get('recording', {}).get('relations'):
            for relation in musicbrainz_data['recording']['relations']:
                rel_type = relation.get('type', '').lower()
                artist_info = relation.get('artist', {})
                
                credit_info = {
                    'name': artist_info.get('name', ''),
                    'mbid': artist_info.get('id', ''),
                    'role': relation.get('type', ''),
                    'attributes': relation.get('attributes', [])
                }
                
                if 'vocal' in rel_type or 'perform' in rel_type:
                    performers.append(credit_info)
                elif 'produc' in rel_type:
                    producers.append(credit_info)
                elif 'engineer' in rel_type or 'mix' in rel_type or 'master' in rel_type:
                    engineers.append(credit_info)
                else:
                    other_credits.append(credit_info)
        
        # Extract composition credits from work relationships
        if musicbrainz_data.get('work', {}).get('relations'):
            for relation in musicbrainz_data['work']['relations']:
                rel_type = relation.get('type', '').lower()
                artist_info = relation.get('artist', {})
                
                credit_info = {
                    'name': artist_info.get('name', ''),
                    'mbid': artist_info.get('id', ''),
                    'role': relation.get('type', ''),
                    'attributes': relation.get('attributes', [])
                }
                
                if 'composer' in rel_type or 'music' in rel_type:
                    composers.append(credit_info)
                elif 'lyricist' in rel_type or 'lyrics' in rel_type:
                    lyricists.append(credit_info)
        
        # Supplement with Discogs credits
        if discogs_data.get('release', {}).get('extraartists'):
            for artist in discogs_data['release']['extraartists']:
                credit_info = {
                    'name': artist.get('name', ''),
                    'role': artist.get('role', ''),
                    'anv': artist.get('anv', ''),  # Artist Name Variation
                    'tracks': artist.get('tracks', '')
                }
                
                role_lower = artist.get('role', '').lower()
                if 'produc' in role_lower:
                    producers.append(credit_info)
                elif 'engineer' in role_lower or 'mix' in role_lower:
                    engineers.append(credit_info)
                elif 'perform' in role_lower or 'vocal' in role_lower:
                    performers.append(credit_info)
                elif 'writ' in role_lower or 'compos' in role_lower:
                    composers.append(credit_info)
                else:
                    other_credits.append(credit_info)
        
        return TrackCredits(
            composers=composers,
            lyricists=lyricists,
            producers=producers,
            performers=performers,
            engineers=engineers,
            other_credits=other_credits
        )
    
    def extract_lyrics_info(self, lyrics_data: Dict) -> Dict[str, Any]:
        """Extract lyrics information from multiple sources"""
        lyrics_info = {}
        
        # Prioritize sources by quality/reliability
        source_priority = ['musixmatch', 'genius']
        
        for source in source_priority:
            if source in lyrics_data and lyrics_data[source].get('has_lyrics'):
                lyrics_info.update({
                    'lyrics': lyrics_data[source].get('lyrics'),
                    'language': lyrics_data[source].get('language'),
                    'source': source,
                    'copyright': lyrics_data[source].get('copyright')
                })
                break
        
        return lyrics_info
    
    def extract_technical_details(self, spotify_data: Dict, musicbrainz_data: Dict) -> Dict[str, Any]:
        """Extract technical audio details"""
        technical = {}
        
        # From Spotify audio features
        if spotify_data.get('audio_features'):
            features = spotify_data['audio_features']
            technical.update({
                'key': self.convert_spotify_key(features.get('key'), features.get('mode')),
                'tempo_bpm': round(features.get('tempo', 0)),
                'time_signature': f"{features.get('time_signature', 4)}/4",
                'energy': features.get('energy', 0),
                'valence': features.get('valence', 0),
                'danceability': features.get('danceability', 0),
                'acousticness': features.get('acousticness', 0),
                'instrumentalness': features.get('instrumentalness', 0),
                'speechiness': features.get('speechiness', 0),
                'loudness': features.get('loudness', 0)
            })
        
        return technical
    
    def extract_rights_info(self, musicbrainz_data: Dict, discogs_data: Dict) -> Dict[str, Any]:
        """Extract publishing and rights information"""
        rights_info = {
            'copyright_info': {},
            'publishing_splits': []
        }
        
        # From MusicBrainz releases
        if musicbrainz_data.get('releases'):
            for release in musicbrainz_data['releases']:
                if release.get('label-info'):
                    for label_info in release['label-info']:
                        label = label_info.get('label', {})
                        rights_info['record_label'] = label.get('name', '')
                        break
        
        # From Discogs
        if discogs_data.get('release'):
            if discogs_data['release'].get('labels'):
                labels = discogs_data['release']['labels']
                rights_info['record_label'] = labels[0].get('name', '')
        
        return rights_info
    
    def extract_platform_info(self, spotify_data: Dict, musicbrainz_data: Dict) -> Dict[str, Any]:
        """Extract platform availability and IDs"""
        platform_info = {
            'availability': {},
            'ids': {}
        }
        
        # Spotify availability
        if spotify_data.get('track'):
            platform_info['availability']['spotify'] = True
            platform_info['ids']['spotify'] = spotify_data['track'].get('id', '')
            
            # Market availability
            markets = spotify_data['track'].get('available_markets', [])
            platform_info['available_markets'] = markets
        
        # From MusicBrainz URLs/relationships
        if musicbrainz_data.get('recording', {}).get('relations'):
            for relation in musicbrainz_data['recording']['relations']:
                if relation.get('type') == 'streaming' and relation.get('url'):
                    url = relation['url']['resource']
                    if 'spotify.com' in url:
                        platform_info['availability']['spotify'] = True
                    elif 'music.apple.com' in url:
                        platform_info['availability']['apple_music'] = True
                    elif 'music.youtube.com' in url:
                        platform_info['availability']['youtube_music'] = True
                    elif 'music.amazon.com' in url:
                        platform_info['availability']['amazon_music'] = True
        
        return platform_info
    
    def convert_spotify_key(self, key_int: int, mode: int) -> str:
        """Convert Spotify key integer to musical key"""
        if key_int is None or mode is None:
            return None
        
        keys = ['C', 'C♯/D♭', 'D', 'D♯/E♭', 'E', 'F', 'F♯/G♭', 'G', 'G♯/A♭', 'A', 'A♯/B♭', 'B']
        key_name = keys[key_int] if 0 <= key_int < 12 else 'Unknown'
        mode_name = 'major' if mode == 1 else 'minor'
        
        return f"{key_name} {mode_name}"
    
    def calculate_confidence_score(self, *data_sources) -> float:
        """Calculate confidence score based on data source availability and quality"""
        source_weights = {
            'musicbrainz': 0.3,
            'spotify': 0.25,
            'discogs': 0.2,
            'lastfm': 0.15,
            'lyrics': 0.1
        }
        
        score = 0.0
        for i, source_data in enumerate(data_sources):
            source_name = list(source_weights.keys())[i]
            if source_data and isinstance(source_data, dict) and source_data:
                score += source_weights[source_name]
        
        return round(score * 100, 1)