import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def validate_startup_configuration():
    """
    Enhanced startup validation with YouTube integration checks
    """
    print("🔍 Validating startup configuration...")
    
    success = True
    
    # 1. Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        success = False
    else:
        print(f"✅ Python version: {sys.version}")
    
    # 2. Check required directories
    required_dirs = ['data', 'logs']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            try:
                os.makedirs(dir_name, exist_ok=True)
                print(f"✅ Created directory: {dir_name}")
            except Exception as e:
                print(f"❌ Failed to create directory {dir_name}: {e}")
                success = False
        else:
            print(f"✅ Directory exists: {dir_name}")
    
    # 3. Check environment variables (basic check)
    if not os.getenv('SPOTIFY_CLIENT_ID') or not os.getenv('SPOTIFY_CLIENT_SECRET'):
        print("⚠️  Warning: Spotify API credentials not configured")
        print("   Some features may not work without these keys.")
    else:
        print("✅ Spotify API credentials configured")
    
    # 4. NEW: Check YouTube API configuration
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    if not youtube_api_key:
        print("⚠️  Warning: YouTube API key not configured")
        print("   YouTube integration will be disabled.")
        print("   Set YOUTUBE_API_KEY environment variable to enable YouTube features.")
    else:
        print(f"✅ YouTube API key configured (...{youtube_api_key[-4:]})")
    
    # 5. Check optional API keys
    lastfm_key = os.getenv('LASTFM_API_KEY')
    if lastfm_key:
        print(f"✅ Last.fm API key configured (...{lastfm_key[-4:]})")
    else:
        print("⚠️  Optional: Last.fm API key not configured")
    
    if success:
        print("✅ Basic startup validations passed!")
    else:
        print("❌ Some startup validations failed!")
    
    return success

def check_database_schema():
    """
    Check if database schema is up to date, including YouTube fields
    """
    print("🔍 Checking database schema...")
    
    try:
        from config.database import check_youtube_migration_needed, migrate_youtube_fields
        
        if check_youtube_migration_needed():
            print("🎥 YouTube fields not found in database")
            print("🔄 Running YouTube schema migration...")
            try:
                migrate_youtube_fields()
                print("✅ YouTube schema migration completed!")
            except Exception as e:
                print(f"❌ YouTube migration failed: {e}")
                return False
        else:
            print("✅ Database schema is up to date (including YouTube fields)")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Could not check database schema: {e}")
        print("Database will be initialized on first run")
        return True

def test_api_integrations():
    """
    Test API integrations to ensure they're working properly
    """
    print("🔍 Testing API integrations...")
    
    # Test imports first
    try:
        from src.integrations.base_client import musicbrainz_client, spotify_client, lastfm_client, youtube_client
        print("✅ All API clients imported successfully")
    except Exception as e:
        print(f"❌ Failed to import API clients: {e}")
        return False
    
    # Test YouTube client specifically
    try:
        from config.settings import settings
        if settings.apis['youtube'].api_key:
            print("✅ YouTube client initialized with API key")
        else:
            print("⚠️  YouTube client initialized without API key (features disabled)")
    except Exception as e:
        print(f"⚠️  YouTube client initialization warning: {e}")
    
    return True

def print_startup_banner():
    """
    Print startup banner with YouTube integration status
    """
    print("\n" + "🎵" * 60)
    print("🎵  PRECISE DIGITAL LEAD GENERATION TOOL")
    print("🎵  with YouTube Integration")
    print("🎵" + " " * 58 + "🎵")
    
    # Show integration status
    integrations = []
    
    # Check each integration
    try:
        from config.settings import settings
        
        if os.getenv('SPOTIFY_CLIENT_ID'):
            integrations.append("✅ Spotify")
        else:
            integrations.append("❌ Spotify")
            
        if settings.apis['youtube'].api_key:
            integrations.append("✅ YouTube")
        else:
            integrations.append("⚠️  YouTube (disabled)")
            
        if settings.apis['lastfm'].api_key:
            integrations.append("✅ Last.fm")
        else:
            integrations.append("⚠️  Last.fm (optional)")
        
        integrations.append("✅ MusicBrainz")
        
        print("🎵  Integrations:")
        for integration in integrations:
            print(f"🎵    {integration}")
            
    except Exception as e:
        print(f"🎵  Integration status check failed: {e}")
    
    print("🎵" + " " * 58 + "🎵")
    print("🎵" * 60)
    print()

def main():
    """Main function to start the application with YouTube integration"""
    
    # Print banner first
    print_startup_banner()
    
    # Validate configuration
    try:
        if not validate_startup_configuration():
            print("❌ Application startup failed due to configuration errors")
            print("Please fix the configuration issues and try again.")
            sys.exit(1)
    except Exception as e:
        print(f"⚠️  Warning: Startup validation failed: {e}")
        print("Continuing anyway...")
    
    # Check database schema
    try:
        if not check_database_schema():
            print("❌ Database schema check failed")
            print("Please check your database configuration.")
            sys.exit(1)
    except Exception as e:
        print(f"⚠️  Database schema check warning: {e}")
    
    # Initialize database if it doesn't exist
    if not os.path.exists('data/leads.db'):
        print("📊 Initializing database...")
        os.makedirs('data', exist_ok=True)
        try:
            from config.database import init_db
            init_db()
            print("✅ Database initialized successfully!")
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            sys.exit(1)
    
    # Test API integrations
    try:
        if not test_api_integrations():
            print("⚠️  Some API integrations may not work properly")
    except Exception as e:
        print(f"⚠️  API integration test warning: {e}")
    
    # Import and start Flask app
    try:
        from src.api.routes import app
        
        print(f"🚀 Starting server at http://localhost:5000")
        print("📊 API Documentation available at /api/")
        print("🔍 Health check: http://localhost:5000/api/health")
        print("🎥 YouTube test: http://localhost:5000/api/youtube/test")
        print("\n🎯 Key Features:")
        print("  • ISRC analysis with YouTube integration")
        print("  • Lead scoring with YouTube opportunity assessment")
        print("  • Contact discovery including YouTube channels")
        print("  • Bulk processing with YouTube data collection")
        print("  • Export capabilities with YouTube metrics")
        print("\n💡 CLI Tools Available:")
        print("  python cli.py test-youtube 'Artist Name'")
        print("  python cli.py youtube-status")
        print("  python cli.py youtube-opportunities")
        print("  python cli.py analyze ISRC --include-youtube")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 70)
        
        # Start the Flask app
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except ImportError as e:
        print(f"❌ Failed to import Flask app: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

def run_cli():
    """Alternative entry point for CLI operations"""
    try:
        from cli import cli
        cli()
    except ImportError as e:
        print(f"❌ Failed to import CLI: {e}")
        sys.exit(1)

if __name__ == '__main__':
    # Check if running in CLI mode
    if len(sys.argv) > 1 and sys.argv[1] in ['cli', 'test', 'migrate']:
        run_cli()
    else:
        main()