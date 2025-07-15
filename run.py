#!/usr/bin/env python3
"""
Precise Digital Lead Generation Tool - Main Entry Point
Prism Analytics Engine by Precise Digital

This is the main entry point for the ISRC-based lead generation system.
Includes comprehensive startup validation and graceful error handling.
"""

import os
import sys
import logging
import signal
import traceback
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """Setup logging configuration"""
    try:
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Import logging config
        from config.settings import LOGGING_CONFIG
        import logging.config
        
        logging.config.dictConfig(LOGGING_CONFIG)
        logger = logging.getLogger('precise_digital')
        logger.info("🎵 Prism Analytics Engine - Logging initialized")
        return logger
        
    except Exception as e:
        # Fallback to basic logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        )
        logger = logging.getLogger('precise_digital')
        logger.warning(f"Failed to setup advanced logging: {e}")
        return logger

def validate_environment():
    """Validate environment and configuration"""
    print("🔍 Validating environment...")
    
    try:
        # Test critical imports
        from config.settings import settings
        from config.database import init_db
        from src.utils.startup_validation import validate_startup_configuration
        
        # Run startup validation
        validation_passed = validate_startup_configuration()
        
        if not validation_passed:
            print("⚠️  Some validation checks failed, but application can still run")
            print("   Check the validation output above for details")
        
        # Validate configuration
        config_status = settings.validate_configuration()
        
        print("\n📊 Configuration Status:")
        print(f"  Database: {'✅ Connected' if config_status['database']['accessible'] else '❌ Not accessible'}")
        
        for api_name, api_status in config_status['apis'].items():
            icon = "✅" if api_status['configured'] else "⚠️ "
            print(f"  {api_name.title()}: {icon}{'Configured' if api_status['configured'] else 'Not configured'}")
        
        # Create required directories
        for directory in ['data', 'logs', 'exports']:
            os.makedirs(directory, exist_ok=True)
        
        return True
        
    except Exception as e:
        print(f"❌ Environment validation failed: {e}")
        traceback.print_exc()
        return False

def initialize_database():
    """Initialize database with proper error handling"""
    print("\n🗄️  Initializing database...")
    
    try:
        from config.database import init_db
        db_manager = init_db()
        print("✅ Database initialized successfully")
        return db_manager
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("   Make sure you have write permissions in the data directory")
        traceback.print_exc()
        return None

def setup_signal_handlers(app=None):
    """Setup graceful shutdown signal handlers"""
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        
        # Cleanup database connections if needed
        try:
            from config.database import DatabaseManager
            # Any cleanup code can go here
        except:
            pass
        
        print("👋 Prism Analytics Engine shutdown complete")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def create_app():
    """Create and configure Flask application"""
    try:
        from src.api.routes import app
        from config.settings import settings
        
        # Additional app configuration
        app.config.update({
            'SECRET_KEY': settings.app.secret_key,
            'DEBUG': settings.app.debug,
            'TESTING': False,
            'JSON_SORT_KEYS': False
        })
        
        print("✅ Flask application configured")
        return app
        
    except Exception as e:
        print(f"❌ Failed to create Flask app: {e}")
        traceback.print_exc()
        return None

