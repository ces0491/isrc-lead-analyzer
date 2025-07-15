"""
API Routes for Prism Analytics Engine - COMPLETE UPDATED VERSION
Precise Digital Lead Generation Tool with YouTube Integration

This is the complete, production-ready API backend for the Prism Analytics Engine.
Includes proper database session management, comprehensive error handling,
and full YouTube integration capabilities.
"""

import os
import time
import logging
import csv
import io
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from typing import Optional, Dict, Any, List
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

# Import core components
from src.core.rate_limiter import rate_limiter, get_rate_limits
from src.core.pipeline import LeadAggregationPipeline
from src.utils.validators import validate_isrc
from config.database import db_manager, Artist, Track, ContactAttempt, OutreachLog, ProcessingLog
from config.settings import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Production-ready CORS configuration
if os.getenv('RENDER') or os.getenv('FLASK_ENV') == 'production':
    # Production CORS - restrict to your frontend domains
    allowed_origins = [
        "https://isrc-analyzer-frontend.onrender.com",
        "https://analytics.precise.digital",              # Custom domain example
        "https://prism.precise.digital",                  # Alternative domain
    ]
    
    # Allow additional origins from environment variable
    extra_origins = os.getenv('CORS_ORIGINS', '').split(',')
    allowed_origins.extend([origin.strip() for origin in extra_origins if origin.strip()])
    
    CORS(app, 
         origins=allowed_origins,
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    logger.info(f"✅ Production CORS configured for origins: {allowed_origins}")
else:
    # Development CORS - allow all origins
    CORS(app)
    logger.info("🛠️  Development CORS configured (all origins allowed)")

# App configuration
app.config.update({
    'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max file size
    'JSON_SORT_KEYS': False,
    'JSONIFY_PRETTYPRINT_REGULAR': True
})

# Initialize services
try:
    pipeline = LeadAggregationPipeline(rate_limiter)
    logger.info("✅ Pipeline initialized successfully")
except Exception as e:
    logger.error(f"❌ Pipeline initialization failed: {e}")
    pipeline = None

# Utility functions
def safe_db_operation(operation_func, *args, **kwargs):
    """Safely execute database operations with proper error handling"""
    try:
        return operation_func(*args, **kwargs)
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in database operation: {e}")
        raise

def validate_request_data(data, required_fields):
    """Validate request data has required fields"""
    if not data:
        return False, "No data provided in request body"
    
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, "Valid"

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'service': 'Prism Analytics Engine',
        'available_endpoints': [
            '/api/health', '/api/status', '/api/analyze-isrc', '/api/analyze-bulk',
            '/api/upload-isrcs', '/api/leads', '/api/export', '/api/youtube/test'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'service': 'Prism Analytics Engine'
    }), 500

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        'error': 'File too large. Maximum size is 16MB.',
        'service': 'Prism Analytics Engine'
    }), 413

# ROOT WELCOME MESSAGE
@app.route('/', methods=['GET'])
def root():
    """Root endpoint with Prism Analytics Engine welcome message"""
    return jsonify({
        'service': 'Prism Analytics Engine',
        'company': 'Precise Digital',
        'tagline': 'Transforming Music Data into Actionable Insights',
        'message': 'Welcome to the Music Industry Lead Generation API',
        'version': '1.0.0',
        'deployment_type': 'separate_services',
        'api_documentation': '/api/',
        'health_check': '/api/health',
        'core_endpoints': {
            'analyze_single_isrc': 'POST /api/analyze-isrc',
            'bulk_analysis': 'POST /api/analyze-bulk',
            'file_upload': 'POST /api/upload-isrcs',
            'get_leads': 'GET /api/leads',
            'export_data': 'POST /api/export',
            'youtube_integration': 'POST /api/youtube/test'
        },
        'integrations': {
            'spotify': '✅ Configured' if os.getenv('SPOTIFY_CLIENT_ID') else '❌ Not configured',
            'youtube': '✅ Configured' if os.getenv('YOUTUBE_API_KEY') else '❌ Not configured',
            'lastfm': '✅ Configured' if os.getenv('LASTFM_API_KEY') else '⚠️  Optional',
            'musicbrainz': '✅ Always available'
        },
        'status': 'operational',
        'timestamp': datetime.utcnow().isoformat()
    })

