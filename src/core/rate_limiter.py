"""
Rate limiting system for API calls - Production version without aiohttp
Respects free tier limitations while maximizing throughput
"""
import time
import json
from typing import Dict, List, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta
import requests
from config.settings import settings

class RateLimitManager:
    """
    Manages rate limits for multiple APIs with different constraints
    Production version without async dependencies
    """
    
    def __init__(self):
        self.api_configs = settings.apis
        self.request_history = defaultdict(deque)  # Track request timestamps
        self.daily_counters = defaultdict(int)     # Track daily usage
        self.last_reset = defaultdict(datetime)    # Track daily resets
        self.session = requests.Session()
        
        # Setup user agents for respectful scraping
        contact_email = getattr(settings, 'contact_email', 'contact@precise.digital')
        self.session.headers.update({
            'User-Agent': f'PreciseDigitalLeadGen/1.0 ({contact_email})'
        })
    
    def _clean_old_requests(self, api_name: str):
        """Remove requests older than 1 minute from history"""
        cutoff_time = time.time() - 60
        history = self.request_history[api_name]
        
        while history and history[0] < cutoff_time:
            history.popleft()
    
    def _reset_daily_counter_if_needed(self, api_name: str):
        """Reset daily counter if it's a new day"""
        now = datetime.now()
        last_reset = self.last_reset.get(api_name, datetime.min)
        
        if now.date() > last_reset.date():
            self.daily_counters[api_name] = 0
            self.last_reset[api_name] = now
    
    def _can_make_request(self, api_name: str) -> tuple[bool, float]:
        """
        Check if we can make a request to the API
        Returns (can_request, wait_time_seconds)
        """
        config = self.api_configs.get(api_name)
        if not config:
            return False, 0
        
        self._clean_old_requests(api_name)
        self._reset_daily_counter_if_needed(api_name)
        
        # Check per-minute limit
        current_requests = len(self.request_history[api_name])
        if current_requests >= config.requests_per_minute:
            # Calculate wait time
            oldest_request = self.request_history[api_name][0]
            wait_time = 61 - (time.time() - oldest_request)
            return False, max(0, wait_time)
        
        # Check daily limit if applicable
        if config.requests_per_day:
            if self.daily_counters[api_name] >= config.requests_per_day:
                # Calculate wait time until next day
                tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                wait_time = (tomorrow - datetime.now()).total_seconds()
                return False, wait_time
        
        return True, 0
    
    def make_request(self, api_name: str, endpoint: str, params: Dict = None, 
                    headers: Dict = None, method: str = 'GET') -> Optional[Dict]:
        """Make a rate-limited synchronous API request"""
        
        can_request, wait_time = self._can_make_request(api_name)
        
        if not can_request:
            if wait_time > 300:  # More than 5 minutes
                print(f"Rate limit exceeded for {api_name}. Wait time: {wait_time/3600:.1f} hours")
                return None
            else:
                print(f"Rate limiting {api_name}. Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time + 1)
        
        config = self.api_configs[api_name]
        url = config.base_url + endpoint.lstrip('/')
        
        # Prepare headers
        request_headers = {}
        if config.headers:
            request_headers.update(config.headers)
        if headers:
            request_headers.update(headers)
        
        # Add API key if available
        if config.api_key and api_name == 'lastfm':
            if not params:
                params = {}
            params['api_key'] = config.api_key
            params['format'] = 'json'
        elif config.api_key and api_name == 'youtube':
            if not params:
                params = {}
            params['key'] = config.api_key
        
        try:
            # Record the request with consistent timestamp
            current_time = time.time()
            self.request_history[api_name].append(current_time)
            self.daily_counters[api_name] += 1
            
            # Make the request
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=request_headers, 
                                          timeout=settings.request_timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=params, headers=request_headers,
                                           timeout=settings.request_timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            # Handle different response types
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                return response.json()
            else:
                return {'text': response.text, 'status_code': response.status_code}
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {api_name}: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response from {api_name}: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error in make_request for {api_name}: {str(e)}")
            return None
    
    def get_rate_limit_status(self) -> Dict:
        """Get current rate limit status for all APIs"""
        status = {}
        
        for api_name, config in self.api_configs.items():
            self._clean_old_requests(api_name)
            self._reset_daily_counter_if_needed(api_name)
            
            current_minute_requests = len(self.request_history[api_name])
            current_day_requests = self.daily_counters[api_name]
            
            status[api_name] = {
                'requests_this_minute': current_minute_requests,
                'minute_limit': config.requests_per_minute,
                'minute_remaining': config.requests_per_minute - current_minute_requests,
                'requests_today': current_day_requests,
                'daily_limit': config.requests_per_day,
                'daily_remaining': (config.requests_per_day - current_day_requests) if config.requests_per_day else None
            }
        
        return status
    
    def estimate_batch_time(self, api_name: str, num_requests: int) -> float:
        """Estimate how long a batch of requests will take"""
        config = self.api_configs.get(api_name)
        if not config:
            return 0
        
        # Calculate based on per-minute limits
        requests_per_second = config.requests_per_minute / 60
        estimated_seconds = num_requests / requests_per_second
        
        # Add buffer for rate limiting and processing
        estimated_seconds *= 1.2  # 20% buffer
        
        return estimated_seconds
    
    def reset_counters(self):
        """Reset all counters (for testing purposes)"""
        self.request_history.clear()
        self.daily_counters.clear()
        self.last_reset.clear()

# Global rate limiter instance
rate_limiter = RateLimitManager()

# Utility functions for common operations
def safe_request(api_name: str, endpoint: str, params: Dict = None, **kwargs) -> Optional[Dict]:
    """Make a safe API request with error handling"""
    try:
        return rate_limiter.make_request(api_name, endpoint, params, **kwargs)
    except Exception as e:
        print(f"Unexpected error in safe_request for {api_name}: {str(e)}")
        return None

if __name__ == "__main__":
    # Test the rate limiter
    print("Rate Limit Status:")
    status = rate_limiter.get_rate_limit_status()
    for api, info in status.items():
        print(f"{api}: {info['minute_remaining']}/{info['minute_limit']} requests remaining this minute")