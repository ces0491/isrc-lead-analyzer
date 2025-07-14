#!/usr/bin/env python3
"""
WSGI entry point for Gunicorn production deployment
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set production environment variables
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_DEBUG', 'false')

def create_app():
    """Create and configure the Flask application for production"""
    
    print("🚀 Starting Precise Digital API in PRODUCTION mode")
    
    try:
        # Initialize database first
        from config.database import init_db
        print("🔄 Initializing database...")
        init_db()
        print("✅ Database initialized")
        
        # Import the Flask app
        from src.api.routes import app
        
        # Configure for production
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        
        print("✅ Flask app configured for production")
        print(f"🎯 API available at: /api/")
        
        return app
        
    except Exception as e:
        print(f"❌ Failed to create app: {e}")
        import traceback
        traceback.print_exc()
        raise

# Create the application instance for Gunicorn
app = create_app()

if __name__ == "__main__":
    # This should never run in production with Gunicorn
    print("⚠️  Warning: Running in fallback mode. Use Gunicorn for production!")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)