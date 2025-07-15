"""
Rate limiting system for API calls - Enhanced version with lyrics APIs
Updated for Prism Analytics Engine enhanced track metadata collection
"""
import os
import time
import json
from typing import Dict, List, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta
import requests
import logging

logger = logging.getLogger(__name__)

class RateLimitManager:
    """
    Enhanced rate limiter with lyrics APIs for comprehensive track metadata
    """
    
    def __init__(self):
        # Load configuration from environment variables with enhanced APIs
        self.api_configs = {
            'musicbrainz': {
                'requests_per_second': 1,      
                'requests_per_minute': int(os.getenv('MUSICBRAINZ_RATE_LIMIT', 50)),
                'requests_per_day': None,
                'base_url': 'https://musicbrainz.org/ws/2/',
                'headers': {'User-Agent': f"PreciseDigitalLeadGen/1.0 ({os.getenv('CONTACT_EMAIL', 'contact@precise.digital')})"},
                'description': '1 req/sec - respectful usage'
            },
            'spotify': {
                'requests_per_second': None,
                'requests_per_minute': int(os.getenv('SPOTIFY_RATE_LIMIT', 100)),
                'requests_per_day': None,
                'base_url': 'https://api.spotify.com/v1/',
                'api_key': None,
                'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
                'client_secret': os.getenv('SPOTIFY_CLIENT_SECRET'),
                'description': f"{os.getenv('SPOTIFY_RATE_LIMIT', 100)} req/min (varies by endpoint)"
            },
            'youtube': {
                'requests_per_second': None,
                'requests_per_minute': None,
                'quota_per_day': int(os.getenv('YOUTUBE_DAILY_QUOTA', 10000)),
                'quota_costs': {
                    'search': 100,
                    'videos': 1,
                    'channels': 1,
                    'playlists': 1,
                    'playlistItems': 1,
                    'commentThreads': 1
                },
                'base_url': 'https://www.googleapis.com/youtube/v3/',
                'api_key': os.getenv('YOUTUBE_API_KEY'),
                'description': f"{os.getenv('YOUTUBE_DAILY_QUOTA', 10000)} quota units/day"
            },
            'lastfm': {
                'requests_per_second': 5,
                'requests_per_minute': int(os.getenv('LASTFM_RATE_LIMIT', 250)),
                'requests_per_day': None,
                'base_url': 'https://ws.audioscrobbler.com/2.0/',
                'api_key': os.getenv('LASTFM_API_KEY'),
                'description': '5 req/sec when authenticated'
            },
            'discogs': {
                'requests_per_second': 1,
                'requests_per_minute': 60,
                'requests_per_day': None,
                'base_url': 'https://api.discogs.com/',
                'headers': {'User-Agent': f"PreciseDigitalLeadGen/1.0 ({os.getenv('CONTACT_EMAIL', 'contact@precise.digital')})"},
                'description': '60 req/min, 1 req/sec'
            },
            # Enhanced APIs for lyrics and metadata
            'genius': {
                'requests_per_minute': 100,
                'requests_per_hour': 1000,
                'requests_per_day': None,
                'base_url': 'https://api.genius.com',
                'api_key': os.getenv('GENIUS_API_KEY'),
                'headers': {'Authorization': f"Bearer {os.getenv('GENIUS_API_KEY')}"} if os.getenv('GENIUS_API_KEY') else {},
                'description': '100 req/min, 1000 req/hour'
            },
            'musixmatch': {
                'requests_per_minute': 20,
                'requests_per_hour': 1000,
                'requests_per_day': None,
                'base_url': 'https://api.musixmatch.com/ws/1.1',
                'api_key': os.getenv('MUSIXMATCH_API_KEY'),
                'description': '20 req/min, 1000 req/hour'
            },
            'lyricfind': {
                'requests_per_minute': 60,
                'requests_per_hour': 1000,
                'requests_per_day': None,
                'base_url': 'https://api.lyricfind.com',
                'api_key': os.getenv('LYRICFIND_API_KEY'),
                'description': '60 req/min, 1000 req/hour'
            }
        }
        
        # Request tracking with separate queues for different time windows
        self.request_history_second = defaultdict(deque)
        self.request_history_minute = defaultdict(deque)
        self.request_history_hour = defaultdict(deque)
        self.daily_counters = defaultdict(int)
        self.youtube_quota_used = 0
        self.last_reset = defaultdict(lambda: datetime.now().date())
        
        # HTTP session with proper configuration
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': f"PreciseDigitalLeadGen/1.0 ({os.getenv('CONTACT_EMAIL', 'contact@precise.digital')})"
        })
        
        # Set timeouts from environment
        self.timeout = int(os.getenv('SCRAPING_TIMEOUT', 10))
        
        logger.info("Enhanced rate limiter initialized with lyrics APIs")
        self._log_configuration()
    
    def _log_configuration(self):
        """Log the current configuration for debugging"""
        logger.info("Enhanced API Rate Limit Configuration:")
        for api_name, config in self.api_configs.items():
            logger.info(f"  {api_name}: {config.get('description', 'No description')}")
            if config.get('api_key'):
                logger.info(f"    API Key: {'✅ Configured' if config['api_key'] else '❌ Missing'}")
            elif config.get('client_id'):
                logger.info(f"    Client ID: {'✅ Configured' if config['client_id'] else '❌ Missing'}")
    
    def _clean_old_requests(self, api_name: str):
        """Remove old requests from tracking queues"""
        current_time = time.time()
        
        # Clean requests older than 1 second
        second_queue = self.request_history_second[api_name]
        while second_queue and current_time - second_queue[0] > 1.0:
            second_queue.popleft()
        
        # Clean requests older than 1 minute
        minute_queue = self.request_history_minute[api_name]
        while minute_queue and current_time - minute_queue[0] > 60.0:
            minute_queue.popleft()
        
        # Clean requests older than 1 hour
        hour_queue = self.request_history_hour[api_name]
        while hour_queue and current_time - hour_queue[0] > 3600.0:
            hour_queue.popleft()
    
    def _reset_daily_counter_if_needed(self, api_name: str):
        """Reset daily counters if it's a new day"""
        today = datetime.now().date()
        if self.last_reset[api_name] < today:
            self.daily_counters[api_name] = 0
            if api_name == 'youtube':
                self.youtube_quota_used = 0
            self.last_reset[api_name] = today
            logger.info(f"Daily counters reset for {api_name}")
    
    def _can_make_request(self, api_name: str, quota_cost: int = 1) -> tuple[bool, float]:
        """
        Enhanced rate limiting check including hourly limits
        Returns (can_make_request, wait_time_in_seconds)
        """
        config = self.api_configs.get(api_name)
        if not config:
            logger.warning(f"Unknown API: {api_name}")
            return False, 0
        
        self._clean_old_requests(api_name)
        self._reset_daily_counter_if_needed(api_name)
        
        current_time = time.time()
        
        # Check per-second limit
        if config.get('requests_per_second'):
            current_second_requests = len(self.request_history_second[api_name])
            if current_second_requests >= config['requests_per_second']:
                if self.request_history_second[api_name]:
                    oldest_request = self.request_history_second[api_name][0]
                    wait_time = 1.0 - (current_time - oldest_request)
                    if wait_time > 0:
                        return False, wait_time
        
        # Check per-minute limit
        if config.get('requests_per_minute'):
            current_minute_requests = len(self.request_history_minute[api_name])
            if current_minute_requests >= config['requests_per_minute']:
                if self.request_history_minute[api_name]:
                    oldest_request = self.request_history_minute[api_name][0]
                    wait_time = 60.0 - (current_time - oldest_request)
                    if wait_time > 0:
                        return False, wait_time
        
        # Check per-hour limit (for lyrics APIs)
        if config.get('requests_per_hour'):
            current_hour_requests = len(self.request_history_hour[api_name])
            if current_hour_requests >= config['requests_per_hour']:
                if self.request_history_hour[api_name]:
                    oldest_request = self.request_history_hour[api_name][0]
                    wait_time = 3600.0 - (current_time - oldest_request)
                    if wait_time > 0:
                        return False, wait_time
        
        # Check YouTube quota specifically
        if api_name == 'youtube' and config.get('quota_per_day'):
            if self.youtube_quota_used + quota_cost > config['quota_per_day']:
                tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                wait_time = (tomorrow - datetime.now()).total_seconds()
                return False, wait_time
        
        # Check other daily limits
        elif config.get('requests_per_day'):
            if self.daily_counters[api_name] >= config['requests_per_day']:
                tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                wait_time = (tomorrow - datetime.now()).total_seconds()
                return False, wait_time
        
        return True, 0
    
    def make_request(self, api_name: str, endpoint: str, params: Dict = None, 
                    headers: Dict = None, method: str = 'GET', quota_cost: int = None) -> Optional[Dict]:
        """Enhanced API request with lyrics API support"""
        
        config = self.api_configs.get(api_name)
        if not config:
            logger.error(f"Unknown API: {api_name}")
            return None
        
        # Determine quota cost for YouTube
        if api_name == 'youtube' and quota_cost is None:
            quota_cost = self._determine_youtube_quota_cost(endpoint)
        elif quota_cost is None:
            quota_cost = 1
        
        # Check if we can make the request
        can_request, wait_time = self._can_make_request(api_name, quota_cost)
        
        if not can_request:
            if wait_time > 3600:  # More than 1 hour
                logger.warning(f"Daily limit exceeded for {api_name}. Wait time: {wait_time/3600:.1f} hours")
                return None
            elif wait_time > 60:  # More than 1 minute but less than 1 hour
                logger.info(f"Rate limit exceeded for {api_name}. Wait time: {wait_time/60:.1f} minutes")
                return None
            else:
                logger.info(f"Rate limiting {api_name}. Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time + 0.1)  # Small buffer
        
        # Build URL
        base_url = config['base_url'].rstrip('/')
        endpoint = endpoint.lstrip('/')
        url = f"{base_url}/{endpoint}" if endpoint else base_url
        
        # Prepare headers
        request_headers = {}
        if config.get('headers'):
            request_headers.update(config['headers'])
        if headers:
            request_headers.update(headers)
        
        # Add API keys based on service
        if not params:
            params = {}
        
        if api_name == 'lastfm' and config.get('api_key'):
            params['api_key'] = config['api_key']
            params['format'] = 'json'
        elif api_name == 'youtube' and config.get('api_key'):
            params['key'] = config['api_key']
        elif api_name == 'musixmatch' and config.get('api_key'):
            params['apikey'] = config['api_key']
            params['format'] = 'json'
        elif api_name == 'lyricfind' and config.get('api_key'):
            params['apikey'] = config['api_key']
        
        try:
            # Record the request
            current_time = time.time()
            self.request_history_second[api_name].append(current_time)
            self.request_history_minute[api_name].append(current_time)
            self.request_history_hour[api_name].append(current_time)
            self.daily_counters[api_name] += 1
            
            # Track YouTube quota
            if api_name == 'youtube':
                self.youtube_quota_used += quota_cost
                logger.debug(f"YouTube quota used: +{quota_cost}, total: {self.youtube_quota_used}")
            
            logger.debug(f"Making {method} request to {api_name}: {url}")
            
            # Make the request
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=request_headers, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=params, headers=request_headers, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            # Parse response
            content_type = response.headers.get('content-type', '').lower()
            if 'application/json' in content_type:
                result = response.json()
                logger.debug(f"Successful {api_name} request")
                return result
            else:
                logger.debug(f"Non-JSON response from {api_name}")
                return {'text': response.text, 'status_code': response.status_code}
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout error for {api_name} request to {url}")
            return None
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 429:
                logger.warning(f"Rate limit hit for {api_name}: {e}")
            else:
                logger.error(f"HTTP error for {api_name}: {e} (Status: {e.response.status_code if e.response else 'Unknown'})")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {api_name}: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for {api_name}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in {api_name} request: {str(e)}")
            return None
    
    def _determine_youtube_quota_cost(self, endpoint: str) -> int:
        """Determine quota cost based on YouTube endpoint"""
        if 'search' in endpoint:
            return 100
        elif any(ep in endpoint for ep in ['videos', 'channels', 'playlists', 'playlistItems']):
            return 1
        elif 'commentThreads' in endpoint:
            return 1
        else:
            return 1  # Default cost
    
    def get_rate_limit_status(self) -> Dict:
        """Get comprehensive rate limit status for all APIs including enhanced ones"""
        status = {}
        
        for api_name, config in self.api_configs.items():
            self._clean_old_requests(api_name)
            self._reset_daily_counter_if_needed(api_name)
            
            # Basic counters
            requests_this_second = len(self.request_history_second[api_name])
            requests_this_minute = len(self.request_history_minute[api_name])
            requests_this_hour = len(self.request_history_hour[api_name])
            requests_today = self.daily_counters[api_name]
            
            api_status = {
                'requests_this_second': requests_this_second,
                'requests_this_minute': requests_this_minute,
                'requests_this_hour': requests_this_hour,
                'requests_today': requests_today,
                'description': config.get('description', ''),
                'configured': bool(config.get('api_key') or config.get('client_id'))
            }
            
            # Add limits and remaining counts
            if config.get('requests_per_second'):
                api_status.update({
                    'second_limit': config['requests_per_second'],
                    'second_remaining': max(0, config['requests_per_second'] - requests_this_second)
                })
            
            if config.get('requests_per_minute'):
                api_status.update({
                    'minute_limit': config['requests_per_minute'],
                    'minute_remaining': max(0, config['requests_per_minute'] - requests_this_minute)
                })
            
            if config.get('requests_per_hour'):
                api_status.update({
                    'hour_limit': config['requests_per_hour'],
                    'hour_remaining': max(0, config['requests_per_hour'] - requests_this_hour)
                })
            
            if config.get('requests_per_day'):
                api_status.update({
                    'daily_limit': config['requests_per_day'],
                    'daily_remaining': max(0, config['requests_per_day'] - requests_today)
                })
            
            # Special YouTube quota handling
            if api_name == 'youtube' and config.get('quota_per_day'):
                api_status.update({
                    'quota_used_today': self.youtube_quota_used,
                    'quota_limit_daily': config['quota_per_day'],
                    'quota_remaining_today': max(0, config['quota_per_day'] - self.youtube_quota_used)
                })
            
            status[api_name] = api_status
        
        return status
    
    def reset_counters(self, api_name: str = None):
        """Reset counters for testing (specify api_name or reset all)"""
        if api_name:
            self.request_history_second[api_name].clear()
            self.request_history_minute[api_name].clear()
            self.request_history_hour[api_name].clear()
            self.daily_counters[api_name] = 0
            if api_name == 'youtube':
                self.youtube_quota_used = 0
            logger.info(f"Counters reset for {api_name}")
        else:
            self.request_history_second.clear()
            self.request_history_minute.clear()
            self.request_history_hour.clear()
            self.daily_counters.clear()
            self.youtube_quota_used = 0
            self.last_reset.clear()
            logger.info("All counters reset")

# Global instance
rate_limiter = RateLimitManager()

# Enhanced convenience functions for lyrics APIs
def genius_request(endpoint: str, params: Dict = None) -> Optional[Dict]:
    """Make Genius API request"""
    return rate_limiter.make_request('genius', endpoint, params)

def musixmatch_request(endpoint: str, params: Dict = None) -> Optional[Dict]:
    """Make Musixmatch API request"""
    return rate_limiter.make_request('musixmatch', endpoint, params)

def lyricfind_request(endpoint: str, params: Dict = None) -> Optional[Dict]:
    """Make LyricFind API request"""
    return rate_limiter.make_request('lyricfind', endpoint, params)

# Existing convenience functions
def safe_request(api_name: str, endpoint: str, params: Dict = None, **kwargs) -> Optional[Dict]:
    """Make a safe API request with automatic error handling"""
    return rate_limiter.make_request(api_name, endpoint, params, **kwargs)

def get_rate_limits() -> Dict:
    """Get current rate limit status"""
    return rate_limiter.get_rate_limit_status()

def musicbrainz_request(endpoint: str, params: Dict = None) -> Optional[Dict]:
    """Make a MusicBrainz request with proper rate limiting (1 req/sec)"""
    return safe_request('musicbrainz', endpoint, params)

def youtube_search(query: str, max_results: int = 10) -> Optional[Dict]:
    """Make YouTube search (costs 100 quota units)"""
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'channel',
        'maxResults': max_results
    }
    return rate_limiter.make_request('youtube', 'search', params, quota_cost=100)

