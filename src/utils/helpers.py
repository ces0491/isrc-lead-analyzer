"""
Utility helper functions for the Precise Digital Lead Generation Tool
Common utilities used across the Prism Analytics Engine
"""

import re
import json
import hashlib
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Date and Time Utilities
def parse_flexible_date(date_string: str) -> Optional[datetime]:
    """
    Parse date string in various formats commonly found in music metadata
    
    Args:
        date_string: Date in various formats (YYYY, YYYY-MM, YYYY-MM-DD, etc.)
    
    Returns:
        datetime object or None if parsing fails
    """
    if not date_string:
        return None
    
    # Clean the date string
    date_clean = str(date_string).strip()
    
    # Common date formats in music data
    formats = [
        '%Y-%m-%d',          # 2024-03-15
        '%Y-%m',             # 2024-03
        '%Y',                # 2024
        '%d-%m-%Y',          # 15-03-2024
        '%m/%d/%Y',          # 03/15/2024
        '%d/%m/%Y',          # 15/03/2024
        '%Y%m%d',            # 20240315
        '%B %d, %Y',         # March 15, 2024
        '%b %d, %Y',         # Mar 15, 2024
        '%d %B %Y',          # 15 March 2024
        '%d %b %Y',          # 15 Mar 2024
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_clean, fmt)
        except ValueError:
            continue
    
    # Handle partial dates (year only, year-month)
    if re.match(r'^\d{4}$', date_clean):
        return datetime(int(date_clean), 1, 1)
    elif re.match(r'^\d{4}-\d{2}$', date_clean):
        year, month = date_clean.split('-')
        return datetime(int(year), int(month), 1)
    
    return None

def format_duration(milliseconds: int) -> str:
    """
    Format duration from milliseconds to human-readable format
    
    Args:
        milliseconds: Duration in milliseconds
    
    Returns:
        Formatted duration string (e.g., "3:45", "1:23:45")
    """
    if not milliseconds or milliseconds <= 0:
        return "0:00"
    
    seconds = milliseconds // 1000
    minutes = seconds // 60
    hours = minutes // 60
    
    seconds = seconds % 60
    minutes = minutes % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def days_since_date(date: Union[datetime, str]) -> Optional[int]:
    """
    Calculate days since a given date
    
    Args:
        date: datetime object or date string
    
    Returns:
        Number of days since the date, or None if invalid
    """
    if isinstance(date, str):
        date = parse_flexible_date(date)
    
    if not date:
        return None
    
    return (datetime.now() - date).days

# String Utilities
def clean_artist_name(name: str) -> str:
    """
    Clean artist name for consistent comparison and storage
    
    Args:
        name: Raw artist name
    
    Returns:
        Cleaned artist name
    """
    if not name:
        return ""
    
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', str(name).strip())
    
    # Remove common prefixes/suffixes that might cause duplicates
    # But preserve the artist's intended style
    patterns_to_clean = [
        r'\s*\(Official\)\s*$',
        r'\s*- Topic\s*$',
        r'\s*VEVO\s*$',
    ]
    
    for pattern in patterns_to_clean:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    return cleaned.strip()

def normalize_genre(genre: str) -> str:
    """
    Normalize genre string for consistent categorization
    
    Args:
        genre: Raw genre string
    
    Returns:
        Normalized genre
    """
    if not genre:
        return ""
    
    # Convert to lowercase and remove extra spaces
    normalized = re.sub(r'\s+', ' ', str(genre).lower().strip())
    
    # Common genre mappings
    genre_mappings = {
        'alternative rock': 'alternative',
        'alt rock': 'alternative',
        'indie rock': 'indie',
        'indie pop': 'indie',
        'electronic dance music': 'electronic',
        'edm': 'electronic',
        'hip hop': 'hip-hop',
        'hiphop': 'hip-hop',
        'rhythm and blues': 'r&b',
        'rnb': 'r&b',
        'country music': 'country',
        'folk music': 'folk',
        'classical music': 'classical',
        'pop music': 'pop',
        'rock music': 'rock'
    }
    
    return genre_mappings.get(normalized, normalized)

