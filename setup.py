#!/usr/bin/env python3
"""
Setup script for Precise Digital Lead Generation Tool
Run this to set up the environment completely
"""

import os
import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """Install all required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def initialize_database():
    """Initialize the database with proper order"""
    print("📊 Initializing database...")
    
    try:
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Import after dependencies are installed
        from config.database import init_db, check_youtube_migration_needed, migrate_youtube_fields
        
        # Initialize basic database
        init_db()
        print("✅ Basic database schema created!")
        
        # Add YouTube fields if needed
        if check_youtube_migration_needed():
            migrate_youtube_fields()
            print("✅ YouTube schema migration completed!")
        else:
            print("✅ YouTube schema already up to date!")
            
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def validate_api_keys():
    """Check if API keys are configured"""
    print("🔐 Checking API configuration...")
    
    missing_keys = []
    
    if not os.getenv('SPOTIFY_CLIENT_ID'):
        missing_keys.append('SPOTIFY_CLIENT_ID')
    if not os.getenv('SPOTIFY_CLIENT_SECRET'):
        missing_keys.append('SPOTIFY_CLIENT_SECRET')
    
    if missing_keys:
        print("⚠️  Missing required API keys:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\nPlease add these to your .env file")
        return False
    
    print("✅ Required API keys configured!")
    
    optional_keys = []
    if not os.getenv('YOUTUBE_API_KEY'):
        optional_keys.append('YOUTUBE_API_KEY')
    if not os.getenv('LASTFM_API_KEY'):
        optional_keys.append('LASTFM_API_KEY')
    
    if optional_keys:
        print("📝 Optional API keys not configured:")
        for key in optional_keys:
            print(f"   - {key} (features will be limited)")
    
    return True

def test_setup():
    """Test that everything is working"""
    print("🧪 Testing setup...")
    
    try:
        # Test imports
        from src.integrations.base_client import check_client_availability
        from src.utils.validators import validate_isrc
        from config.database import DatabaseManager
        
        # Test ISRC validation
        is_valid, result = validate_isrc("USRC17607839")
        if not is_valid:
            print(f"❌ ISRC validation test failed: {result}")
            return False
        print("✅ ISRC validation working!")
        
        # Test database connection
        db_manager = DatabaseManager()
        with db_manager:
            pass
        print("✅ Database connection working!")
        
        # Test API client availability
        client_status = check_client_availability()
        working_clients = sum(1 for available in client_status.values() if available)
        print(f"✅ {working_clients}/4 API clients available!")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Precise Digital Lead Generation Tool")
    print("=" * 60)
    
    # Step 1: Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        return 1
    
    # Step 2: Initialize database
    if not initialize_database():
        print("❌ Setup failed at database initialization")
        return 1
    
    # Step 3: Validate API keys
    if not validate_api_keys():
        print("⚠️  Setup completed with warnings - check API keys")
    
    # Step 4: Test everything
    if not test_setup():
        print("❌ Setup validation failed")
        return 1
    
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("\nTo start the application:")
    print("  python run.py")
    print("\nTo test with CLI:")
    print("  python cli.py status")
    print("  python cli.py analyze USRC17607839 --no-save")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())