"""
Application settings and configuration for Precise Digital Lead Generation Tool
Centralized configuration management with environment variable support
"""
import os
from typing import Dict, Any
from dataclasses import dataclass, field

@dataclass
class APIConfig:
    """Configuration for external API"""
    api_key: str = ""
    base_url: str = ""
    requests_per_minute: int = 60
    requests_per_day: int = None
    headers: Dict[str, str] = field(default_factory=dict)

@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = "sqlite:///data/precise_leads.db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    pool_pre_ping: bool = True

@dataclass
class AppConfig:
    """Application configuration"""
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 5000
    secret_key: str = "dev-secret-key-change-in-production"

class Settings:
    """Main settings class with all configuration"""
    
    def __init__(self):
        # App configuration
        self.app = AppConfig(
            debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
            host=os.getenv('HOST', '0.0.0.0'),
            port=int(os.getenv('PORT', 5000)),
            secret_key=os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        )
        
        # Database configuration
        self.database = DatabaseConfig(
            url=os.getenv('DATABASE_URL', 'sqlite:///data/precise_leads.db'),
            echo=os.getenv('DATABASE_ECHO', 'False').lower() == 'true'
        )
        
        # API configurations
        self.apis = {
            'musicbrainz': APIConfig(
                base_url='https://musicbrainz.org/ws/2/',
                requests_per_minute=1,  # Be respectful to MusicBrainz
                headers={'User-Agent': 'PreciseDigitalLeadGen/1.0 (contact@precise.digital)'}
            ),
            'spotify': APIConfig(
                base_url='https://api.spotify.com/v1/',
                requests_per_minute=100,
                requests_per_day=None
            ),
            'lastfm': APIConfig(
                api_key=os.getenv('LASTFM_API_KEY', ''),
                base_url='https://ws.audioscrobbler.com/2.0/',
                requests_per_minute=5,
                requests_per_day=None
            ),
            'youtube': APIConfig(
                api_key=os.getenv('YOUTUBE_API_KEY', ''),
                base_url='https://www.googleapis.com/youtube/v3/',
                requests_per_minute=100,
                requests_per_day=10000  # Free tier quota
            )
        }
        
        # Spotify credentials (separate from API config due to OAuth)
        self.spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID', '')
        self.spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET', '')
        
        # Contact information
        self.contact_email = os.getenv('CONTACT_EMAIL', 'contact@precise.digital')
        
        # Processing limits
        self.max_bulk_isrcs = int(os.getenv('MAX_BULK_ISRCS', 1000))
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', 30))
        
        # Target regions for geographic scoring
        self.target_regions = {
            'new_zealand': ['NZ', 'NEW ZEALAND'],
            'australia': ['AU', 'AUSTRALIA'],
            'pacific_islands': ['FJ', 'PG', 'SB', 'VU', 'NC', 'PF', 'WS', 'TO', 'TV', 'KI', 'NR', 'PW', 'MH', 'FM'],
            'other': []  # All other countries
        }
        
        # Major platforms for opportunity scoring
        self.major_platforms = [
            'spotify', 'apple_music', 'youtube_music', 'amazon_music',
            'deezer', 'tidal', 'bandcamp', 'soundcloud'
        ]
        
        # Scoring weights for lead qualification
        self.scoring_weights = {
            'independence': {
                'self_released': 40,
                'small_distributor': 35,
                'indie_label': 25,
                'major_distributed': 0
            },
            'opportunity': {
                'missing_platforms': 20,
                'basic_distribution_only': 15,
                'no_publishing_admin': 10,
                'growing_streams': 15,
                'recent_activity': 10,
                'low_professional_presence': 10,
                'youtube_opportunities': 15  # NEW: YouTube-specific opportunities
            },
            'geographic': {
                'new_zealand': 30,
                'australia': 25,
                'pacific_islands': 20,
                'other': 5
            }
        }
        
        # YouTube-specific settings
        self.youtube_settings = {
            'min_subscriber_threshold': 100,
            'high_potential_threshold': 10000,
            'engagement_rate_threshold': 0.05,
            'upload_frequency_scoring': {
                'very_active': 10,
                'active': 8,
                'moderate': 5,
                'low': 2,
                'inactive': 0
            }
        }
        
        # Contact discovery settings
        self.contact_discovery = {
            'max_contacts_per_artist': 15,
            'min_confidence_threshold': 20,
            'website_scraping_enabled': True,
            'social_platform_priority': [
                'youtube', 'instagram', 'twitter', 'facebook', 
                'soundcloud', 'bandcamp', 'tiktok'
            ]
        }
        
        # Prism Analytics branding
        self.prism_branding = {
            'company_name': 'Precise Digital',
            'analytics_engine': 'Prism Analytics Engine',
            'tagline': 'Transforming Music Data into Actionable Insights',
            'primary_color': '#1A1A1A',  # Prism Black
            'accent_color': '#E50914',   # Precise Red
            'logo_usage': 'Use Prism logo with proper spacing and color guidelines'
        }
    
    def get_api_config(self, api_name: str) -> APIConfig:
        """Get configuration for specific API"""
        return self.apis.get(api_name, APIConfig())
    
    def is_api_configured(self, api_name: str) -> bool:
        """Check if API is properly configured"""
        config = self.get_api_config(api_name)
        
        if api_name == 'musicbrainz':
            return True  # Always available
        elif api_name == 'spotify':
            return bool(self.spotify_client_id and self.spotify_client_secret)
        elif api_name in ['lastfm', 'youtube']:
            return bool(config.api_key)
        
        return False
    
    def get_database_url(self) -> str:
        """Get database URL with proper formatting"""
        url = self.database.url
        
        # Handle special case for SQLite in production
        if url.startswith('sqlite:///') and not os.path.exists('data'):
            os.makedirs('data', exist_ok=True)
        
        return url
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate current configuration and return status"""
        status = {
            'database': {
                'configured': bool(self.database.url),
                'url': self.database.url,
                'accessible': False
            },
            'apis': {},
            'required_directories': {
                'data': os.path.exists('data'),
                'logs': os.path.exists('logs')
            },
            'environment': {
                'debug_mode': self.app.debug,
                'port': self.app.port,
                'host': self.app.host
            }
        }
        
        # Test database accessibility
        try:
            import sqlalchemy
            engine = sqlalchemy.create_engine(self.get_database_url())
            with engine.connect():
                status['database']['accessible'] = True
        except Exception as e:
            status['database']['error'] = str(e)
        
        # Check API configurations
        for api_name in self.apis.keys():
            status['apis'][api_name] = {
                'configured': self.is_api_configured(api_name),
                'api_key_present': bool(self.get_api_config(api_name).api_key) if api_name != 'musicbrainz' else True,
                'base_url': self.get_api_config(api_name).base_url
            }
        
        # Special handling for Spotify
        status['apis']['spotify']['client_credentials'] = {
            'client_id': bool(self.spotify_client_id),
            'client_secret': bool(self.spotify_client_secret)
        }
        
        return status

# Global settings instance
settings = Settings()

# Environment-specific overrides
if os.getenv('RENDER'):  # Render.com deployment
    settings.app.host = '0.0.0.0'
    settings.app.port = int(os.getenv('PORT', 10000))
    settings.app.debug = False
    
elif os.getenv('HEROKU'):  # Heroku deployment
    settings.app.host = '0.0.0.0'
    settings.app.port = int(os.getenv('PORT', 5000))
    settings.app.debug = False

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
        }
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'detailed',
            'class': 'logging.FileHandler',
            'filename': 'logs/precise_digital.log',
            'mode': 'a',
        }
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
        'precise_digital': {
            'handlers': ['default', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

# Export commonly used settings
__all__ = [
    'settings',
    'Settings',
    'APIConfig',
    'DatabaseConfig',
    'AppConfig',
    'LOGGING_CONFIG'
]