def extract_social_handle(url: str, platform: str) -> str:
    """
    Extract social media handle from URL
    
    Args:
        url: Social media URL
        platform: Platform name (instagram, twitter, etc.)
    
    Returns:
        Extracted handle or empty string
    """
    if not url:
        return ""
    
    patterns = {
        'instagram': r'instagram\.com/([a-zA-Z0-9_.]+)',
        'twitter': r'twitter\.com/([a-zA-Z0-9_]+)',
        'youtube': r'youtube\.com/(?:c/|channel/|user/|@)([a-zA-Z0-9_.-]+)',
        'facebook': r'facebook\.com/([a-zA-Z0-9.]+)',
        'tiktok': r'tiktok\.com/@([a-zA-Z0-9_.]+)',
        'soundcloud': r'soundcloud\.com/([a-zA-Z0-9_-]+)',
        'bandcamp': r'([a-zA-Z0-9_-]+)\.bandcamp\.com'
    }
    
    pattern = patterns.get(platform.lower())
    if pattern:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return ""

# Number and Data Utilities
def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to integer
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
    
    Returns:
        Integer value or default
    """
    if value is None:
        return default
    
    if isinstance(value, int):
        return value
    
    try:
        # Handle string numbers with commas
        if isinstance(value, str):
            value = value.replace(',', '').replace(' ', '')
        return int(float(value))
    except (ValueError, TypeError):
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
    
    Returns:
        Float value or default
    """
    if value is None:
        return default
    
    if isinstance(value, (int, float)):
        return float(value)
    
    try:
        if isinstance(value, str):
            value = value.replace(',', '').replace(' ', '')
        return float(value)
    except (ValueError, TypeError):
        return default

def format_number(number: Union[int, float], precision: int = 0) -> str:
    """
    Format number with thousands separators
    
    Args:
        number: Number to format
        precision: Decimal places
    
    Returns:
        Formatted number string
    """
    if number is None:
        return "0"
    
    try:
        if precision == 0:
            return f"{int(number):,}"
        else:
            return f"{float(number):,.{precision}f}"
    except (ValueError, TypeError):
        return str(number)

def calculate_percentage(part: Union[int, float], total: Union[int, float], precision: int = 1) -> float:
    """
    Calculate percentage with safe division
    
    Args:
        part: Part value
        total: Total value
        precision: Decimal places
    
    Returns:
        Percentage value
    """
    if not total or total == 0:
        return 0.0
    
    try:
        percentage = (float(part) / float(total)) * 100
        return round(percentage, precision)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0

# URL and Web Utilities
def is_valid_url(url: str) -> bool:
    """
    Check if URL is valid
    
    Args:
        url: URL to validate
    
    Returns:
        True if valid URL, False otherwise
    """
    if not url:
        return False
    
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def clean_url(url: str) -> str:
    """
    Clean and normalize URL
    
    Args:
        url: Raw URL
    
    Returns:
        Cleaned URL
    """
    if not url:
        return ""
    
    url = url.strip()
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Remove trailing slash
    url = url.rstrip('/')
    
    return url

def extract_domain(url: str) -> str:
    """
    Extract domain from URL
    
    Args:
        url: URL string
    
    Returns:
        Domain name or empty string
    """
    if not url:
        return ""
    
    try:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain
    except Exception:
        return ""

# Data Processing Utilities
def merge_dictionaries(*dicts: Dict[str, Any], strategy: str = 'last_wins') -> Dict[str, Any]:
    """
    Merge multiple dictionaries with conflict resolution
    
    Args:
        *dicts: Dictionaries to merge
        strategy: Merge strategy ('last_wins', 'first_wins', 'combine_lists')
    
    Returns:
        Merged dictionary
    """
    if not dicts:
        return {}
    
    result = {}
    
    for d in dicts:
        if not isinstance(d, dict):
            continue
        
        for key, value in d.items():
            if key not in result:
                result[key] = value
            else:
                if strategy == 'last_wins':
                    result[key] = value
                elif strategy == 'first_wins':
                    continue  # Keep existing value
                elif strategy == 'combine_lists':
                    if isinstance(result[key], list) and isinstance(value, list):
                        result[key] = list(set(result[key] + value))  # Combine and deduplicate
                    else:
                        result[key] = value
    
    return result

def deduplicate_list(items: List[Any], key_func: Optional[callable] = None) -> List[Any]:
    """
    Remove duplicates from list while preserving order
    
    Args:
        items: List of items
        key_func: Function to extract comparison key
    
    Returns:
        Deduplicated list
    """
    if not items:
        return []
    
    seen = set()
    result = []
    
    for item in items:
        key = key_func(item) if key_func else item
        
        if key not in seen:
            seen.add(key)
            result.append(item)
    
    return result

