#!/usr/bin/env python3
"""
Comprehensive test script to verify all critical fixes are working
Run this script to validate the application setup
"""

import sys
import os
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all critical imports work"""
    print("🔍 Testing imports...")
    
    try:
        # Test core imports
        from src.core.pipeline import LeadAggregationPipeline
        from src.core.rate_limiter import RateLimitManager
        from src.core.scoring import LeadScoringEngine
        print("  ✅ Core modules imported successfully")
        
        # Test API integrations
        from src.integrations.base_client import musicbrainz_client, spotify_client, lastfm_client
        print("  ✅ API clients imported successfully")
        
        # Test database
        from config.database import DatabaseManager, Artist, Track, init_db
        print("  ✅ Database modules imported successfully")
        
        # Test validators
        from src.utils.validators import validate_isrc
        print("  ✅ Validator imported successfully")
        
        # Test startup validation
        from src.utils.startup_validation import validate_startup_configuration
        print("  ✅ Startup validation imported successfully")
        
        # Test Flask app
        from src.api.routes import app
        print("  ✅ Flask app imported successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_isrc_validation():
    """Test ISRC validation functionality"""
    print("\n🔍 Testing ISRC validation...")
    
    try:
        from src.utils.validators import validate_isrc
        
        # Test valid ISRCs
        valid_isrcs = [
            "USRC17607839",
            "GBUM71505078",
            "USRC1760783A",
            "us-rc-17-607839",  # Should be cleaned
            "  USRC17607839  ",  # Should be trimmed
        ]
        
        for isrc in valid_isrcs:
            is_valid, result = validate_isrc(isrc)
            if is_valid:
                print(f"  ✅ '{isrc}' -> '{result}'")
            else:
                print(f"  ❌ '{isrc}' should be valid but got: {result}")
                return False
        
        # Test invalid ISRCs
        invalid_isrcs = [
            "INVALID",
            "USRC1760783",  # Too short
            "USRC17607839X",  # Too long
            "12RC17607839",  # Invalid country code
            "",  # Empty
            None,  # None
        ]
        
        for isrc in invalid_isrcs:
            is_valid, result = validate_isrc(isrc)
            if not is_valid:
                print(f"  ✅ '{isrc}' correctly rejected: {result}")
            else:
                print(f"  ❌ '{isrc}' should be invalid but was accepted")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ ISRC validation error: {e}")
        traceback.print_exc()
        return False

def test_rate_limiter():
    """Test rate limiter functionality"""
    print("\n🔍 Testing rate limiter...")
    
    try:
        from src.core.rate_limiter import RateLimitManager
        
        rate_limiter = RateLimitManager()
        
        # Test status retrieval
        status = rate_limiter.get_rate_limit_status()
        print(f"  ✅ Rate limit status retrieved: {len(status)} APIs configured")
        
        # Test that all expected APIs are present
        expected_apis = ['musicbrainz', 'spotify', 'lastfm', 'youtube']
        for api in expected_apis:
            if api in status:
                print(f"  ✅ {api} API configured")
            else:
                print(f"  ❌ {api} API not found in status")
                return False
        
        # Test time estimation
        estimated_time = rate_limiter.estimate_batch_time('musicbrainz', 10)
        print(f"  ✅ Batch time estimation works: {estimated_time:.2f}s for 10 requests")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Rate limiter error: {e}")
        traceback.print_exc()
        return False

def test_database():
    """Test database functionality"""
    print("\n🔍 Testing database...")
    
    try:
        from config.database import DatabaseManager, init_db, Artist
        
        # Test database initialization
        if not os.path.exists('data'):
            os.makedirs('data')
        
        # Initialize database
        init_db()
        print("  ✅ Database initialized successfully")
        
        # Test database manager
        db_manager = DatabaseManager()
        
        # Test context manager
        with db_manager as db:
            # Test basic query
            count = db.session.query(Artist).count()
            print(f"  ✅ Database query successful: {count} artists")
        
        print("  ✅ Context manager worked successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        traceback.print_exc()
        return False

def test_scoring_engine():
    """Test scoring engine functionality"""
    print("\n🔍 Testing scoring engine...")
    
    try:
        from src.core.scoring import LeadScoringEngine
        
        scoring_engine = LeadScoringEngine()
        
        # Test with sample data
        sample_data = {
            'track_data': {
                'label': 'Self-Released',
                'platforms_available': ['spotify', 'apple_music']
            },
            'spotify_data': {
                'followers': 25000,
                'popularity': 45
            },
            'musicbrainz_data': {
                'artist': {'country': 'NZ'}
            },
            'lastfm_data': {
                'artist': {'listeners': 5000}
            }
        }
        
        scores = scoring_engine.calculate_scores(sample_data)
        
        # Validate score structure
        required_keys = ['independence_score', 'opportunity_score', 'geographic_score', 'total_score', 'tier', 'confidence']
        for key in required_keys:
            if key not in scores:
                print(f"  ❌ Missing score key: {key}")
                return False
        
        print(f"  ✅ Scoring successful: {scores['total_score']} (Tier {scores['tier']})")
        print(f"  ✅ Score breakdown: I:{scores['independence_score']}, O:{scores['opportunity_score']}, G:{scores['geographic_score']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Scoring engine error: {e}")
        traceback.print_exc()
        return False

def test_pipeline():
    """Test main pipeline functionality"""
    print("\n🔍 Testing pipeline...")
    
    try:
        from src.core.pipeline import LeadAggregationPipeline
        from src.core.rate_limiter import RateLimitManager
        
        rate_limiter = RateLimitManager()
        pipeline = LeadAggregationPipeline(rate_limiter)
        
        # Test pipeline initialization
        print("  ✅ Pipeline initialized successfully")
        
        # Test stats
        stats = pipeline.get_processing_stats()
        print(f"  ✅ Pipeline stats: {stats}")
        
        # Test with invalid ISRC (should fail gracefully)
        result = pipeline.process_isrc("INVALID", save_to_db=False)
        if result['status'] == 'failed' and 'ISRC' in str(result['errors']):
            print("  ✅ Pipeline correctly rejects invalid ISRC")
        else:
            print("  ❌ Pipeline should reject invalid ISRC")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Pipeline error: {e}")
        traceback.print_exc()
        return False

def test_flask_app():
    """Test Flask app functionality"""
    print("\n🔍 Testing Flask app...")
    
    try:
        from src.api.routes import app
        
        # Test that app is configured
        print(f"  ✅ Flask app created: {app.name}")
        
        # Test with test client
        with app.test_client() as client:
            # Test health check
            response = client.get('/api/health')
            if response.status_code == 200:
                print("  ✅ Health check endpoint works")
            else:
                print(f"  ❌ Health check failed: {response.status_code}")
                return False
            
            # Test status endpoint
            response = client.get('/api/status')
            if response.status_code == 200:
                print("  ✅ Status endpoint works")
            else:
                print(f"  ❌ Status endpoint failed: {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Flask app error: {e}")
        traceback.print_exc()
        return False

def test_startup_validation():
    """Test startup validation functionality"""
    print("\n🔍 Testing startup validation...")
    
    try:
        from src.utils.startup_validation import validate_startup_configuration
        
        # Run validation (may fail due to missing API keys, but shouldn't crash)
        result = validate_startup_configuration()
        print(f"  ✅ Startup validation completed: {'✅ PASSED' if result else '⚠️ FAILED (expected if API keys missing)'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Startup validation error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 Running comprehensive test suite for critical fixes...")
    print("=" * 70)
    
    tests = [
        ("Imports", test_imports),
        ("ISRC Validation", test_isrc_validation),
        ("Rate Limiter", test_rate_limiter),
        ("Database", test_database),
        ("Scoring Engine", test_scoring_engine),
        ("Pipeline", test_pipeline),
        ("Flask App", test_flask_app),
        ("Startup Validation", test_startup_validation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"\n✅ {test_name} test PASSED")
                passed += 1
            else:
                print(f"\n❌ {test_name} test FAILED")
                failed += 1
        except Exception as e:
            print(f"\n❌ {test_name} test ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"🧪 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The application is ready to run.")
        print("\nTo start the application:")
        print("  python run.py")
        return 0
    else:
        print("❌ Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())