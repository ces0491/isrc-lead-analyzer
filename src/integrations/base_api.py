"""
Base API client class - separated to avoid circular imports
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote
from config.settings import settings


class BaseAPIClient:
    """Base class for API clients with common functionality"""
    
    def __init__(self, api_name: str):
        self.api_name = api_name
        self._rate_limiter = None
    
    @property
    def rate_limiter(self):
        """Lazy import of rate limiter to avoid circular imports"""
        if self._rate_limiter is None:
            from src.core.rate_limiter import rate_limiter
            self._rate_limiter = rate_limiter
        return self._rate_limiter
    
    def _normalize_country_code(self, country):
        if not country:
            return None
        country = country.upper().strip()
        country_mappings = {
            'NEW ZEALAND': 'NZ', 'AUSTRALIA': 'AU', 'UNITED STATES': 'US',
            'UNITED KINGDOM': 'GB', 'CANADA': 'CA'
        }
        return country_mappings.get(country, country)
    
    def _parse_date(self, date_str):
        if not date_str:
            return None
        formats = ['%Y-%m-%d', '%Y-%m', '%Y', '%d-%m-%Y', '%m/%d/%Y']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    def _parse_number(self, value):
        if not value:
            return 0
        try:
            if isinstance(value, str):
                value = value.replace(',', '')
            return int(value)
        except (ValueError, TypeError):
            return 0
