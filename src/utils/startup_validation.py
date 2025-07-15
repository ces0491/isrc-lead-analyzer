"""
Comprehensive startup validation for Precise Digital Lead Generation Tool
Validates environment, dependencies, API configurations, and system readiness
Part of the Prism Analytics Engine
"""

import os
import sys
import importlib
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime

# Add project root to path if not already there
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

class ValidationResult:
    """Container for validation results"""
    
    def __init__(self, category: str, name: str, passed: bool, message: str, details: Optional[Dict] = None):
        self.category = category
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.utcnow()

class StartupValidator:
    """
    Comprehensive startup validation system for the Prism Analytics Engine
    Checks all critical components before application starts
    """
    
    def __init__(self):
        self.results: List[ValidationResult] = []
        self.logger = self._setup_logger()
        self.critical_dependencies = [
            'flask', 'sqlalchemy', 'requests', 'beautifulsoup4', 
            'pandas', 'xlsxwriter'
        ]
        self.optional_dependencies = [
            'reportlab', 'gunicorn', 'psycopg2'
        ]
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for validation"""
        logger = logging.getLogger('startup_validator')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def validate_all(self) -> bool:
        """
        Run all validation checks
        Returns True if all critical validations pass
        """
        self.logger.info("🔍 Starting comprehensive system validation...")
        self.results.clear()
        
        # Core validations (must pass)
        self._validate_python_version()
        self._validate_dependencies()
        self._validate_project_structure()
        self._validate_configuration()
        self._validate_environment_variables()
        self._validate_database()
        self._validate_api_integrations()
        
        # Additional validations (warnings only)
        self._validate_optional_features()
        self._validate_performance_requirements()
        self._validate_security_settings()
        
        # Generate summary report
        return self._generate_validation_report()
    
    def _validate_python_version(self):
        """Validate Python version compatibility"""
        try:
            version_info = sys.version_info
            required_version = (3, 8)
            
            if version_info >= required_version:
                self.results.append(ValidationResult(
                    'System', 'Python Version', True,
                    f"Python {version_info.major}.{version_info.minor}.{version_info.micro} (required: {required_version[0]}.{required_version[1]}+)",
                    {'version': f"{version_info.major}.{version_info.minor}.{version_info.micro}"}
                ))
            else:
                self.results.append(ValidationResult(
                    'System', 'Python Version', False,
                    f"Python {version_info.major}.{version_info.minor} is too old (required: {required_version[0]}.{required_version[1]}+)"
                ))
        except Exception as e:
            self.results.append(ValidationResult(
                'System', 'Python Version', False,
                f"Failed to check Python version: {e}"
            ))
    
    def _validate_dependencies(self):
        """Validate critical Python dependencies"""
        
        # Check critical dependencies
        for package in self.critical_dependencies:
            try:
                importlib.import_module(package)
                self.results.append(ValidationResult(
                    'Dependencies', f'Critical: {package}', True,
                    f"{package} is available"
                ))
            except ImportError:
                self.results.append(ValidationResult(
                    'Dependencies', f'Critical: {package}', False,
                    f"{package} is not installed (required)"
                ))
        
        # Check optional dependencies
        for package in self.optional_dependencies:
            try:
                importlib.import_module(package)
                self.results.append(ValidationResult(
                    'Dependencies', f'Optional: {package}', True,
                    f"{package} is available"
                ))
            except ImportError:
                self.results.append(ValidationResult(
                    'Dependencies', f'Optional: {package}', True,  # Not critical
                    f"{package} is not installed (optional feature may be disabled)"
                ))
    
    def _validate_project_structure(self):
        """Validate project directory structure"""
        
        required_directories = [
            'src', 'src/api', 'src/core', 'src/integrations', 
            'src/services', 'src/utils', 'config'
        ]
        
        required_files = [
            'run.py', 'requirements.txt',
            'config/settings.py', 'config/database.py',
            'src/api/routes.py', 'src/core/pipeline.py',
            'src/core/rate_limiter.py', 'src/core/scoring.py'
        ]
        
        # Check directories
        for directory in required_directories:
            dir_path = project_root / directory
            if dir_path.exists() and dir_path.is_dir():
                self.results.append(ValidationResult(
                    'Project Structure', f'Directory: {directory}', True,
                    f"Directory exists: {directory}"
                ))
            else:
                self.results.append(ValidationResult(
                    'Project Structure', f'Directory: {directory}', False,
                    f"Missing directory: {directory}"
                ))
        
        # Check files
        for file_path in required_files:
            full_path = project_root / file_path
            if full_path.exists() and full_path.is_file():
                # Check if file has content
                if full_path.stat().st_size > 0:
                    self.results.append(ValidationResult(
                        'Project Structure', f'File: {file_path}', True,
                        f"File exists and has content: {file_path}"
                    ))
                else:
                    self.results.append(ValidationResult(
                        'Project Structure', f'File: {file_path}', False,
                        f"File exists but is empty: {file_path}"
                    ))
            else:
                self.results.append(ValidationResult(
                    'Project Structure', f'File: {file_path}', False,
                    f"Missing file: {file_path}"
                ))
    
    def _validate_configuration(self):
        """Validate configuration files and settings"""
        
        try:
            # Test settings import
            from config.settings import settings
            
            self.results.append(ValidationResult(
                'Configuration', 'Settings Import', True,
                "Settings module imported successfully"
            ))
            
            # Validate configuration completeness
            config_status = settings.validate_configuration()
            
            # Database configuration
            if config_status['database']['configured']:
                self.results.append(ValidationResult(
                    'Configuration', 'Database Config', True,
                    f"Database configured: {config_status['database']['url']}"
                ))
            else:
                self.results.append(ValidationResult(
                    'Configuration', 'Database Config', False,
                    "Database configuration missing or invalid"
                ))
            
            # API configurations
            api_configs = config_status['apis']
            for api_name, api_status in api_configs.items():
                if api_name == 'musicbrainz':
                    # MusicBrainz is always available
                    self.results.append(ValidationResult(
                        'Configuration', f'API: {api_name}', True,
                        f"{api_name} is always available"
                    ))
                else:
                    if api_status['configured']:
                        self.results.append(ValidationResult(
                            'Configuration', f'API: {api_name}', True,
                            f"{api_name} API configured"
                        ))
                    else:
                        # Not critical for startup, but noted
                        self.results.append(ValidationResult(
                            'Configuration', f'API: {api_name}', True,
                            f"{api_name} API not configured (feature will be limited)"
                        ))
        
        except ImportError as e:
            self.results.append(ValidationResult(
                'Configuration', 'Settings Import', False,
                f"Failed to import settings: {e}"
            ))
        except Exception as e:
            self.results.append(ValidationResult(
                'Configuration', 'Settings Validation', False,
                f"Configuration validation failed: {e}"
            ))
    
    def _validate_environment_variables(self):
        """Validate environment variables"""
        
        # Critical environment variables
        critical_env_vars = {
            'SECRET_KEY': 'Flask secret key for security'
        }
        
        # Optional but recommended environment variables
        optional_env_vars = {
            'SPOTIFY_CLIENT_ID': 'Spotify API integration',
            'SPOTIFY_CLIENT_SECRET': 'Spotify API integration',
            'YOUTUBE_API_KEY': 'YouTube Data API integration',
            'LASTFM_API_KEY': 'Last.fm API integration',
            'DATABASE_URL': 'Database connection',
            'FLASK_DEBUG': 'Debug mode setting'
        }
        
        # Check critical variables
        for var_name, description in critical_env_vars.items():
            value = os.getenv(var_name)
            if value:
                self.results.append(ValidationResult(
                    'Environment', f'Critical: {var_name}', True,
                    f"{var_name} is set"
                ))
            else:
                self.results.append(ValidationResult(
                    'Environment', f'Critical: {var_name}', False,
                    f"{var_name} not set ({description})"
                ))
        
        # Check optional variables
        for var_name, description in optional_env_vars.items():
            value = os.getenv(var_name)
            if value:
                # Hide sensitive values
                display_value = f"{value[:8]}..." if len(value) > 8 else "***"
                self.results.append(ValidationResult(
                    'Environment', f'Optional: {var_name}', True,
                    f"{var_name} is configured ({display_value})"
                ))
            else:
                self.results.append(ValidationResult(
                    'Environment', f'Optional: {var_name}', True,  # Not critical
                    f"{var_name} not set ({description} will be unavailable)"
                ))
    
    def _validate_database(self):
        """Validate database connectivity and structure"""
        
        try:
            from config.database import DatabaseManager, init_db
            
            # Test database initialization
            try:
                db_manager = DatabaseManager()
                self.results.append(ValidationResult(
                    'Database', 'Connection', True,
                    "Database connection established"
                ))
                
                # Test basic query
                with db_manager as db:
                    from sqlalchemy import text
                    result = db.session.execute(text("SELECT 1")).scalar()
                    if result == 1:
                        self.results.append(ValidationResult(
                            'Database', 'Query Test', True,
                            "Database query test successful"
                        ))
                    else:
                        self.results.append(ValidationResult(
                            'Database', 'Query Test', False,
                            "Database query test failed"
                        ))
                
                # Test table existence
                from config.database import Artist, Track
                try:
                    artist_count = db.session.query(Artist).count()
                    track_count = db.session.query(Track).count()
                    
                    self.results.append(ValidationResult(
                        'Database', 'Tables', True,
                        f"Database tables accessible (Artists: {artist_count}, Tracks: {track_count})"
                    ))
                except Exception as e:
                    # Tables might not exist yet - try to create them
                    try:
                        init_db()
                        self.results.append(ValidationResult(
                            'Database', 'Tables', True,
                            "Database tables created successfully"
                        ))
                    except Exception as create_error:
                        self.results.append(ValidationResult(
                            'Database', 'Tables', False,
                            f"Failed to create database tables: {create_error}"
                        ))
            
            except Exception as e:
                self.results.append(ValidationResult(
                    'Database', 'Connection', False,
                    f"Database connection failed: {e}"
                ))
        
        except ImportError as e:
            self.results.append(ValidationResult(
                'Database', 'Import', False,
                f"Failed to import database modules: {e}"
            ))
    
    def _validate_api_integrations(self):
        """Validate API client integrations"""
        
        try:
            from src.integrations.base_client import (
                musicbrainz_client, spotify_client, lastfm_client, youtube_client
            )
            
            # Test client availability
            clients = {
                'MusicBrainz': musicbrainz_client,
                'Spotify': spotify_client,
                'Last.fm': lastfm_client,
                'YouTube': youtube_client
            }
            
            for client_name, client in clients.items():
                try:
                    # Check if client is properly initialized
                    if hasattr(client, 'api_name'):
                        self.results.append(ValidationResult(
                            'API Clients', client_name, True,
                            f"{client_name} client initialized"
                        ))
                    else:
                        self.results.append(ValidationResult(
                            'API Clients', client_name, True,
                            f"{client_name} client available (fallback mode)"
                        ))
                except Exception as e:
                    self.results.append(ValidationResult(
                        'API Clients', client_name, False,
                        f"{client_name} client error: {e}"
                    ))
            
            # Test rate limiter
            try:
                from src.core.rate_limiter import RateLimitManager
                rate_limiter = RateLimitManager()
                status = rate_limiter.get_rate_limit_status()
                
                self.results.append(ValidationResult(
                    'API Clients', 'Rate Limiter', True,
                    f"Rate limiter operational ({len(status)} APIs configured)"
                ))
            except Exception as e:
                self.results.append(ValidationResult(
                    'API Clients', 'Rate Limiter', False,
                    f"Rate limiter initialization failed: {e}"
                ))
        
        except ImportError as e:
            self.results.append(ValidationResult(
                'API Clients', 'Import', False,
                f"Failed to import API clients: {e}"
            ))
    
    def _validate_optional_features(self):
        """Validate optional features and their dependencies"""
        
        # PDF Export capability
        try:
            import reportlab
            self.results.append(ValidationResult(
                'Optional Features', 'PDF Export', True,
                "PDF export functionality available"
            ))
        except ImportError:
            self.results.append(ValidationResult(
                'Optional Features', 'PDF Export', True,  # Not critical
                "PDF export not available (reportlab not installed)"
            ))
        
        # Advanced Excel features
        try:
            import xlsxwriter
            self.results.append(ValidationResult(
                'Optional Features', 'Excel Export', True,
                "Advanced Excel export available"
            ))
        except ImportError:
            self.results.append(ValidationResult(
                'Optional Features', 'Excel Export', True,  # Not critical
                "Advanced Excel features not available"
            ))
        
        # Production server capability
        try:
            import gunicorn
            self.results.append(ValidationResult(
                'Optional Features', 'Production Server', True,
                "Gunicorn available for production deployment"
            ))
        except ImportError:
            self.results.append(ValidationResult(
                'Optional Features', 'Production Server', True,  # Not critical
                "Gunicorn not available (development server only)"
            ))
    
    def _validate_performance_requirements(self):
        """Validate system performance requirements"""
        
        # Check available memory
        try:
            import psutil
            
            # Get system memory
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            
            if available_gb >= 1.0:
                self.results.append(ValidationResult(
                    'Performance', 'Memory', True,
                    f"Sufficient memory available: {available_gb:.1f} GB"
                ))
            else:
                self.results.append(ValidationResult(
                    'Performance', 'Memory', False,
                    f"Low memory: {available_gb:.1f} GB (recommend 1GB+)"
                ))
            
            # Check disk space
            disk = psutil.disk_usage('.')
            available_gb = disk.free / (1024**3)
            
            if available_gb >= 1.0:
                self.results.append(ValidationResult(
                    'Performance', 'Disk Space', True,
                    f"Sufficient disk space: {available_gb:.1f} GB"
                ))
            else:
                self.results.append(ValidationResult(
                    'Performance', 'Disk Space', False,
                    f"Low disk space: {available_gb:.1f} GB"
                ))
        
        except ImportError:
            self.results.append(ValidationResult(
                'Performance', 'System Monitoring', True,  # Not critical
                "psutil not available (system monitoring disabled)"
            ))
        except Exception as e:
            self.results.append(ValidationResult(
                'Performance', 'System Check', True,  # Not critical
                f"Performance check failed: {e}"
            ))
    
    def _validate_security_settings(self):
        """Validate security-related settings"""
        
        # Check secret key security
        secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        if secret_key == 'dev-secret-key-change-in-production':
            self.results.append(ValidationResult(
                'Security', 'Secret Key', False,
                "Using default secret key (change for production)"
            ))
        elif len(secret_key) < 32:
            self.results.append(ValidationResult(
                'Security', 'Secret Key', False,
                "Secret key too short (recommend 32+ characters)"
            ))
        else:
            self.results.append(ValidationResult(
                'Security', 'Secret Key', True,
                "Secret key properly configured"
            ))
        
        # Check debug mode in production
        debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        is_production = os.getenv('RENDER') or os.getenv('HEROKU') or os.getenv('PRODUCTION')
        
        if debug_mode and is_production:
            self.results.append(ValidationResult(
                'Security', 'Debug Mode', False,
                "Debug mode enabled in production (security risk)"
            ))
        else:
            self.results.append(ValidationResult(
                'Security', 'Debug Mode', True,
                f"Debug mode: {'Enabled (development)' if debug_mode else 'Disabled'}"
            ))
    
    def _generate_validation_report(self) -> bool:
        """Generate and display validation report"""
        
        # Categorize results
        categories = {}
        critical_failures = 0
        warnings = 0
        total_checks = len(self.results)
        
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = {'passed': 0, 'failed': 0, 'results': []}
            
            categories[result.category]['results'].append(result)
            
            if result.passed:
                categories[result.category]['passed'] += 1
            else:
                categories[result.category]['failed'] += 1
                
                # Determine if this is critical
                if result.category in ['System', 'Dependencies', 'Project Structure', 'Database'] and 'Critical' in result.name:
                    critical_failures += 1
                else:
                    warnings += 1
        
        # Print report header
        print("\n" + "="*80)
        print("🎵 PRISM ANALYTICS ENGINE - STARTUP VALIDATION REPORT")
        print("="*80)
        
        # Print summary
        passed_checks = sum(1 for r in self.results if r.passed)
        print(f"\n📊 Summary: {passed_checks}/{total_checks} checks passed")
        print(f"❌ Critical Failures: {critical_failures}")
        print(f"⚠️  Warnings: {warnings}")
        
        # Print detailed results by category
        for category, data in categories.items():
            print(f"\n📁 {category}")
            print("-" * 40)
            
            for result in data['results']:
                icon = "✅" if result.passed else "❌"
                print(f"  {icon} {result.name}: {result.message}")
        
        # Print recommendations
        if critical_failures > 0 or warnings > 0:
            print(f"\n💡 Recommendations:")
            
            if critical_failures > 0:
                print(f"  🚨 Address {critical_failures} critical issue(s) before starting the application")
            
            if warnings > 0:
                print(f"  ⚠️  Review {warnings} warning(s) to ensure optimal functionality")
            
            # Specific recommendations
            failed_results = [r for r in self.results if not r.passed]
            
            if any('SECRET_KEY' in r.name for r in failed_results):
                print("     • Set a secure SECRET_KEY environment variable")
            
            if any('API' in r.category and not r.passed for r in failed_results):
                print("     • Configure API keys for full functionality")
            
            if any('Database' in r.category and not r.passed for r in failed_results):
                print("     • Ensure database is accessible and properly configured")
        
        print(f"\n🎵 Prism Analytics Engine validation completed at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print("="*80)
        
        # Return True if no critical failures
        return critical_failures == 0

def validate_startup_configuration() -> bool:
    """
    Main validation function called during startup
    Returns True if validation passes, False otherwise
    """
    validator = StartupValidator()
    return validator.validate_all()

def run_validation_only():
    """Run validation without starting the application"""
    print("🧪 Running standalone validation...")
    success = validate_startup_configuration()
    
    if success:
        print("\n✅ All critical validations passed!")
        print("   The application is ready to start.")
        return 0
    else:
        print("\n❌ Critical validations failed!")
        print("   Please address the issues above before starting the application.")
        return 1

def create_environment_template():
    """Create a template .env file with all required variables"""
    
    template_content = """# Prism Analytics Engine - Environment Configuration
