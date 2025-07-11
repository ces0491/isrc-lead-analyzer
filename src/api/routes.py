"""
Flask API routes for Precise Digital Lead Generation Tool with YouTube Integration
Provides REST endpoints for the frontend application
"""
import os
import csv
import io
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

from src.core.pipeline import LeadAggregationPipeline
from src.core.rate_limiter import RateLimitManager
from src.utils.validators import validate_isrc
from config.database import DatabaseManager, get_db, Artist, Track
from config.settings import settings

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Configuration
app.config['SECRET_KEY'] = settings.app.secret_key
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize services
rate_limiter = RateLimitManager()
pipeline = LeadAggregationPipeline(rate_limiter)
db_manager = DatabaseManager()

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'youtube_integration': 'enabled'
    })

# System status endpoint
@app.route('/api/status', methods=['GET'])
def system_status():
    """Get system status including API rate limits and YouTube integration"""
    rate_status = rate_limiter.get_rate_limit_status()
    processing_stats = pipeline.get_processing_stats()
    
    # Check YouTube API availability
    youtube_status = 'available' if settings.apis['youtube'].api_key else 'not_configured'
    
    return jsonify({
        'rate_limits': rate_status,
        'processing_stats': processing_stats,
        'database_status': 'connected',
        'youtube_integration': {
            'status': youtube_status,
            'api_key_configured': bool(settings.apis['youtube'].api_key),
            'daily_quota_used': rate_status.get('youtube', {}).get('requests_today', 0),
            'daily_quota_limit': rate_status.get('youtube', {}).get('daily_limit', 10000)
        },
        'timestamp': datetime.utcnow().isoformat()
    })

# Single ISRC analysis
@app.route('/api/analyze-isrc', methods=['POST'])
def analyze_isrc():
    """Analyze a single ISRC with YouTube integration"""
    try:
        data = request.get_json()
        
        if not data or 'isrc' not in data:
            return jsonify({'error': 'ISRC required in request body'}), 400
        
        # Use proper validation
        is_valid, result = validate_isrc(data['isrc'])
        if not is_valid:
            return jsonify({'error': result}), 400
        
        isrc = result  # Use cleaned ISRC
        
        # Check if already processed recently
        save_to_db = data.get('save_to_db', True)
        force_refresh = data.get('force_refresh', False)
        include_youtube = data.get('include_youtube', True)  # NEW: YouTube toggle
        
        if not force_refresh and save_to_db:
            # Check if we have recent data for this ISRC
            try:
                existing_track = db_manager.session.query(Track).filter_by(isrc=isrc).first()
                if existing_track and existing_track.updated_at:
                    # Return cached data if processed within last 24 hours
                    time_diff = datetime.utcnow() - existing_track.updated_at
                    if time_diff.total_seconds() < 86400:  # 24 hours
                        return jsonify({
                            'isrc': isrc,
                            'status': 'cached',
                            'message': 'Returning cached data. Use force_refresh=true to reprocess.',
                            'artist_id': existing_track.artist_id,
                            'last_updated': existing_track.updated_at.isoformat()
                        })
            except Exception as e:
                # If cache check fails, continue with processing
                print(f"Cache check failed: {e}")
        
        # Process the ISRC
        result = pipeline.process_isrc(isrc, save_to_db=save_to_db)
        
        # Add YouTube integration status to response
        result['youtube_integration'] = {
            'enabled': include_youtube,
            'data_found': bool(result.get('youtube_data')),
            'api_status': 'available' if settings.apis['youtube'].api_key else 'not_configured'
        }
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in analyze_isrc: {e}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

# Bulk ISRC analysis
@app.route('/api/analyze-bulk', methods=['POST'])
def analyze_bulk():
    """Analyze multiple ISRCs with YouTube integration"""
    try:
        data = request.get_json()
        
        if not data or 'isrcs' not in data:
            return jsonify({'error': 'ISRCs list required in request body'}), 400
        
        isrcs = data['isrcs']
        
        if not isinstance(isrcs, list):
            return jsonify({'error': 'ISRCs must be provided as a list'}), 400
        
        if len(isrcs) == 0:
            return jsonify({'error': 'No ISRCs provided'}), 400
        
        if len(isrcs) > settings.max_bulk_isrcs:
            return jsonify({
                'error': f'Too many ISRCs. Maximum allowed: {settings.max_bulk_isrcs}',
                'provided': len(isrcs)
            }), 400
        
        # Clean and validate ISRCs
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
                'invalid_isrcs': invalid_isrcs[:10]  # Show first 10 invalid ones
            }), 400
        
        # Process batch
        batch_size = data.get('batch_size', 10)
        result = pipeline.process_bulk(cleaned_isrcs, batch_size=batch_size)
        
        # Add YouTube statistics to bulk result
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
        
        result['youtube_statistics'] = youtube_stats
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in analyze_bulk: {e}")
        return jsonify({'error': f'Bulk processing failed: {str(e)}'}), 500

