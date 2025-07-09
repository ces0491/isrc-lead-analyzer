# run.py - Main application entry point
"""
Main entry point for Precise Digital Lead Generation Tool
Run this file to start the Flask development server
"""
import os
import sys
from flask import Flask

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api.routes import app
from config.database import init_db

def main():
    """Main function to start the application"""
    print("🎵 Precise Digital Lead Generation Tool")
    print("=" * 50)
    
    # Initialize database if it doesn't exist
    if not os.path.exists('data/leads.db'):
        print("Initializing database...")
        os.makedirs('data', exist_ok=True)
        init_db()
        print("✅ Database initialized successfully!")
    
    print(f"🚀 Starting server at http://localhost:5000")
    print("📊 API Documentation available at /api/")
    print("🔍 Health check: http://localhost:5000/api/health")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()