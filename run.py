import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def is_production():
    """Check if running in production environment"""
    return bool(
        os.getenv('RENDER') or 
        os.getenv('FLASK_ENV') == 'production' or
        os.getenv('GUNICORN_CMD_ARGS')  # Gunicorn sets this
    )

def validate_production_config():
    """Validate production configuration"""
    if not is_production():
        return True
        
    required_vars = ['DATABASE_URL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Production configuration validated")
    return True

def validate_startup_configuration():
    """Enhanced startup validation with production checks"""
    print("🔍 Validating startup configuration...")
    
    success = True
    
    # 1. Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        success = False
    else:
        print(f"✅ Python version: {sys.version}")
    
    # 2. Validate production config if needed
    if is_production():
        if not validate_production_config():
            success = False
    
    # 3. Check required directories (only for development)
    if not is_production():
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
    
    # 4. Check API credentials
    if not os.getenv('SPOTIFY_CLIENT_ID') or not os.getenv('SPOTIFY_CLIENT_SECRET'):
        print("⚠️  Warning: Spotify API credentials not configured")
        print("   Some features may not work without these keys.")
    else:
        print("✅ Spotify API credentials configured")
    
    # 5. Check YouTube API configuration
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    if not youtube_api_key:
        print("⚠️  Warning: YouTube API key not configured")
        print("   YouTube integration will be disabled.")
    else:
        print(f"✅ YouTube API key configured (...{youtube_api_key[-4:]})")
    
    return success

def initialize_database():
    """Initialize database with proper error handling"""
    print("🔄 Initializing database...")
    
    try:
        from config.database import init_db
        
        # Initialize database tables
        init_db()
        print("✅ Database tables initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        if is_production():
            # In production, log error but don't exit immediately
            print("⚠️  Continuing in production mode - database may need manual setup")
            return False
        else:
            # In development, exit on database errors
            return False

def print_startup_banner():
    """Print startup banner with environment info"""
    env = "PRODUCTION" if is_production() else "DEVELOPMENT"
    
    print("\n" + "🎵" * 60)
    print("🎵  PRISM ANALYTICS ENGINE")
    print(f"🎵  Environment: {env}")
    print("🎵  by Precise Digital")
    print("🎵" + " " * 58 + "🎵")
    
    # Show integration status
    integrations = []
    
    if os.getenv('SPOTIFY_CLIENT_ID'):
        integrations.append("✅ Spotify")
    else:
        integrations.append("❌ Spotify")
        
    if os.getenv('YOUTUBE_API_KEY'):
        integrations.append("✅ YouTube")
    else:
        integrations.append("⚠️  YouTube (disabled)")
        
    if os.getenv('LASTFM_API_KEY'):
        integrations.append("✅ Last.fm")
    else:
        integrations.append("⚠️  Last.fm (optional)")
    
    integrations.append("✅ MusicBrainz")
    
    print("🎵  API Integrations:")
    for integration in integrations:
        print(f"🎵    {integration}")
        
    print("🎵" + " " * 58 + "🎵")
    print("🎵" * 60)
    print()

def main():
    """Main function to start the application"""
    
    # Print banner first
    print_startup_banner()
    
    # Check if this is being run in production
    if is_production():
        print("🚨 PRODUCTION ENVIRONMENT DETECTED")
        print("❌ Do not run this script directly in production!")
        print("🔧 Use Gunicorn instead:")
        print("   gunicorn --bind 0.0.0.0:$PORT --workers 4 wsgi:app")
        print("\n💡 If you see this message on Render, check your render.yaml startCommand")
        sys.exit(1)
    
    # Validate configuration
    try:
        if not validate_startup_configuration():
            print("❌ Application startup failed due to configuration errors")
            sys.exit(1)
    except Exception as e:
        print(f"⚠️  Warning: Startup validation failed: {e}")
    
    # Initialize database
    try:
        db_success = initialize_database()
        if not db_success:
            print("❌ Database setup required for development")
            sys.exit(1)
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
    
    # Import and start Flask app (DEVELOPMENT ONLY)
    try:
        from src.api.routes import app
        
        # Get port and host
        port = int(os.getenv('PORT', 5000))
        host = '0.0.0.0'
        
        print(f"🛠️  Starting DEVELOPMENT server on {host}:{port}")
        print("📊 API Documentation: http://localhost:5000/api/")
        print("🔍 Health check: http://localhost:5000/api/health")
        print("🎥 YouTube test: http://localhost:5000/api/youtube/test")
        print("\n💡 CLI Tools Available:")
        print("  python cli.py test-youtube 'Artist Name'")
        print("  python cli.py analyze ISRC --include-youtube")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 70)
        
        # Run in development mode only
        app.run(
            host=host,
            port=port,
            debug=True,
            threaded=True
        )
            
    except ImportError as e:
        print(f"❌ Failed to import Flask app: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()