# API Documentation
@app.route('/api/', methods=['GET'])
def api_documentation():
    """Comprehensive API documentation and status for Prism Analytics Engine"""
    return jsonify({
        'service': 'Prism Analytics Engine API',
        'company': 'Precise Digital',
        'version': '1.0.0',
        'status': 'running',
        'deployment': 'separate_backend_service',
        'description': 'Music industry lead generation through ISRC analysis and multi-platform data aggregation',
        'endpoints': {
            'health_monitoring': {
                'health': 'GET /api/health',
                'status': 'GET /api/status',
                'dashboard_stats': 'GET /api/dashboard/stats'
            },
            'isrc_analysis': {
                'single_isrc': 'POST /api/analyze-isrc',
                'bulk_processing': 'POST /api/analyze-bulk',
                'file_upload': 'POST /api/upload-isrcs'
            },
            'lead_management': {
                'list_leads': 'GET /api/leads',
                'get_artist': 'GET /api/artist/<id>',
                'update_outreach': 'PUT /api/artist/<id>/outreach',
                'export_leads': 'POST /api/export'
            },
            'youtube_integration': {
                'test_api': 'POST /api/youtube/test',
                'get_stats': 'GET /api/youtube/stats',
                'get_opportunities': 'GET /api/youtube/opportunities',
                'refresh_artist': 'POST /api/artist/<id>/youtube/refresh'
            },
            'api_testing': {
                'test_musicbrainz': 'POST /api/musicbrainz/test',
                'test_lastfm': 'POST /api/lastfm/test',
                'rate_limits': 'GET /api/rate-limits'
            }
        },
        'integrations': {
            'musicbrainz': {'status': 'always_available', 'description': 'Free music metadata database'},
            'spotify': {
                'status': 'configured' if os.getenv('SPOTIFY_CLIENT_ID') else 'not_configured',
                'description': 'Music streaming platform with artist/track data'
            },
            'youtube': {
                'status': 'configured' if os.getenv('YOUTUBE_API_KEY') else 'not_configured',
                'description': 'Video platform with channel analytics and engagement data'
            },
            'lastfm': {
                'status': 'configured' if os.getenv('LASTFM_API_KEY') else 'optional',
                'description': 'Social music platform with listening data'
            }
        },
        'data_sources': {
            'primary': ['MusicBrainz', 'Spotify Web API'],
            'secondary': ['YouTube Data API', 'Last.fm API'],
            'target_regions': ['New Zealand', 'Australia', 'Pacific Islands'],
            'lead_scoring': ['Independence', 'Opportunity', 'Geographic']
        },
        'timestamp': datetime.utcnow().isoformat()
    })

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Comprehensive health check for Prism Analytics Engine"""
    db_connected = True
    database_type = 'unknown'
    
    try:
        with db_manager.get_session() as session:
            result = session.execute(text("SELECT 1")).scalar()
            db_connected = (result == 1)
            database_type = str(session.bind.dialect.name)
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_connected = False
    
    # Check pipeline status
    pipeline_status = pipeline is not None
    
    # Check API integrations
    api_status = {
        'musicbrainz': True,  # Always available
        'spotify': bool(os.getenv('SPOTIFY_CLIENT_ID')),
        'youtube': bool(os.getenv('YOUTUBE_API_KEY')),
        'lastfm': bool(os.getenv('LASTFM_API_KEY'))
    }
    
    overall_status = 'healthy' if (db_connected and pipeline_status) else 'degraded'
    
    return jsonify({
        'status': overall_status,
        'service': 'Prism Analytics Engine',
        'company': 'Precise Digital',
        'deployment_type': 'separate_backend_service',
        'components': {
            'database': {
                'connected': db_connected,
                'type': database_type,
                'status': 'healthy' if db_connected else 'error'
            },
            'pipeline': {
                'initialized': pipeline_status,
                'status': 'healthy' if pipeline_status else 'error'
            },
            'api_integrations': api_status,
            'rate_limiter': {
                'status': 'healthy',
                'active_apis': len([k for k, v in api_status.items() if v])
            }
        },
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

# System status endpoint
@app.route('/api/status', methods=['GET'])
def system_status():
    """Get comprehensive system status including rate limits and YouTube integration"""
    try:
        rate_status = get_rate_limits()
        
        # Get database status
        db_status = db_manager.get_status() if hasattr(db_manager, 'get_status') else {
            'connected': True, 'database_type': 'Unknown'
        }
        
        # Check YouTube integration
        youtube_integration = {
            'status': 'available' if settings.apis['youtube'].api_key else 'not_configured',
            'api_key_configured': bool(settings.apis['youtube'].api_key),
            'daily_quota_used': rate_status.get('youtube', {}).get('quota_used_today', 0),
            'daily_quota_limit': rate_status.get('youtube', {}).get('quota_limit_daily', 10000)
        }
        
        return jsonify({
            'service': 'Prism Analytics Engine',
            'status': 'online',
            'timestamp': datetime.utcnow().isoformat(),
            'database_status': {
                'connected': db_status.get('connected', False),
                'type': db_status.get('database_type', 'Unknown'),
                'url_masked': db_status.get('database_url_masked', 'Not available')
            },
            'youtube_integration': youtube_integration,
            'rate_limits': rate_status,
            'cors_configuration': {
                'mode': 'production' if os.getenv('RENDER') else 'development',
                'allowed_origins': os.getenv('CORS_ORIGINS', 'development_mode').split(',') if os.getenv('CORS_ORIGINS') else ['*']
            },
            'environment': os.getenv('FLASK_ENV', 'production'),
            'version': '1.0.0'
        })
        
    except Exception as e:
        logger.error(f"Failed to get system status: {str(e)}")
        return jsonify({
            'service': 'Prism Analytics Engine',
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e),
            'rate_limits': {}
        }), 500

# Single ISRC analysis
@app.route('/api/analyze-isrc', methods=['POST'])
def analyze_isrc():
    """Analyze a single ISRC with full integration support"""
    try:
        data = request.get_json()
        
        if not data or 'isrc' not in data:
            return jsonify({
                'error': 'ISRC required in request body',
                'service': 'Prism Analytics Engine'
            }), 400
        
        # Validate ISRC
        is_valid, result = validate_isrc(data['isrc'])
        if not is_valid:
            return jsonify({
                'error': f'Invalid ISRC: {result}',
                'service': 'Prism Analytics Engine'
            }), 400
        
        isrc = result  # Use cleaned ISRC
        
        # Extract options
        save_to_db = data.get('save_to_db', True)
        force_refresh = data.get('force_refresh', False)
        include_youtube = data.get('include_youtube', True)
        
        # Check for cached data if not forcing refresh
        if not force_refresh and save_to_db:
            try:
                with db_manager.get_session() as session:
                    existing_track = session.query(Track).filter_by(isrc=isrc).first()
                    if existing_track and hasattr(existing_track, 'updated_at'):
                        track_updated_at = existing_track.updated_at
                        if track_updated_at:
                            time_diff = datetime.utcnow() - track_updated_at
                            if time_diff.total_seconds() < 86400:  # 24 hours
                                return jsonify({
                                    'isrc': isrc,
                                    'status': 'cached',
                                    'message': 'Returning cached data. Use force_refresh=true to reprocess.',
                                    'artist_id': existing_track.artist_id,
                                    'last_updated': track_updated_at.isoformat(),
                                    'service': 'Prism Analytics Engine'
                                })
            except Exception as e:
                logger.warning(f"Cache check failed: {e}")
        
        # Process the ISRC
        if not pipeline:
            return jsonify({
                'error': 'Processing pipeline not available',
                'service': 'Prism Analytics Engine'
            }), 500
        
        logger.info(f"Processing ISRC: {isrc}")
        start_time = time.time()
        
        result = pipeline.process_isrc(
            isrc=isrc,
            save_to_database=save_to_db,
            include_youtube=include_youtube,
            force_refresh=force_refresh
        )
        
        processing_time = round(time.time() - start_time, 2)
        
        # Add metadata to response
        result.update({
            'processing_time': processing_time,
            'youtube_integration': {
                'enabled': include_youtube,
                'data_found': bool(result.get('youtube_data')),
                'api_status': 'available' if settings.apis['youtube'].api_key else 'not_configured'
            },
            'service': 'Prism Analytics Engine',
            'timestamp': datetime.utcnow().isoformat()
        })
        
        logger.info(f"ISRC {isrc} processed successfully in {processing_time}s")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in analyze_isrc: {e}")
        return jsonify({
            'error': f'Processing failed: {str(e)}',
            'service': 'Prism Analytics Engine',
            'isrc': data.get('isrc', 'unknown') if 'data' in locals() else 'unknown'
        }), 500

# Bulk ISRC analysis
@app.route('/api/analyze-bulk', methods=['POST'])
def analyze_bulk():
    """Analyze multiple ISRCs with comprehensive error handling"""
    try:
        data = request.get_json()
        
        is_valid, error_msg = validate_request_data(data, ['isrcs'])
        if not is_valid:
            return jsonify({
                'error': error_msg,
                'service': 'Prism Analytics Engine'
            }), 400
        
        isrcs = data['isrcs']
        
        if not isinstance(isrcs, list):
            return jsonify({
                'error': 'ISRCs must be provided as a list',
                'service': 'Prism Analytics Engine'
            }), 400
        
        if len(isrcs) == 0:
            return jsonify({
                'error': 'No ISRCs provided',
                'service': 'Prism Analytics Engine'
            }), 400
        
        if len(isrcs) > settings.max_bulk_isrcs:
            return jsonify({
                'error': f'Too many ISRCs. Maximum allowed: {settings.max_bulk_isrcs}',
                'provided': len(isrcs),
                'service': 'Prism Analytics Engine'
            }), 400
        
        # Validate and clean ISRCs
        cleaned_isrcs = []
        invalid_isrcs = []
        
        for isrc in isrcs:
            if isinstance(isrc, str):
                is_valid, result = validate_isrc(isrc)
                if is_valid:
                    cleaned_isrcs.append(result)
                else:
                    invalid_isrcs.append(isrc)
            else:
                invalid_isrcs.append(str(isrc))
        
        if invalid_isrcs:
            return jsonify({
                'error': 'Invalid ISRCs found',
                'invalid_isrcs': invalid_isrcs[:10],  # Show first 10 invalid ones
                'service': 'Prism Analytics Engine'
            }), 400
        
        if not pipeline:
            return jsonify({
                'error': 'Processing pipeline not available',
                'service': 'Prism Analytics Engine'
            }), 500
        
        # Process batch
        batch_size = data.get('batch_size', 10)
        include_youtube = data.get('include_youtube', True)
        
        logger.info(f"Starting bulk analysis of {len(cleaned_isrcs)} ISRCs")
        start_time = time.time()
        
        result = pipeline.process_bulk_isrcs(
            isrcs=cleaned_isrcs,
            batch_size=batch_size,
            include_youtube=include_youtube
        )
        
        total_time = round(time.time() - start_time, 2)
        
        # Calculate YouTube statistics
        youtube_stats = {
            'artists_with_youtube': 0,
            'youtube_data_collected': 0,
            'total_youtube_subscribers': 0
        }
        
        for item in result.get('results', []):
            if item.get('youtube_data'):
                youtube_stats['youtube_data_collected'] += 1
                if item['youtube_data'].get('channel'):
                    youtube_stats['artists_with_youtube'] += 1
                    subs = item['youtube_data']['channel'].get('statistics', {}).get('subscriber_count', 0)
                    youtube_stats['total_youtube_subscribers'] += int(subs or 0)
        
        # Add metadata
        result.update({
            'total_time': total_time,
            'average_time_per_isrc': round(total_time / len(cleaned_isrcs), 2) if cleaned_isrcs else 0,
            'youtube_statistics': youtube_stats,
            'service': 'Prism Analytics Engine',
            'timestamp': datetime.utcnow().isoformat()
        })
        
        logger.info(f"Bulk analysis completed in {total_time}s")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in analyze_bulk: {e}")
        return jsonify({
            'error': f'Bulk processing failed: {str(e)}',
            'service': 'Prism Analytics Engine',
            'total_processed': 0,
            'successful': 0,
            'failed': len(data.get('isrcs', [])) if 'data' in locals() else 0
        }), 500

# File upload for bulk processing
@app.route('/api/upload-isrcs', methods=['POST'])
def upload_isrcs():
    """Upload CSV/TXT file with ISRCs for bulk processing"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file uploaded',
                'service': 'Prism Analytics Engine'
            }), 400
        
        file = request.files['file']
        
        if not file or not file.filename:
            return jsonify({
                'error': 'No file selected',
                'service': 'Prism Analytics Engine'
            }), 400
        
        # Check file extension
        filename = secure_filename(file.filename)
        if not filename.lower().endswith(('.csv', '.txt')):
            return jsonify({
                'error': 'Only CSV and TXT files are supported',
                'supported_formats': ['.csv', '.txt'],
                'service': 'Prism Analytics Engine'
            }), 400
        
        # Read file content
        try:
            file_content = file.read().decode('utf-8')
        except UnicodeDecodeError:
            try:
                file_content = file.read().decode('utf-8-sig')  # Try with BOM
            except UnicodeDecodeError:
                return jsonify({
                    'error': 'File encoding not supported. Please use UTF-8.',
                    'service': 'Prism Analytics Engine'
                }), 400
        
        # Parse ISRCs from file
        isrcs = []
        
        if filename.lower().endswith('.csv'):
            # Parse CSV
            csv_reader = csv.reader(io.StringIO(file_content))
            for row_num, row in enumerate(csv_reader, 1):
                if row_num == 1 and any('isrc' in cell.lower() for cell in row):
                    # Skip header row if it contains 'ISRC'
                    continue
                
                for cell in row:
                    is_valid, result = validate_isrc(cell)
                    if is_valid:
                        isrcs.append(result)
                        break  # Take first valid ISRC from row
        else:
            # Parse TXT (one ISRC per line)
            for line in file_content.split('\n'):
                is_valid, result = validate_isrc(line.strip())
                if is_valid:
                    isrcs.append(result)
        
        # Remove duplicates while preserving order
        unique_isrcs = []
        seen = set()
        for isrc in isrcs:
            if isrc not in seen:
                unique_isrcs.append(isrc)
                seen.add(isrc)
        
        if not unique_isrcs:
            return jsonify({
                'error': 'No valid ISRCs found in file',
                'service': 'Prism Analytics Engine',
                'filename': filename
            }), 400
        
        if len(unique_isrcs) > settings.max_bulk_isrcs:
            return jsonify({
                'error': f'Too many ISRCs in file. Maximum allowed: {settings.max_bulk_isrcs}',
                'found': len(unique_isrcs),
                'service': 'Prism Analytics Engine'
            }), 400
        
        return jsonify({
            'isrcs': unique_isrcs,
            'count': len(unique_isrcs),
            'filename': filename,
            'message': f'Successfully parsed {len(unique_isrcs)} unique ISRCs',
            'service': 'Prism Analytics Engine',
            'ready_for_processing': True
        })
        
    except Exception as e:
        logger.error(f"Error in upload_isrcs: {e}")
        return jsonify({
            'error': f'File processing failed: {str(e)}',
            'service': 'Prism Analytics Engine'
        }), 500

