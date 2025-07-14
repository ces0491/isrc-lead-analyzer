"""
Configuration management for Precise Digital Lead Generation Tool
"""
import os
try:
    from dotenv import load_dotenv  # Try to import dotenv
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables will be read from system.")
    def load_dotenv():
        pass

from dataclasses import dataclass
from typing import Optional, Dict, Any

# Load environment variables
load_dotenv()

@dataclass
class APIConfig:
    """API configuration settings"""
    name: str
    base_url: str
    requests_per_minute: int
    requests_per_day: Optional[int] = None
    api_key: Optional[str] = None
    headers: Optional[dict] = None

@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str
    echo: bool = False

@dataclass
class AppConfig:
    """Main application configuration"""
    debug: bool
    secret_key: str
    host: str = "0.0.0.0"
    port: int = 5000

class Settings:
    """Main settings class"""
    
    def __init__(self):
        # Application settings
        self.app = AppConfig(
            debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true',
            secret_key=os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
            host=os.getenv('FLASK_HOST', '0.0.0.0'),
            port=int(os.getenv('FLASK_PORT', 5000))
        )
        
        # Database settings
        self.database = DatabaseConfig(
            url=os.getenv('DATABASE_URL', 'sqlite:///data/leads.db'),
            echo=os.getenv('DATABASE_ECHO', 'false').lower() == 'true'
        )
        
        # API configurations
        self.apis = {
            'musicbrainz': APIConfig(
                name='musicbrainz',
                base_url='https://musicbrainz.org/ws/2/',
                requests_per_minute=60,
                headers={'User-Agent': 'PreciseDigitalLeadGen/1.0 (contact@precise.digital)'}
            ),
            'spotify': APIConfig(
                name='spotify',
                base_url='https://api.spotify.com/v1/',
                requests_per_minute=100,
                api_key=None  # Will be set via OAuth
            ),
            'lastfm': APIConfig(
                name='lastfm',
                base_url='http://ws.audioscrobbler.com/2.0/',
                requests_per_minute=300,
                api_key=os.getenv('LASTFM_API_KEY')
            ),
            'youtube': APIConfig(
                name='youtube',
                base_url='https://www.googleapis.com/youtube/v3/',
                requests_per_minute=100,
                requests_per_day=10000,
                api_key=os.getenv('YOUTUBE_API_KEY')
            )
        }
        
        # Spotify OAuth settings
        self.spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        # Redis for rate limiting
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        
        # Scoring weights
        self.scoring_weights = {
            'independence': {
                'self_released': 40,
                'indie_label': 25,
                'small_distributor': 15,
                'major_distributed': 0
            },
            'opportunity': {
                'missing_platforms': 20,
                'basic_distribution_only': 15,
                'no_publishing_admin': 10,
                'growing_streams': 15,
                'recent_activity': 10,
                'low_professional_presence': 10
            },
            'geographic': {
                'new_zealand': 30,
                'australia': 25,
                'pacific_islands': 20,
                'other_english_speaking': 10,
                'other': 5
            }
        }
        
        # Target regions for geographic scoring
        self.target_regions = {
            'new_zealand': ['NZ', 'New Zealand'],
            'australia': ['AU', 'Australia'],
            'pacific_islands': ['FJ', 'TO', 'WS', 'VU', 'PG', 'SB', 'FM', 'PW', 'MH', 'KI', 'NR', 'TV'],
            'other_english_speaking': ['US', 'CA', 'GB', 'IE', 'ZA']
        }
        
        # Platform identifiers for opportunity scoring
        self.major_platforms = [
            'spotify', 'apple_music', 'youtube_music', 'amazon_music',
            'deezer', 'tidal', 'bandcamp', 'soundcloud'
        ]
        
        # Validation settings
        self.max_bulk_isrcs = 1000
        self.max_retry_attempts = 3
        self.request_timeout = 30

    def validate_required_keys(self):
        """Validate that required API keys are present"""
        missing_keys = []
        
        if not self.spotify_client_id:
            missing_keys.append('SPOTIFY_CLIENT_ID')
        if not self.spotify_client_secret:
            missing_keys.append('SPOTIFY_CLIENT_SECRET')
            
        if missing_keys:
            print(f"Warning: Missing API keys: {', '.join(missing_keys)}")
            print("Some features may not work without these keys.")
            
        return len(missing_keys) == 0

    def get_api_config(self, api_name: str) -> Optional[APIConfig]:  # Fixed: Return type is now Optional[APIConfig]
        """Get configuration for specific API"""
        return self.apis.get(api_name)

# Global settings instance
settings = Settings()

# Validate configuration on import
settings.validate_required_keys()

class ProductionConfig:
    """Production configuration for Render deployment"""
    
    @property
    def app(self) -> Dict[str, Any]:
        return {
            'host': '0.0.0.0',
            'port': int(os.getenv('PORT', 5000)),
            'debug': False,
            'secret_key': os.getenv('SECRET_KEY', 'your-secret-key-here')
        }
    
    @property 
    def database_url(self) -> str:
        """Get PostgreSQL URL from environment"""
        db_url = os.getenv('DATABASE_URL')
        if db_url and db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        return db_url or 'sqlite:///data/leads.db'

# Add environment detection
def get_config():
    """Get configuration based on environment"""
    if os.getenv('RENDER'):
        return ProductionConfig()
    else:
        return settings  # Your existing development config