# Copy this file to .env and configure your values

# Flask Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_DEBUG=false
HOST=0.0.0.0
PORT=5000

# Database Configuration
DATABASE_URL=sqlite:///data/precise_leads.db
# For PostgreSQL: postgresql://user:password@localhost/precise_leads

# Spotify API (Required for Spotify integration)
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# YouTube Data API (Optional but recommended)
YOUTUBE_API_KEY=your_youtube_api_key

# Last.fm API (Optional)
LASTFM_API_KEY=your_lastfm_api_key

# Contact Information
CONTACT_EMAIL=contact@precise.digital

# Performance Settings
MAX_BULK_ISRCS=1000
REQUEST_TIMEOUT=30

# CORS Settings (for production deployment)
CORS_ORIGINS=https://your-frontend-domain.com

# Production Settings
RENDER=false
HEROKU=false
PRODUCTION=false

# Logging
LOG_LEVEL=INFO

# Feature Flags
ENABLE_PDF_EXPORT=true
ENABLE_YOUTUBE_INTEGRATION=true
ENABLE_ADVANCED_ANALYTICS=true
"""
    
    env_file = Path('.env.example')
    with open(env_file, 'w') as f:
        f.write(template_content)
    
    print(f"✅ Environment template created: {env_file}")
    print("   Copy this to .env and configure your values")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Prism Analytics Engine - Startup Validation')
    parser.add_argument('--create-env', action='store_true', help='Create environment template file')
    parser.add_argument('--validate-only', action='store_true', help='Run validation without starting app')
    
    args = parser.parse_args()
    
    if args.create_env:
        create_environment_template()
    elif args.validate_only:
        sys.exit(run_validation_only())
    else:
        # Run full validation (this is called by run.py)
        success = validate_startup_configuration()
        sys.exit(0 if success else 1)