# Get leads with comprehensive filtering
@app.route('/api/leads', methods=['GET'])
def get_leads():
    """Get filtered list of leads with YouTube filtering options"""
    try:
        # Get and validate query parameters
        tier = request.args.get('tier')
        region = request.args.get('region')
        min_score = request.args.get('min_score', type=int)
        max_score = request.args.get('max_score', type=int)
        youtube_filter = request.args.get('youtube_filter')
        search = request.args.get('search')
        limit = min(request.args.get('limit', 50, type=int), 1000)  # Cap at 1000
        offset = request.args.get('offset', 0, type=int)
        sort_by = request.args.get('sort_by', 'total_score')
        sort_order = request.args.get('sort_order', 'desc')
        
        with db_manager.get_session() as session:
            # Build query
            query = session.query(Artist)
            
            # Apply filters
            if tier:
                query = query.filter(Artist.lead_tier == tier.upper())
            
            if region:
                query = query.filter(Artist.region == region)
            
            if min_score is not None:
                query = query.filter(Artist.total_score >= min_score)
            
            if max_score is not None:
                query = query.filter(Artist.total_score <= max_score)
            
            if search:
                query = query.filter(Artist.name.ilike(f'%{search}%'))
            
            # YouTube filtering
            if youtube_filter:
                if youtube_filter == 'has_channel':
                    query = query.filter(Artist.youtube_channel_id.isnot(None))
                elif youtube_filter == 'no_channel':
                    query = query.filter(Artist.youtube_channel_id.is_(None))
                elif youtube_filter == 'high_potential':
                    query = query.filter(Artist.youtube_growth_potential == 'high_potential')
                elif youtube_filter == 'underperforming':
                    query = query.filter(
                        Artist.monthly_listeners > 10000,
                        Artist.youtube_subscribers < Artist.monthly_listeners * 0.3
                    )
                elif youtube_filter == 'active_uploaders':
                    query = query.filter(Artist.youtube_upload_frequency.in_(['very_active', 'active']))
            
            # Apply sorting
            sort_column = Artist.total_score  # Default
            if sort_by == 'name':
                sort_column = Artist.name
            elif sort_by == 'created_at':
                sort_column = Artist.created_at
            elif sort_by == 'youtube_subscribers':
                sort_column = Artist.youtube_subscribers
            elif sort_by == 'monthly_listeners':
                sort_column = Artist.monthly_listeners
            
            if sort_order.lower() == 'desc':
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
            
            # Get total count before pagination
            total_count = query.count()
            
            # Apply pagination
            leads = query.offset(offset).limit(limit).all()
            
            # Format results
            results = []
            for artist in leads:
                # Safe attribute access
                last_release_date = getattr(artist, 'last_release_date', None)
                created_at = getattr(artist, 'created_at', None)
                updated_at = getattr(artist, 'updated_at', None)
                
                result_item = {
                    'id': artist.id,
                    'name': artist.name,
                    'country': artist.country,
                    'region': artist.region,
                    'genre': artist.genre,
                    'total_score': artist.total_score,
                    'independence_score': artist.independence_score,
                    'opportunity_score': artist.opportunity_score,
                    'geographic_score': artist.geographic_score,
                    'lead_tier': artist.lead_tier,
                    'monthly_listeners': artist.monthly_listeners,
                    'last_release_date': last_release_date.isoformat() if last_release_date else None,
                    'outreach_status': artist.outreach_status,
                    'contact_email': artist.contact_email,
                    'website': artist.website,
                    'social_handles': artist.social_handles,
                    'youtube_summary': {
                        'has_channel': bool(artist.youtube_channel_id),
                        'channel_url': artist.youtube_channel_url,
                        'subscribers': artist.youtube_subscribers or 0,
                        'total_views': artist.youtube_total_views or 0,
                        'video_count': artist.youtube_video_count or 0,
                        'upload_frequency': artist.youtube_upload_frequency,
                        'growth_potential': artist.youtube_growth_potential,
                        'engagement_rate': artist.youtube_engagement_rate or 0.0
                    },
                    'created_at': created_at.isoformat() if created_at else None,
                    'updated_at': updated_at.isoformat() if updated_at else None
                }
                results.append(result_item)
            
            return jsonify({
                'leads': results,
                'pagination': {
                    'total': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < total_count,
                    'page': (offset // limit) + 1,
                    'total_pages': (total_count + limit - 1) // limit
                },
                'filters_applied': {
                    'tier': tier,
                    'region': region,
                    'min_score': min_score,
                    'max_score': max_score,
                    'youtube_filter': youtube_filter,
                    'search': search,
                    'sort_by': sort_by,
                    'sort_order': sort_order
                },
                'service': 'Prism Analytics Engine',
                'timestamp': datetime.utcnow().isoformat()
            })
        
    except Exception as e:
        logger.error(f"Error in get_leads: {e}")
        return jsonify({
            'error': f'Failed to fetch leads: {str(e)}',
            'service': 'Prism Analytics Engine'
        }), 500

# Get individual artist details
@app.route('/api/artist/<int:artist_id>', methods=['GET'])
def get_artist(artist_id):
    """Get detailed information for a specific artist including YouTube data"""
    try:
        with db_manager.get_session() as session:
            artist = session.query(Artist).filter_by(id=artist_id).first()
            
            if not artist:
                return jsonify({
                    'error': 'Artist not found',
                    'service': 'Prism Analytics Engine'
                }), 404
            
            # Get associated tracks
            tracks = session.query(Track).filter_by(artist_id=artist_id).all()
            
            # Get contact attempts
            contacts = session.query(ContactAttempt).filter_by(artist_id=artist_id).all()
            
            # Safe datetime access
            last_release_date = getattr(artist, 'last_release_date', None)
            youtube_last_upload = getattr(artist, 'youtube_last_upload', None)
            created_at = getattr(artist, 'created_at', None)
            updated_at = getattr(artist, 'updated_at', None)
            last_scraped = getattr(artist, 'last_scraped', None)
            
            result = {
                'id': artist.id,
                'name': artist.name,
                'musicbrainz_id': artist.musicbrainz_id,
                'spotify_id': artist.spotify_id,
                'country': artist.country,
                'region': artist.region,
                'genre': artist.genre,
                'scores': {
                    'total_score': artist.total_score,
                    'independence_score': artist.independence_score,
                    'opportunity_score': artist.opportunity_score,
                    'geographic_score': artist.geographic_score,
                    'lead_tier': artist.lead_tier
                },
                'metrics': {
                    'monthly_listeners': artist.monthly_listeners,
                    'follower_count': artist.follower_count,
                    'release_count': artist.release_count,
                    'last_release_date': last_release_date.isoformat() if last_release_date else None
                },
                'youtube_metrics': {
                    'channel_id': artist.youtube_channel_id,
                    'channel_url': artist.youtube_channel_url,
                    'subscribers': artist.youtube_subscribers,
                    'total_views': artist.youtube_total_views,
                    'video_count': artist.youtube_video_count,
                    'upload_frequency': artist.youtube_upload_frequency,
                    'engagement_rate': artist.youtube_engagement_rate,
                    'growth_potential': artist.youtube_growth_potential,
                    'last_upload': youtube_last_upload.isoformat() if youtube_last_upload else None,
                    'has_channel': bool(artist.youtube_channel_id)
                },
                'contact_info': {
                    'email': artist.contact_email,
                    'website': artist.website,
                    'social_handles': artist.social_handles,
                    'management_contact': artist.management_contact
                },
                'outreach_status': artist.outreach_status,
                'tracks': [{
                    'id': track.id,
                    'isrc': track.isrc,
                    'title': track.title,
                    'release_date': (lambda rd: rd.isoformat() if rd else None)(getattr(track, 'release_date', None)),
                    'label': track.label,
                    'spotify_popularity': track.spotify_popularity
                } for track in tracks],
                'contact_attempts': [{
                    'method': contact.contact_method,
                    'value': contact.contact_value,
                    'confidence': contact.confidence_score,
                    'source': contact.source,
                    'verified': contact.verified
                } for contact in contacts],
                'timestamps': {
                    'created_at': created_at.isoformat() if created_at else None,
                    'updated_at': updated_at.isoformat() if updated_at else None,
                    'last_scraped': last_scraped.isoformat() if last_scraped else None
                },
                'service': 'Prism Analytics Engine'
            }
            
            return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_artist: {e}")
        return jsonify({
            'error': f'Failed to fetch artist: {str(e)}',
            'service': 'Prism Analytics Engine'
        }), 500

# Update outreach status
@app.route('/api/artist/<int:artist_id>/outreach', methods=['PUT'])
def update_outreach_status(artist_id):
    """Update outreach status for an artist"""
    try:
        data = request.get_json()
        
        is_valid, error_msg = validate_request_data(data, ['status'])
        if not is_valid:
            return jsonify({
                'error': error_msg,
                'service': 'Prism Analytics Engine'
            }), 400
        
        status = data['status']
        valid_statuses = ['not_contacted', 'contacted', 'responded', 'interested', 'not_interested', 'converted']
        
        if status not in valid_statuses:
            return jsonify({
                'error': f'Invalid status. Must be one of: {valid_statuses}',
                'service': 'Prism Analytics Engine'
            }), 400
        
        with db_manager.get_session() as session:
            artist = session.query(Artist).filter_by(id=artist_id).first()
            
            if not artist:
                return jsonify({
                    'error': 'Artist not found',
                    'service': 'Prism Analytics Engine'
                }), 404
            
            # Update artist status
            artist.outreach_status = status
            artist.updated_at = datetime.utcnow()
            
            # Log the outreach attempt if notes provided
            notes = data.get('notes')
            if notes:
                outreach_log = OutreachLog(
                    artist_id=artist_id,
                    contact_date=datetime.utcnow(),
                    method=data.get('method', 'manual'),
                    notes=notes,
                    conversion_status=status if status in ['interested', 'not_interested', 'converted'] else 'no_response'
                )
                session.add(outreach_log)
            
            return jsonify({
                'message': 'Outreach status updated successfully',
                'artist_id': artist_id,
                'new_status': status,
                'updated_at': datetime.utcnow().isoformat(),
                'service': 'Prism Analytics Engine'
            })
        
    except Exception as e:
        logger.error(f"Error in update_outreach_status: {e}")
        return jsonify({
            'error': f'Failed to update outreach status: {str(e)}',
            'service': 'Prism Analytics Engine'
        }), 500

# Export leads to CSV
@app.route('/api/export', methods=['POST'])
def export_leads():
    """Export filtered leads to CSV including YouTube data"""
    try:
        data = request.get_json() or {}
        filters = data.get('filters', {})
        include_youtube_data = data.get('include_youtube_data', True)
        
        with db_manager.get_session() as session:
            # Build query with filters
            query = session.query(Artist)
            
            if filters.get('tier'):
                query = query.filter(Artist.lead_tier == filters['tier'].upper())
            
            if filters.get('region'):
                query = query.filter(Artist.region == filters['region'])
            
            if filters.get('min_score'):
                query = query.filter(Artist.total_score >= filters['min_score'])
            
            if filters.get('max_score'):
                query = query.filter(Artist.total_score <= filters['max_score'])
            
            # YouTube filtering for export
            if filters.get('youtube_filter'):
                youtube_filter = filters['youtube_filter']
                if youtube_filter == 'has_channel':
                    query = query.filter(Artist.youtube_channel_id.isnot(None))
                elif youtube_filter == 'no_channel':
                    query = query.filter(Artist.youtube_channel_id.is_(None))
                elif youtube_filter == 'high_potential':
                    query = query.filter(Artist.youtube_growth_potential == 'high_potential')
            
            # Order by score
            leads = query.order_by(Artist.total_score.desc()).all()
            
            if not leads:
                return jsonify({
                    'error': 'No leads found with current filters',
                    'service': 'Prism Analytics Engine'
                }), 404
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Define headers
            basic_headers = [
                'Artist Name', 'Country', 'Region', 'Genre', 'Total Score',
                'Independence Score', 'Opportunity Score', 'Geographic Score',
                'Lead Tier', 'Monthly Listeners', 'Last Release Date',
                'Outreach Status', 'Contact Email', 'Website', 'Social Handles',
                'Created Date'
            ]
            
            youtube_headers = [
                'YouTube Channel ID', 'YouTube Channel URL', 'YouTube Subscribers', 
                'YouTube Total Views', 'YouTube Video Count', 'YouTube Upload Frequency', 
                'YouTube Growth Potential', 'YouTube Engagement Rate'
            ]
            
            headers = basic_headers + (youtube_headers if include_youtube_data else [])
            writer.writerow(headers)
            
            # Write data
            for artist in leads:
                # Safe datetime access
                last_release_date = getattr(artist, 'last_release_date', None)
                created_at = getattr(artist, 'created_at', None)
                
                basic_data = [
                    artist.name,
                    artist.country or '',
                    artist.region or '',
                    artist.genre or '',
                    artist.total_score,
                    artist.independence_score,
                    artist.opportunity_score,
                    artist.geographic_score,
                    artist.lead_tier,
                    artist.monthly_listeners or 0,
                    last_release_date.strftime('%Y-%m-%d') if last_release_date else '',
                    artist.outreach_status or '',
                    artist.contact_email or '',
                    artist.website or '',
                    str(getattr(artist, 'social_handles', '')) if getattr(artist, 'social_handles', None) else '',
                    created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else ''
                ]
                
                youtube_data = [
                    artist.youtube_channel_id or '',
                    artist.youtube_channel_url or '',
                    artist.youtube_subscribers or 0,
                    artist.youtube_total_views or 0,
                    artist.youtube_video_count or 0,
                    artist.youtube_upload_frequency or '',
                    artist.youtube_growth_potential or '',
                    artist.youtube_engagement_rate or 0.0
                ]
                
                row_data = basic_data + (youtube_data if include_youtube_data else [])
                writer.writerow(row_data)
            
            csv_content = output.getvalue()
            output.close()
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'prism_analytics_leads_{timestamp}.csv'
            
            return jsonify({
                'csv_data': csv_content,
                'filename': filename,
                'count': len(leads),
                'includes_youtube_data': include_youtube_data,
                'filters_applied': filters,
                'generated_at': datetime.utcnow().isoformat(),
                'service': 'Prism Analytics Engine'
            })
        
    except Exception as e:
        logger.error(f"Error in export_leads: {e}")
        return jsonify({
            'error': f'Export failed: {str(e)}',
            'service': 'Prism Analytics Engine'
        }), 500

# Add this to your src/api/routes.py file

@app.route('/api/analyze-isrc-enhanced', methods=['POST'])
def analyze_isrc_enhanced():
    """
    Enhanced ISRC analysis with comprehensive track metadata for distribution teams
    """
    try:
        data = request.get_json()
        
        if not data or 'isrc' not in data:
            return jsonify({
                'error': 'ISRC required in request body',
                'service': 'Prism Analytics Engine'
            }), 400
        
        # Validate ISRC
        is_valid, result = validate_isrc(data['isrc'])
        if not is_valid:
            return jsonify({
                'error': f'Invalid ISRC: {result}',
                'service': 'Prism Analytics Engine'
            }), 400
        
        isrc = result  # Use cleaned ISRC
        
        # Import the enhanced collector
        from src.services.enhanced_track_metadata import EnhancedTrackMetadataCollector
        
        # Initialize enhanced collector
        enhanced_collector = EnhancedTrackMetadataCollector(rate_limiter)
        
        logger.info(f"Starting enhanced processing for ISRC: {isrc}")
        start_time = time.time()
        
        # Collect comprehensive track metadata
        track_metadata = enhanced_collector.collect_comprehensive_track_data(isrc)
        
        processing_time = round(time.time() - start_time, 2)
        
        # Convert to JSON-serializable format
        result = {
            'isrc': track_metadata.isrc,
            'status': 'completed',
            'processing_time': processing_time,
            
            # Basic Information
            'track_data': {
                'title': track_metadata.title,
                'artist': track_metadata.artist,
                'album': track_metadata.album,
                'duration_ms': track_metadata.duration_ms,
                'release_date': track_metadata.release_date.isoformat() if track_metadata.release_date else None,
                'genre': track_metadata.genre,
                'tags': track_metadata.tags
            },
            
            # Comprehensive Credits
            'credits': {
                'composers': track_metadata.credits.composers,
                'lyricists': track_metadata.credits.lyricists,
                'producers': track_metadata.credits.producers,
                'performers': track_metadata.credits.performers,
                'engineers': track_metadata.credits.engineers,
                'other_credits': track_metadata.credits.other_credits
            },
            
            # Lyrics Information
            'lyrics': {
                'content': track_metadata.lyrics,
                'language': track_metadata.lyrics_language,
                'copyright': track_metadata.lyrics_copyright,
                'source': 'Available' if track_metadata.lyrics else None
            },
            
            # Technical Details
            'technical': {
                'key': track_metadata.key,
                'tempo_bpm': track_metadata.tempo_bpm,
                'time_signature': track_metadata.time_signature,
                'energy': track_metadata.energy,
                'valence': track_metadata.valence,
                'danceability': track_metadata.danceability,
                'acousticness': track_metadata.acousticness,
                'instrumentalness': track_metadata.instrumentalness,
                'speechiness': track_metadata.speechiness,
                'loudness': track_metadata.loudness
            },
            
            # Publishing & Rights
            'rights': {
                'publisher': track_metadata.publisher,
                'record_label': track_metadata.record_label,
                'copyright_info': track_metadata.copyright_info,
                'publishing_splits': track_metadata.publishing_splits
            },
            
            # Platform Information
            'platform_availability': track_metadata.platform_availability,
            'platform_ids': track_metadata.platform_ids,
            
            # Recording Information
            'recording_info': {
                'location': track_metadata.recording_location,
                'date': track_metadata.recording_date.isoformat() if track_metadata.recording_date else None
            },
            
            # Metadata
            'data_sources_used': track_metadata.data_sources,
            'confidence_score': track_metadata.confidence_score,
            'service': 'Prism Analytics Engine',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Enhanced ISRC {isrc} processed successfully in {processing_time}s")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in analyze_isrc_enhanced: {e}")
        return jsonify({
            'error': f'Enhanced processing failed: {str(e)}',
            'service': 'Prism Analytics Engine',
            'isrc': data.get('isrc', 'unknown') if 'data' in locals() else 'unknown'
        }), 500


# Also add a route to get enhanced track data for existing tracks
@app.route('/api/track/<isrc>/enhanced', methods=['GET'])
def get_enhanced_track_data(isrc):
    """
    Get enhanced track data for a specific ISRC
    """
    try:
        # Validate ISRC
        is_valid, result = validate_isrc(isrc)
        if not is_valid:
            return jsonify({
                'error': f'Invalid ISRC: {result}',
                'service': 'Prism Analytics Engine'
            }), 400
        
        clean_isrc = result
        
        # Import the enhanced collector
        from src.services.enhanced_track_metadata import EnhancedTrackMetadataCollector
        
        # Initialize enhanced collector
        enhanced_collector = EnhancedTrackMetadataCollector(rate_limiter)
        
        # Collect comprehensive track metadata
        track_metadata = enhanced_collector.collect_comprehensive_track_data(clean_isrc)
        
        # Convert to JSON-serializable format (same as above)
        result = {
            'isrc': track_metadata.isrc,
            'status': 'completed',
            
            # Basic Information
            'track_data': {
                'title': track_metadata.title,
                'artist': track_metadata.artist,
                'album': track_metadata.album,
                'duration_ms': track_metadata.duration_ms,
                'release_date': track_metadata.release_date.isoformat() if track_metadata.release_date else None,
                'genre': track_metadata.genre,
                'tags': track_metadata.tags
            },
            
            # Comprehensive Credits
            'credits': {
                'composers': track_metadata.credits.composers,
                'lyricists': track_metadata.credits.lyricists,
                'producers': track_metadata.credits.producers,
                'performers': track_metadata.credits.performers,
                'engineers': track_metadata.credits.engineers,
                'other_credits': track_metadata.credits.other_credits
            },
            
            # Lyrics Information
            'lyrics': {
                'content': track_metadata.lyrics,
                'language': track_metadata.lyrics_language,
                'copyright': track_metadata.lyrics_copyright,
                'source': 'Available' if track_metadata.lyrics else None
            },
            
            # Technical Details
            'technical': {
                'key': track_metadata.key,
                'tempo_bpm': track_metadata.tempo_bpm,
                'time_signature': track_metadata.time_signature,
                'energy': track_metadata.energy,
                'valence': track_metadata.valence,
                'danceability': track_metadata.danceability,
                'acousticness': track_metadata.acousticness,
                'instrumentalness': track_metadata.instrumentalness,
                'speechiness': track_metadata.speechiness,
                'loudness': track_metadata.loudness
            },
            
            # Publishing & Rights
            'rights': {
                'publisher': track_metadata.publisher,
                'record_label': track_metadata.record_label,
                'copyright_info': track_metadata.copyright_info,
                'publishing_splits': track_metadata.publishing_splits
            },
            
            # Platform Information
            'platform_availability': track_metadata.platform_availability,
            'platform_ids': track_metadata.platform_ids,
            
            # Recording Information
            'recording_info': {
                'location': track_metadata.recording_location,
                'date': track_metadata.recording_date.isoformat() if track_metadata.recording_date else None
            },
            
            # Metadata
            'data_sources_used': track_metadata.data_sources,
            'confidence_score': track_metadata.confidence_score,
            'service': 'Prism Analytics Engine',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_enhanced_track_data: {e}")
        return jsonify({
            'error': f'Failed to fetch enhanced track data: {str(e)}',
            'service': 'Prism Analytics Engine'
        }), 500

# Dashboard statistics
@app.route('/api/dashboard/stats', methods=['GET'])
def dashboard_stats():
    """Get comprehensive dashboard statistics"""
    try:
        stats = db_manager.get_dashboard_stats() if hasattr(db_manager, 'get_dashboard_stats') else {}
        
        # Add service metadata
        stats.update({
            'service': 'Prism Analytics Engine',
            'generated_at': datetime.utcnow().isoformat(),
            'company': 'Precise Digital'
        })
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error in dashboard_stats: {e}")
        return jsonify({
            'error': f'Failed to fetch dashboard stats: {str(e)}',
            'service': 'Prism Analytics Engine'
        }), 500

# YouTube Integration Endpoints

@app.route('/api/youtube/test', methods=['POST'])
def test_youtube_integration():
    """Test YouTube API integration for a specific artist"""
    try:
        data = request.get_json()
        
        is_valid, error_msg = validate_request_data(data, ['artist_name'])
        if not is_valid:
            return jsonify({
                'error': error_msg,
                'service': 'Prism Analytics Engine'
            }), 400
        
        artist_name = data['artist_name']
        
        from src.integrations.youtube import youtube_client
        
        # Test channel search
        channel_data = youtube_client.search_artist_channel(artist_name)
        
        if not channel_data:
            return jsonify({
                'status': 'not_found',
                'message': f'No YouTube channel found for "{artist_name}"',
                'artist_name': artist_name,
                'service': 'Prism Analytics Engine'
            })
        
        # Get additional analytics if channel found
        analytics = youtube_client.get_channel_analytics(channel_data['channel_id'])
        videos = youtube_client.search_artist_videos(artist_name, max_results=5)
        
        return jsonify({
            'status': 'success',
            'artist_name': artist_name,
            'channel_data': channel_data,
            'analytics': analytics,
            'recent_videos': videos,
            'integration_status': 'YouTube API working correctly',
            'service': 'Prism Analytics Engine'
        })
        
    except Exception as e:
        logger.error(f"YouTube API test failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'message': 'YouTube API integration test failed',
            'service': 'Prism Analytics Engine'
        }), 500

@app.route('/api/youtube/opportunities', methods=['GET'])
def get_youtube_opportunities():
    """Get artists with YouTube opportunities for targeted outreach"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        opportunities = db_manager.get_youtube_opportunities(limit=limit) if hasattr(db_manager, 'get_youtube_opportunities') else []
        
        return jsonify({
            'youtube_opportunities': opportunities,
            'generated_at': datetime.utcnow().isoformat(),
            'service': 'Prism Analytics Engine'
        })
        
    except Exception as e:
        logger.error(f"Error in get_youtube_opportunities: {e}")
        return jsonify({
            'error': f'Failed to fetch YouTube opportunities: {str(e)}',
            'service': 'Prism Analytics Engine'
        }), 500

@app.route('/api/youtube/stats', methods=['GET'])
def get_youtube_stats():
    """Get overall YouTube integration statistics"""
    try:
        stats = db_manager.get_dashboard_stats() if hasattr(db_manager, 'get_dashboard_stats') else {}
        youtube_stats = stats.get('youtube_statistics', {})
        
        total_artists = stats.get('total_artists', 0)
        artists_with_youtube = youtube_stats.get('artists_with_youtube', 0)
        coverage_percentage = (artists_with_youtube / max(total_artists, 1)) * 100
        
        return jsonify({
            'total_artists': total_artists,
            'artists_with_youtube_channels': artists_with_youtube,
            'youtube_coverage_percentage': round(coverage_percentage, 1),
            'total_youtube_subscribers': youtube_stats.get('total_youtube_subscribers', 0),
            'average_youtube_subscribers': round(youtube_stats.get('avg_youtube_subscribers', 0)),
            'high_potential_channels': youtube_stats.get('high_potential_channels', 0),
            'api_status': 'available' if settings.apis['youtube'].api_key else 'not_configured',
            'generated_at': datetime.utcnow().isoformat(),
            'service': 'Prism Analytics Engine'
        })
        
    except Exception as e:
        logger.error(f"Error in get_youtube_stats: {e}")
        return jsonify({
            'error': f'Failed to fetch YouTube stats: {str(e)}',
            'service': 'Prism Analytics Engine'
        }), 500

@app.route('/api/artist/<int:artist_id>/youtube/refresh', methods=['POST'])
def refresh_artist_youtube_data(artist_id):
    """Refresh YouTube data for a specific artist"""
    try:
        with db_manager.get_session() as session:
            artist = session.query(Artist).filter_by(id=artist_id).first()
            if not artist:
                return jsonify({
                    'error': 'Artist not found',
                    'service': 'Prism Analytics Engine'
                }), 404
            
            from src.integrations.youtube import youtube_client
            
            # Get fresh YouTube data
            artist_name = getattr(artist, 'name', 'Unknown Artist')
            channel_data = youtube_client.search_artist_channel(artist_name)
            
            if not channel_data:
                return jsonify({
                    'status': 'no_channel_found',
                    'message': f'No YouTube channel found for "{artist.name}"',
                    'service': 'Prism Analytics Engine'
                })
            
            # Prepare YouTube data for database update
            youtube_update_data = {
                'channel_id': channel_data.get('channel_id'),
                'channel_url': f"https://youtube.com/channel/{channel_data.get('channel_id')}",
                'subscribers': channel_data.get('statistics', {}).get('subscriber_count', 0),
                'total_views': channel_data.get('statistics', {}).get('view_count', 0),
                'video_count': channel_data.get('statistics', {}).get('video_count', 0)
            }
            
            # Get analytics if available
            if channel_data.get('channel_id'):
                analytics = youtube_client.get_channel_analytics(channel_data['channel_id'])
                if analytics:
                    youtube_update_data.update({
                        'upload_frequency': analytics.get('recent_activity', {}).get('upload_frequency'),
                        'growth_potential': analytics.get('growth_potential'),
                        'engagement_rate': analytics.get('engagement_indicators', {}).get('subscriber_to_view_ratio', 0)
                    })
            
            # Update database
            success = db_manager.update_youtube_data(artist_id, youtube_update_data) if hasattr(db_manager, 'update_youtube_data') else False
            
            if success:
                return jsonify({
                    'status': 'success',
                    'message': 'YouTube data refreshed successfully',
                    'updated_data': youtube_update_data,
                    'service': 'Prism Analytics Engine'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to update YouTube data in database',
                    'service': 'Prism Analytics Engine'
                }), 500
            
    except Exception as e:
        logger.error(f"Error in refresh_artist_youtube_data: {e}")
        return jsonify({
            'error': f'Failed to refresh YouTube data: {str(e)}',
            'service': 'Prism Analytics Engine'
        }), 500

# API Testing Endpoints

@app.route('/api/musicbrainz/test', methods=['POST'])
def test_musicbrainz_api():
    """Test MusicBrainz API integration"""
    try:
        # Test MusicBrainz with a simple query
        result = rate_limiter.make_request(
            'musicbrainz',
            'recording',
            params={
                'query': 'isrc:USRC17607839',
                'limit': 1,
                'fmt': 'json'
            }
        )
        
        if result:
            return jsonify({
                'status': 'success',
                'message': 'MusicBrainz API is working correctly',
                'results_found': len(result.get('recordings', [])),
                'service': 'Prism Analytics Engine'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'MusicBrainz API request failed',
                'service': 'Prism Analytics Engine'
            }), 500
            
    except Exception as e:
        logger.error(f"MusicBrainz API test failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'service': 'Prism Analytics Engine'
        }), 500

@app.route('/api/lastfm/test', methods=['POST'])
def test_lastfm_api():
    """Test Last.fm API integration"""
    try:
        data = request.get_json() or {}
        artist_name = data.get('artist_name', 'Test Artist')
        
        # Test Last.fm artist info
        result = rate_limiter.make_request(
            'lastfm', 
            '',
            params={
                'method': 'artist.getinfo',
                'artist': artist_name
            }
        )
        
        if result and not result.get('error'):
            return jsonify({
                'status': 'success',
                'message': 'Last.fm API is working correctly',
                'test_query': artist_name,
                'service': 'Prism Analytics Engine'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result.get('message', 'Last.fm API request failed'),
                'service': 'Prism Analytics Engine'
            }), 500
            
    except Exception as e:
        logger.error(f"Last.fm API test failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'service': 'Prism Analytics Engine'
        }), 500

@app.route('/api/rate-limits', methods=['GET'])
def get_rate_limit_status():
    """Get current rate limit status for all APIs"""
    try:
        status = get_rate_limits()
        return jsonify({
            'rate_limits': status,
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'Prism Analytics Engine'
        })
    except Exception as e:
        logger.error(f"Failed to get rate limits: {e}")
        return jsonify({
            'rate_limits': {},
            'error': str(e),
            'service': 'Prism Analytics Engine'
        }), 500

@app.route('/api/rate-limits/reset', methods=['POST'])
def reset_rate_limits():
    """Reset rate limit counters (for testing)"""
    try:
        data = request.get_json() or {}
        api_name = data.get('api_name')
        
        rate_limiter.reset_counters(api_name)
        
        return jsonify({
            'status': 'success',
            'message': f'Rate limits reset for {api_name or "all APIs"}',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'Prism Analytics Engine'
        })
    except Exception as e:
        logger.error(f"Failed to reset rate limits: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'service': 'Prism Analytics Engine'
        }), 500

# Request logging middleware
@app.before_request
def log_request_info():
    """Log API requests for monitoring"""
    if os.getenv('LOG_API_REQUESTS', 'false').lower() == 'true':
        logger.info(f'{request.method} {request.url} - {request.remote_addr}')

# Response headers middleware
@app.after_request
def after_request(response):
    """Add common response headers"""
    response.headers['X-Service'] = 'Prism Analytics Engine'
    response.headers['X-Company'] = 'Precise Digital'
    response.headers['X-Version'] = '1.0.0'
    return response

if __name__ == '__main__':
    # Initialize database
    try:
        from config.database import init_db
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
    # Run the app
    logger.info("🎵 Starting Prism Analytics Engine API Server")
    app.run(
        host=settings.app.host,
        port=settings.app.port,
        debug=settings.app.debug
    )