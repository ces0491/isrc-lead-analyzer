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

def create_app():
    """Create and configure the Flask application for production"""
    
    # Set production environment
    os.environ.setdefault('FLASK_ENV', 'production')
    os.environ.setdefault('FLASK_DEBUG', 'false')
    
    try:
        # Initialize database first
        from config.database import init_db
        print("🔄 Initializing database...")
        init_db()
        print("✅ Database initialized")
        
        # Import the Flask app
        from src.api.routes import app
        
        print("✅ Flask app loaded successfully")
        return app
        
    except Exception as e:
        print(f"❌ Failed to create app: {e}")
        import traceback
        traceback.print_exc()
        raise

# Create the application instance
app = create_app()

if __name__ == "__main__":
    # This won't be used in production but useful for testing
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))