def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks of specified size
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
    
    Returns:
        List of chunks
    """
    if chunk_size <= 0:
        return [items] if items else []
    
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]

# Scoring and Analytics Utilities
def normalize_score(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float], 
                   target_min: int = 0, target_max: int = 100) -> int:
    """
    Normalize a value to a target range
    
    Args:
        value: Value to normalize
        min_val: Minimum value of input range
        max_val: Maximum value of input range
        target_min: Minimum value of target range
        target_max: Maximum value of target range
    
    Returns:
        Normalized value
    """
    if max_val == min_val:
        return target_min
    
    try:
        # Normalize to 0-1 range
        normalized = (float(value) - float(min_val)) / (float(max_val) - float(min_val))
        
        # Scale to target range
        scaled = normalized * (target_max - target_min) + target_min
        
        # Clamp to target range
        return max(target_min, min(target_max, int(round(scaled))))
    except (ValueError, TypeError, ZeroDivisionError):
        return target_min

def calculate_growth_rate(old_value: Union[int, float], new_value: Union[int, float]) -> float:
    """
    Calculate growth rate percentage
    
    Args:
        old_value: Previous value
        new_value: Current value
    
    Returns:
        Growth rate as percentage
    """
    if not old_value or old_value == 0:
        return 0.0 if new_value == 0 else 100.0
    
    try:
        growth = ((float(new_value) - float(old_value)) / float(old_value)) * 100
        return round(growth, 2)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0

# File and Path Utilities
def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        path: Directory path
    
    Returns:
        Path object
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj

def get_file_size_mb(file_path: Union[str, Path]) -> float:
    """
    Get file size in megabytes
    
    Args:
        file_path: Path to file
    
    Returns:
        File size in MB
    """
    try:
        size_bytes = Path(file_path).stat().st_size
        return round(size_bytes / (1024 * 1024), 2)
    except (OSError, FileNotFoundError):
        return 0.0

def generate_filename(base_name: str, extension: str = '', timestamp: bool = True) -> str:
    """
    Generate filename with optional timestamp
    
    Args:
        base_name: Base filename
        extension: File extension (with or without dot)
        timestamp: Whether to include timestamp
    
    Returns:
        Generated filename
    """
    # Clean base name
    base_clean = re.sub(r'[^\w\-_.]', '_', base_name)
    
    # Add timestamp if requested
    if timestamp:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_clean = f"{base_clean}_{ts}"
    
    # Add extension
    if extension:
        if not extension.startswith('.'):
            extension = '.' + extension
        return base_clean + extension
    
    return base_clean

# Hashing and Security Utilities
def generate_hash(data: str, algorithm: str = 'md5') -> str:
    """
    Generate hash of string data
    
    Args:
        data: Data to hash
        algorithm: Hash algorithm (md5, sha1, sha256)
    
    Returns:
        Hex hash string
    """
    if not data:
        return ""
    
    try:
        if algorithm == 'md5':
            return hashlib.md5(data.encode()).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(data.encode()).hexdigest()
        elif algorithm == 'sha256':
            return hashlib.sha256(data.encode()).hexdigest()
        else:
            return hashlib.md5(data.encode()).hexdigest()
    except Exception:
        return ""

def create_cache_key(*args: Any) -> str:
    """
    Create cache key from arguments
    
    Args:
        *args: Arguments to include in key
    
    Returns:
        Cache key string
    """
    key_parts = []
    for arg in args:
        if isinstance(arg, (dict, list)):
            key_parts.append(json.dumps(arg, sort_keys=True))
        else:
            key_parts.append(str(arg))
    
    combined = '|'.join(key_parts)
    return generate_hash(combined, 'md5')[:16]  # Short hash for cache keys

# Logging Utilities
def log_function_call(func_name: str, args: Tuple = (), kwargs: Dict = None, 
                     result: Any = None, duration: float = None):
    """
    Log function call details for debugging
    
    Args:
        func_name: Name of the function
        args: Function arguments
        kwargs: Function keyword arguments
        result: Function result
        duration: Execution duration in seconds
    """
    kwargs = kwargs or {}
    
    log_data = {
        'function': func_name,
        'args_count': len(args),
        'kwargs_count': len(kwargs),
        'has_result': result is not None,
        'duration_ms': round(duration * 1000, 2) if duration else None
    }
    
    logger.debug(f"Function call: {func_name}", extra=log_data)

# YouTube Specific Utilities
def parse_youtube_duration(duration: str) -> int:
    """
    Parse YouTube duration format (PT4M13S) to seconds
    
    Args:
        duration: YouTube duration string
    
    Returns:
        Duration in seconds
    """
    if not duration:
        return 0
    
    # YouTube uses ISO 8601 duration format: PT4M13S
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration)
    
    if not match:
        return 0
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    return hours * 3600 + minutes * 60 + seconds

def extract_youtube_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from various URL formats
    
    Args:
        url: YouTube URL
    
    Returns:
        Video ID or None
    """
    if not url:
        return None
    
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