# File upload for bulk processing
@app.route('/api/upload-isrcs', methods=['POST'])
def upload_isrcs():
    """Upload CSV/TXT file with ISRCs for bulk processing"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        filename = secure_filename(file.filename)
        if not filename.lower().endswith(('.csv', '.txt')):
            return jsonify({'error': 'Only CSV and TXT files are supported'}), 400
        
        # Read file content
        file_content = file.read().decode('utf-8')
        
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
            return jsonify({'error': 'No valid ISRCs found in file'}), 400
        
        if len(unique_isrcs) > settings.max_bulk_isrcs:
            return jsonify({
                'error': f'Too many ISRCs in file. Maximum allowed: {settings.max_bulk_isrcs}',
                'found': len(unique_isrcs)
            }), 400
        
        return jsonify({
            'isrcs': unique_isrcs,
            'count': len(unique_isrcs),
            'filename': filename,
            'message': f'Successfully parsed {len(unique_isrcs)} unique ISRCs'
        })
        
    except Exception as e:
        print(f"Error in upload_isrcs: {e}")
        return jsonify({'error': f'File processing failed: {str(e)}'}), 500

# Get leads list with filtering including YouTube filters
@app.route('/api/leads', methods=['GET'])
def get_leads():
    """Get filtered list of leads with YouTube filtering options"""
    try:
        # Get query parameters
        tier = request.args.get('tier')
        region = request.args.get('region')
        min_score = request.args.get('min_score', type=int)
        max_score = request.args.get('max_score', type=int)
        youtube_filter = request.args.get('youtube_filter')  # NEW: YouTube filtering
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        sort_by = request.args.get('sort_by', 'total_score')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Validate parameters
        if limit > 1000:
            limit = 1000
        
        # Build query
        query = db_manager.session.query(Artist)
        
        # Apply filters
        if tier:
            query = query.filter(Artist.lead_tier == tier.upper())
        
        if region:
            query = query.filter(Artist.region == region)
        
        if min_score is not None:
            query = query.filter(Artist.total_score >= min_score)
        
        if max_score is not None:
            query = query.filter(Artist.total_score <= max_score)
        
        # NEW: YouTube filtering
        if youtube_filter:
            if youtube_filter == 'has_channel':
                query = query.filter(Artist.youtube_channel_id.isnot(None))
            elif youtube_filter == 'no_channel':
                query = query.filter(Artist.youtube_channel_id.is_(None))
            elif youtube_filter == 'high_potential':
                query = query.filter(Artist.youtube_growth_potential == 'high_potential')
            elif youtube_filter == 'underperforming':
                # Artists with Spotify following but low YouTube subscribers
                query = query.filter(
                    Artist.monthly_listeners > 10000,
                    Artist.youtube_subscribers < Artist.monthly_listeners * 0.3
                )
            elif youtube_filter == 'active_uploaders':
                query = query.filter(Artist.youtube_upload_frequency.in_(['very_active', 'active']))
        
        # Apply sorting
        if sort_by == 'total_score':
            sort_column = Artist.total_score
        elif sort_by == 'name':
            sort_column = Artist.name
        elif sort_by == 'created_at':
            sort_column = Artist.created_at
        elif sort_by == 'youtube_subscribers':  # NEW: YouTube sorting
            sort_column = Artist.youtube_subscribers
        else:
            sort_column = Artist.total_score
        
        if sort_order.lower() == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination
        leads = query.offset(offset).limit(limit).all()
        
        # Format results including YouTube data
        results = []
        for artist in leads:
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
                'last_release_date': artist.last_release_date.isoformat() if artist.last_release_date else None,
                'outreach_status': artist.outreach_status,
                'contact_email': artist.contact_email,
                'website': artist.website,
                'social_handles': artist.social_handles,
                # NEW: YouTube summary data
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
                'created_at': artist.created_at.isoformat(),
                'updated_at': artist.updated_at.isoformat()
            }
            results.append(result_item)
        
        return jsonify({
            'leads': results,
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            },
            'filters_applied': {
                'tier': tier,
                'region': region,
                'min_score': min_score,
                'max_score': max_score,
                'youtube_filter': youtube_filter,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        })
        
    except Exception as e:
        print(f"Error in get_leads: {e}")
        return jsonify({'error': f'Failed to fetch leads: {str(e)}'}), 500

# Export leads to CSV including YouTube data
@app.route('/api/export', methods=['POST'])
def export_leads():
    """Export filtered leads to CSV including YouTube data"""
    try:
        data = request.get_json() or {}
        filters = data.get('filters', {})
        
        # Get leads with filters (no pagination for export)
        query = db_manager.session.query(Artist)
        
        if filters.get('tier'):
            query = query.filter(Artist.lead_tier == filters['tier'].upper())
        
        if filters.get('region'):
            query = query.filter(Artist.region == filters['region'])
        
        if filters.get('min_score'):
            query = query.filter(Artist.total_score >= filters['min_score'])
        
        if filters.get('max_score'):
            query = query.filter(Artist.total_score <= filters['max_score'])
        
        # NEW: YouTube filtering for export
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
            return jsonify({'error': 'No leads found with current filters'}), 404
        
        # Create CSV content with YouTube data
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header including YouTube columns
        writer.writerow([
            'Artist Name', 'Country', 'Region', 'Genre', 'Total Score',
            'Independence Score', 'Opportunity Score', 'Geographic Score',
            'Lead Tier', 'Monthly Listeners', 'Last Release Date',
            'Outreach Status', 'Contact Email', 'Website', 'Social Handles',
            'YouTube Channel ID', 'YouTube Channel URL', 'YouTube Subscribers', 
            'YouTube Total Views', 'YouTube Video Count', 'YouTube Upload Frequency', 
            'YouTube Growth Potential', 'YouTube Engagement Rate',
            'Created Date'
        ])
        
        # Write data including YouTube metrics
        for artist in leads:
            writer.writerow([
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
                artist.last_release_date.strftime('%Y-%m-%d') if artist.last_release_date else '',
                artist.outreach_status or '',
                artist.contact_email or '',
                artist.website or '',
                str(artist.social_handles) if artist.social_handles else '',
                # NEW: YouTube data columns
                artist.youtube_channel_id or '',
                artist.youtube_channel_url or '',
                artist.youtube_subscribers or 0,
                artist.youtube_total_views or 0,
                artist.youtube_video_count or 0,
                artist.youtube_upload_frequency or '',
                artist.youtube_growth_potential or '',
                artist.youtube_engagement_rate or 0.0,
                artist.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'precise_digital_leads_{timestamp}.csv'
        
        return jsonify({
            'csv_data': csv_content,
            'filename': filename,
            'count': len(leads),
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"Error in export_leads: {e}")
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

# Get artist details including YouTube data
@app.route('/api/artist/<int:artist_id>', methods=['GET'])
def get_artist(artist_id):
    """Get detailed information for a specific artist including YouTube data"""
    try:
        artist = db_manager.session.query(Artist).filter_by(id=artist_id).first()
        
        if not artist:
            return jsonify({'error': 'Artist not found'}), 404
        
        # Get associated tracks
        tracks = db_manager.session.query(Track).filter_by(artist_id=artist_id).all()
        
        # Get contact attempts
        from config.database import ContactAttempt
        contacts = db_manager.session.query(ContactAttempt).filter_by(artist_id=artist_id).all()
        
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
                'last_release_date': artist.last_release_date.isoformat() if artist.last_release_date else None
            },
            # NEW: YouTube metrics
            'youtube_metrics': {
                'channel_id': artist.youtube_channel_id,
                'channel_url': artist.youtube_channel_url,
                'subscribers': artist.youtube_subscribers,
                'total_views': artist.youtube_total_views,
                'video_count': artist.youtube_video_count,
                'upload_frequency': artist.youtube_upload_frequency,
                'engagement_rate': artist.youtube_engagement_rate,
                'growth_potential': artist.youtube_growth_potential,
                'last_upload': artist.youtube_last_upload.isoformat() if artist.youtube_last_upload else None,
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
                'release_date': track.release_date.isoformat() if track.release_date else None,
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
                'created_at': artist.created_at.isoformat(),
                'updated_at': artist.updated_at.isoformat(),
                'last_scraped': artist.last_scraped.isoformat() if artist.last_scraped else None
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in get_artist: {e}")
        return jsonify({'error': f'Failed to fetch artist: {str(e)}'}), 500

# Update outreach status
@app.route('/api/artist/<int:artist_id>/outreach', methods=['PUT'])
def update_outreach_status(artist_id):
    """Update outreach status for an artist"""
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({'error': 'Status required in request body'}), 400
        
        status = data['status']
        valid_statuses = ['not_contacted', 'contacted', 'responded', 'interested', 'not_interested', 'converted']
        
        if status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        
        artist = db_manager.session.query(Artist).filter_by(id=artist_id).first()
        
        if not artist:
            return jsonify({'error': 'Artist not found'}), 404
        
        artist.outreach_status = status
        artist.updated_at = datetime.utcnow()
        
        # Log the outreach attempt if notes provided
        notes = data.get('notes')
        if notes:
            from config.database import OutreachLog
            outreach_log = OutreachLog(
                artist_id=artist_id,
                contact_date=datetime.utcnow(),
                method=data.get('method', 'manual'),
                notes=notes,
                conversion_status=status if status in ['interested', 'not_interested', 'converted'] else 'no_response'
            )
            db_manager.session.add(outreach_log)
        
        db_manager.session.commit()
        
        return jsonify({
            'message': 'Outreach status updated successfully',
            'artist_id': artist_id,
            'new_status': status
        })
        
    except Exception as e:
        db_manager.session.rollback()
        print(f"Error in update_outreach_status: {e}")
        return jsonify({'error': f'Failed to update outreach status: {str(e)}'}), 500

# Dashboard statistics including YouTube metrics
@app.route('/api/dashboard/stats', methods=['GET'])
def dashboard_stats():
    """Get dashboard statistics including YouTube metrics"""
    try:
        stats = db_manager.get_dashboard_stats()
        stats['generated_at'] = datetime.utcnow().isoformat()
        return jsonify(stats)
        
    except Exception as e:
        print(f"Error in dashboard_stats: {e}")
        return jsonify({'error': f'Failed to fetch dashboard stats: {str(e)}'}), 500

# NEW: YouTube-specific endpoints

@app.route('/api/youtube/test', methods=['POST'])
def test_youtube_integration():
    """Test YouTube API integration for a specific artist"""
    try:
        data = request.get_json()
        artist_name = data.get('artist_name')
        
        if not artist_name:
            return jsonify({'error': 'Artist name required'}), 400
        
        from src.integrations.youtube import youtube_client
        
        # Test channel search
        channel_data = youtube_client.search_artist_channel(artist_name)
        
        if not channel_data:
            return jsonify({
                'status': 'not_found',
                'message': f'No YouTube channel found for "{artist_name}"',
                'artist_name': artist_name
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
            'integration_status': 'YouTube API working correctly'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'message': 'YouTube API integration test failed'
        }), 500

@app.route('/api/youtube/opportunities', methods=['GET'])
def get_youtube_opportunities():
    """Get artists with YouTube opportunities for targeted outreach"""
    try:
        limit = request.args.get('limit', 20, type=int)
        opportunities = db_manager.get_youtube_opportunities(limit=limit)
        
        return jsonify({
            'youtube_opportunities': opportunities,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"Error in get_youtube_opportunities: {e}")
        return jsonify({'error': f'Failed to fetch YouTube opportunities: {str(e)}'}), 500

@app.route('/api/artist/<int:artist_id>/youtube/refresh', methods=['POST'])
def refresh_artist_youtube_data(artist_id):
    """Refresh YouTube data for a specific artist"""
    try:
        artist = db_manager.session.query(Artist).filter_by(id=artist_id).first()
        if not artist:
            return jsonify({'error': 'Artist not found'}), 404
        
        from src.integrations.youtube import youtube_client
        
        # Get fresh YouTube data
        channel_data = youtube_client.search_artist_channel(artist.name)
        
        if not channel_data:
            return jsonify({
                'status': 'no_channel_found',
                'message': f'No YouTube channel found for "{artist.name}"'
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
        success = db_manager.update_youtube_data(artist_id, youtube_update_data)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'YouTube data refreshed successfully',
                'updated_data': youtube_update_data
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to update YouTube data in database'
            }), 500
            
    except Exception as e:
        print(f"Error in refresh_artist_youtube_data: {e}")
        return jsonify({'error': f'Failed to refresh YouTube data: {str(e)}'}), 500

@app.route('/api/youtube/stats', methods=['GET'])
def get_youtube_stats():
    """Get overall YouTube integration statistics"""
    try:
        stats = db_manager.get_dashboard_stats()
        youtube_stats = stats.get('youtube_statistics', {})
        
        # Calculate additional YouTube metrics
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
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"Error in get_youtube_stats: {e}")
        return jsonify({'error': f'Failed to fetch YouTube stats: {str(e)}'}), 500

if __name__ == '__main__':
    # Initialize database
    from config.database import init_db, run_youtube_migration_if_needed
    init_db()
    run_youtube_migration_if_needed()
    
    # Run the app
    app.run(
        host=settings.app.host,
        port=settings.app.port,
        debug=settings.app.debug
    )