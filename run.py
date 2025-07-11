import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main function to start the application"""
    print("🎵 Precise Digital Lead Generation Tool")
    print("=" * 50)
    
    # Validate configuration first
    try:
        from src.utils.startup_validation import validate_startup_configuration
        if not validate_startup_configuration():
            print("❌ Application startup failed due to configuration errors")
            sys.exit(1)
    except ImportError as e:
        print(f"⚠️  Warning: Could not import startup validation: {e}")
        print("Continuing without validation...")
    
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