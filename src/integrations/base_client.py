"""
Refactored base API client with common functionality for music lead generation.
Precise Digital - Music Services Lead Generation Tool

This module provides the base class for all API clients and imports
all specific client implementations for backward compatibility.
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


# Import all client implementations for backward compatibility
from .musicbrainz import MusicBrainzClient, musicbrainz_client
from .spotify import SpotifyClient, spotify_client
from .lastfm import LastFmClient, lastfm_client
from .youtube import YouTubeClient, youtube_client

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
]