def youtube_channel_details(channel_id: str) -> Optional[Dict]:
    """Get YouTube channel details (costs 1 quota unit)"""
    params = {
        'part': 'snippet,statistics',
        'id': channel_id
    }
    return rate_limiter.make_request('youtube', 'channels', params, quota_cost=1)

def lastfm_artist_info(artist_name: str) -> Optional[Dict]:
    """Get Last.fm artist info (5 req/sec limit)"""
    params = {
        'method': 'artist.getinfo',
        'artist': artist_name
    }
    return safe_request('lastfm', '', params)

if __name__ == "__main__":
    # Test the enhanced rate limiter
    print("🎵 Prism Analytics Engine - Enhanced Rate Limiter Test")
    print("=" * 60)
    
    status = rate_limiter.get_rate_limit_status()
    for api, info in status.items():
        print(f"\n{api.upper()}:")
        print(f"  Description: {info.get('description', 'N/A')}")
        print(f"  Configured: {'✅ Yes' if info.get('configured') else '❌ No'}")
        
        if 'second_limit' in info:
            print(f"  Per second: {info['requests_this_second']}/{info['second_limit']}")
        if 'minute_limit' in info:
            print(f"  Per minute: {info['requests_this_minute']}/{info['minute_limit']}")
        if 'hour_limit' in info:
            print(f"  Per hour: {info['requests_this_hour']}/{info['hour_limit']}")
        if 'quota_limit_daily' in info:
            print(f"  Daily quota: {info['quota_used_today']}/{info['quota_limit_daily']}")
        
        print(f"  Today's requests: {info['requests_today']}")