# Testing Utilities
def create_test_data(data_type: str, count: int = 1) -> Union[Dict, List[Dict]]:
    """
    Create test data for various components
    
    Args:
        data_type: Type of test data (artist, track, contact)
        count: Number of records to create
    
    Returns:
        Test data dictionary or list
    """
    import random
    
    def create_artist():
        return {
            'name': f'Test Artist {random.randint(1, 1000)}',
            'country': random.choice(['NZ', 'AU', 'US', 'GB']),
            'genre': random.choice(['indie', 'rock', 'electronic', 'folk']),
            'monthly_listeners': random.randint(1000, 100000),
            'total_score': round(random.uniform(30, 95), 1),
            'lead_tier': random.choice(['A', 'B', 'C', 'D'])
        }
    
    def create_track():
        return {
            'isrc': f'TEST{random.randint(10000000, 99999999)}',
            'title': f'Test Song {random.randint(1, 1000)}',
            'duration_ms': random.randint(120000, 360000),
            'release_date': f'2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}'
        }
    
    def create_contact():
        return {
            'type': random.choice(['email', 'social', 'website']),
            'value': f'test{random.randint(1, 1000)}@example.com',
            'confidence': random.randint(50, 95),
            'source': 'test_data'
        }
    
    generators = {
        'artist': create_artist,
        'track': create_track,
        'contact': create_contact
    }
    
    if data_type not in generators:
        raise ValueError(f"Unknown data type: {data_type}")
    
    if count == 1:
        return generators[data_type]()
    else:
        return [generators[data_type]() for _ in range(count)]

# Main utility class for common operations
class PrismUtils:
    """
    Main utility class combining common operations for the Prism Analytics Engine
    """
    
    @staticmethod
    def clean_and_validate_isrc(isrc: str) -> Tuple[bool, str]:
        """Clean and validate ISRC (wrapper for validators)"""
        from src.utils.validators import validate_isrc
        return validate_isrc(isrc)
    
    @staticmethod
    def format_lead_score(score: float) -> str:
        """Format lead score for display"""
        if score >= 80:
            return f"🔥 {score:.1f}"
        elif score >= 60:
            return f"⭐ {score:.1f}"
        elif score >= 40:
            return f"📈 {score:.1f}"
        else:
            return f"📊 {score:.1f}"
    
    @staticmethod
    def get_tier_emoji(tier: str) -> str:
        """Get emoji for lead tier"""
        tier_emojis = {
            'A': '🥇',
            'B': '🥈', 
            'C': '🥉',
            'D': '📋'
        }
        return tier_emojis.get(tier.upper(), '❓')
    
    @staticmethod
    def format_social_reach(followers: int) -> str:
        """Format social media reach numbers"""
        if followers >= 1000000:
            return f"{followers / 1000000:.1f}M"
        elif followers >= 1000:
            return f"{followers / 1000:.1f}K"
        else:
            return str(followers)

# Export commonly used functions
__all__ = [
    'parse_flexible_date', 'format_duration', 'days_since_date',
    'clean_artist_name', 'normalize_genre', 'extract_social_handle',
    'safe_int', 'safe_float', 'format_number', 'calculate_percentage',
    'is_valid_url', 'clean_url', 'extract_domain',
    'merge_dictionaries', 'deduplicate_list', 'chunk_list',
    'normalize_score', 'calculate_growth_rate',
    'ensure_directory', 'get_file_size_mb', 'generate_filename',
    'generate_hash', 'create_cache_key',
    'parse_youtube_duration', 'extract_youtube_video_id',
    'create_test_data', 'PrismUtils'
]