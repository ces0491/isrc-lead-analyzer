import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def validate_startup_configuration():
    """
    Simple startup validation without external dependencies
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
    
    if success:
        print("✅ Basic startup validations passed!")
    else:
        print("❌ Some startup validations failed!")
    
    return success

def main():
    """Main function to start the application"""
    print("🎵 Precise Digital Lead Generation Tool")
    print("=" * 50)
    
    # Validate configuration first (using local function)
    try:
        if not validate_startup_configuration():
            print("❌ Application startup failed due to configuration errors")
            sys.exit(1)
    except Exception as e:
        print(f"⚠️  Warning: Startup validation failed: {e}")
        print("Continuing anyway...")
    
    # Initialize database if it doesn't exist
    if not os.path.exists('data/leads.db'):
        print("Initializing database...")
        os.makedirs('data', exist_ok=True)
        try:
            from config.database import init_db
            init_db()
            print("✅ Database initialized successfully!")
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            sys.exit(1)
    
    # Import and start Flask app
    try:
        from src.api.routes import app
        
        print(f"🚀 Starting server at http://localhost:5000")
        print("📊 API Documentation available at /api/")
        print("🔍 Health check: http://localhost:5000/api/health")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 50)
        
        # Start the Flask app
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except ImportError as e:
        print(f"❌ Failed to import Flask app: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()