def print_startup_banner():
    """Print startup banner with Prism branding"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    ██████╗ ██████╗ ██╗███████╗███╗   ███╗                   ║
║    ██╔══██╗██╔══██╗██║██╔════╝████╗ ████║                   ║
║    ██████╔╝██████╔╝██║███████╗██╔████╔██║                   ║
║    ██╔═══╝ ██╔══██╗██║╚════██║██║╚██╔╝██║                   ║
║    ██║     ██║  ██║██║███████║██║ ╚═╝ ██║                   ║
║    ╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝     ╚═╝                   ║
║                                                              ║
║              Analytics Engine by Precise Digital            ║
║         Transforming Music Data into Actionable Insights    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def print_api_status():
    """Print API integration status"""
    try:
        from src.integrations.base_client import check_client_availability
        from config.settings import settings
        
        availability = check_client_availability()
        
        print("\n🔌 API Integration Status:")
        integrations = {
            'MusicBrainz': {
                'available': availability['musicbrainz'],
                'description': 'Music metadata (always available)',
                'priority': 'Essential'
            },
            'Spotify': {
                'available': availability['spotify'],
                'description': f"Streaming data ({'Configured' if settings.spotify_client_id else 'Needs API keys'})",
                'priority': 'High'
            },
            'YouTube': {
                'available': availability['youtube'],
                'description': f"Video analytics ({'Configured' if settings.apis['youtube'].api_key else 'Needs API key'})",
                'priority': 'Medium'
            },
            'Last.fm': {
                'available': availability['lastfm'],
                'description': f"Social listening ({'Configured' if settings.apis['lastfm'].api_key else 'Optional'})",
                'priority': 'Low'
            }
        }
        
        for name, info in integrations.items():
            status = "✅ Active" if info['available'] else "❌ Inactive"
            print(f"  {name:12} {status:12} - {info['description']}")
        
        # Show configuration instructions for missing APIs
        missing_apis = [name for name, info in integrations.items() if not info['available'] and info['priority'] != 'Low']
        if missing_apis:
            print(f"\n⚠️  Configure missing APIs for full functionality:")
            if not settings.spotify_client_id:
                print(f"   Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables")
            if not settings.apis['youtube'].api_key:
                print(f"   Set YOUTUBE_API_KEY environment variable")
    
    except Exception as e:
        print(f"Error checking API status: {e}")

def print_startup_info():
    """Print startup information"""
    from config.settings import settings
    
    print(f"\n🚀 Starting Prism Analytics Engine...")
    print(f"   Environment: {'Development' if settings.app.debug else 'Production'}")
    print(f"   Host: {settings.app.host}")
    print(f"   Port: {settings.app.port}")
    print(f"   Database: {settings.database.url}")
    
    if settings.app.debug:
        print(f"   Debug Mode: Enabled")
        print(f"   Auto-reload: Enabled")
    
    print(f"\n📋 Available Endpoints:")
    print(f"   Health Check: http://{settings.app.host}:{settings.app.port}/api/health")
    print(f"   API Status:   http://{settings.app.host}:{settings.app.port}/api/status")
    print(f"   ISRC Analyze: http://{settings.app.host}:{settings.app.port}/api/analyze-isrc")
    print(f"   Leads:        http://{settings.app.host}:{settings.app.port}/api/leads")

def run_development_server():
    """Run the development server"""
    from config.settings import settings
    
    try:
        app = create_app()
        if not app:
            return False
        
        print(f"\n🎵 Prism Analytics Engine is running!")
        print(f"   Access the API at: http://{settings.app.host}:{settings.app.port}")
        print(f"   Press Ctrl+C to stop the server")
        
        # Setup signal handlers
        setup_signal_handlers(app)
        
        # Run the Flask development server
        app.run(
            host=settings.app.host,
            port=settings.app.port,
            debug=settings.app.debug,
            use_reloader=settings.app.debug,
            threaded=True
        )
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to start development server: {e}")
        traceback.print_exc()
        return False

def run_production_server():
    """Run the production server (using Gunicorn if available)"""
    from config.settings import settings
    
    try:
        # Try to use Gunicorn for production
        import gunicorn.app.wsgiapp as wsgi
        
        app = create_app()
        if not app:
            return False
        
        print(f"\n🎵 Starting Prism Analytics Engine (Production Mode)")
        
        # Gunicorn configuration
        sys.argv = [
            'gunicorn',
            '--bind', f'{settings.app.host}:{settings.app.port}',
            '--workers', '4',
            '--worker-class', 'sync',
            '--timeout', '120',
            '--keep-alive', '2',
            '--max-requests', '1000',
            '--max-requests-jitter', '100',
            '--preload',
            'src.api.routes:app'
        ]
        
        wsgi.run()
        return True
        
    except ImportError:
        print("⚠️  Gunicorn not available, falling back to development server")
        return run_development_server()
    except Exception as e:
        print(f"❌ Failed to start production server: {e}")
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    try:
        # Print startup banner
        print_startup_banner()
        
        # Setup logging
        logger = setup_logging()
        logger.info("Starting Precise Digital Lead Generation Tool")
        
        # Validate environment
        if not validate_environment():
            print("❌ Environment validation failed. Exiting.")
            return 1
        
        # Initialize database
        if not initialize_database():
            print("❌ Database initialization failed. Exiting.")
            return 1
        
        # Print API status
        print_api_status()
        
        # Print startup info
        print_startup_info()
        
        # Determine if we're in production or development
        from config.settings import settings
        
        if settings.app.debug:
            success = run_development_server()
        else:
            success = run_production_server()
        
        if not success:
            logger.error("Failed to start server")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 Prism Analytics Engine shutdown by user")
        return 0
    except Exception as e:
        print(f"\n❌ Startup failed: {e}")
        traceback.print_exc()
        return 1

def test_mode():
    """Run in test mode for debugging"""
    print("🧪 Running Prism Analytics Engine in Test Mode\n")
    
    # Test imports
    try:
        from src.core.pipeline import LeadAggregationPipeline
        from src.core.rate_limiter import RateLimitManager
        from src.utils.validators import validate_isrc
        
        print("✅ Core imports successful")
        
        # Test ISRC validation
        test_isrc = "USRC17607839"
        is_valid, result = validate_isrc(test_isrc)
        print(f"✅ ISRC validation test: {test_isrc} -> {'Valid' if is_valid else 'Invalid'}")
        
        # Test rate limiter
        rate_limiter = RateLimitManager()
        status = rate_limiter.get_rate_limit_status()
        print(f"✅ Rate limiter test: {len(status)} APIs configured")
        
        # Test database
        from config.database import init_db
        db_manager = init_db()
        print("✅ Database test successful")
        
        # Test pipeline initialization
        pipeline = LeadAggregationPipeline(rate_limiter)
        print("✅ Pipeline test successful")
        
        print("\n🎉 All tests passed! The application is ready to run.")
        print("   To start the server: python run.py")
        
        return 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['test', '--test', '-t']:
            sys.exit(test_mode())
        elif sys.argv[1] in ['help', '--help', '-h']:
            print("Prism Analytics Engine - Precise Digital Lead Generation Tool")
            print()
            print("Usage:")
            print("  python run.py          Start the application")
            print("  python run.py test     Run in test mode")
            print("  python run.py help     Show this help message")
            print()
            print("Environment Variables:")
            print("  SPOTIFY_CLIENT_ID      Spotify API client ID")
            print("  SPOTIFY_CLIENT_SECRET  Spotify API client secret")
            print("  YOUTUBE_API_KEY        YouTube Data API key")
            print("  LASTFM_API_KEY         Last.fm API key (optional)")
            print("  DATABASE_URL           Database connection URL")
            print("  FLASK_DEBUG            Enable debug mode (true/false)")
            print("  PORT                   Server port (default: 5000)")
            print()
            sys.exit(0)
    
    # Run the main application
    sys.exit(main())