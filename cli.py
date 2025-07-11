# cli.py - Command Line Interface with YouTube Integration
"""
Command Line Interface for Precise Digital Lead Generation Tool with YouTube Integration
Provides admin tools and testing capabilities including YouTube-specific commands
"""
import click
import csv
import json
from datetime import datetime, timedelta
from tabulate import tabulate

from src.core.pipeline import LeadAggregationPipeline
from src.core.rate_limiter import rate_limiter
from src.core.scoring import LeadScoringEngine
from config.database import DatabaseManager, Artist, Track, init_db, reset_db, migrate_youtube_fields
from src.services.contact_discovery import ContactDiscoveryService
from config.settings import settings

@click.group()
def cli():
    """Precise Digital Lead Generation Tool CLI with YouTube Integration"""
    pass

@cli.command()
def init():
    """Initialize the database"""
    try:
        init_db()
        click.echo("✅ Database initialized successfully!")
        
        # Check if YouTube migration is needed
        from config.database import check_youtube_migration_needed
        if check_youtube_migration_needed():
            click.echo("🎥 YouTube fields not found, running migration...")
            migrate_youtube_fields()
        else:
            click.echo("🎥 YouTube integration already configured!")
            
    except Exception as e:
        click.echo(f"❌ Database initialization failed: {e}")

@cli.command()
@click.confirmation_option(prompt='Are you sure you want to reset the database? This will delete all data.')
def reset():
    """Reset the database (WARNING: Deletes all data)"""
    try:
        reset_db()
        click.echo("✅ Database reset successfully!")
        # YouTube fields will be included in the reset
        click.echo("🎥 YouTube integration included in reset")
    except Exception as e:
        click.echo(f"❌ Database reset failed: {e}")

@cli.command()
@click.argument('isrc')
@click.option('--save/--no-save', default=True, help='Save results to database')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--include-youtube/--no-youtube', default=True, help='Include YouTube data collection')
def analyze(isrc, save, verbose, include_youtube):
    """Analyze a single ISRC with optional YouTube integration"""
    pipeline = LeadAggregationPipeline(rate_limiter)
    
    click.echo(f"🔍 Analyzing ISRC: {isrc}")
    if not include_youtube:
        click.echo("⚠️  YouTube integration disabled for this analysis")
    
    try:
        # Temporarily disable YouTube if requested
        original_method = None
        if not include_youtube:
            original_method = pipeline._get_youtube_data
            pipeline._get_youtube_data = lambda x: None
        
        result = pipeline.process_isrc(isrc, save_to_db=save)
        
        if result['status'] == 'completed':
            click.echo("✅ Analysis completed successfully!")
            
            # Display basic info
            artist_name = result['artist_data'].get('name', 'Unknown')
            track_title = result['track_data'].get('title', 'Unknown')
            
            click.echo(f"\n🎵 Artist: {artist_name}")
            click.echo(f"🎧 Track: {track_title}")
            
            # Display scores
            scores = result['scores']
            click.echo(f"\n📊 Lead Score: {scores['total_score']} (Tier {scores['tier']})")
            click.echo(f"   Independence: {scores['independence_score']}/100")
            click.echo(f"   Opportunity: {scores['opportunity_score']}/100")
            click.echo(f"   Geographic: {scores['geographic_score']}/100")
            click.echo(f"   Confidence: {scores['confidence']}%")
            
            # Display data sources
            sources = result.get('data_sources_used', [])
            click.echo(f"\n📡 Data Sources: {', '.join(sources)}")
            
            # NEW: Display YouTube data if available
            if 'youtube' in sources:
                youtube_data = result.get('youtube_data', {})
                if youtube_data.get('channel'):
                    channel = youtube_data['channel']
                    click.echo(f"\n🎥 YouTube Channel Found:")
                    click.echo(f"   Channel: {channel.get('title', 'N/A')}")
                    click.echo(f"   Subscribers: {channel.get('statistics', {}).get('subscriber_count', 'N/A'):,}")
                    click.echo(f"   Total Views: {channel.get('statistics', {}).get('view_count', 'N/A'):,}")
                    click.echo(f"   Videos: {channel.get('statistics', {}).get('video_count', 'N/A')}")
                    
                    if youtube_data.get('analytics'):
                        analytics = youtube_data['analytics']
                        click.echo(f"   Upload Frequency: {analytics.get('recent_activity', {}).get('upload_frequency', 'unknown')}")
                        click.echo(f"   Growth Potential: {analytics.get('growth_potential', 'unknown')}")
            elif include_youtube:
                click.echo("\n🎥 No YouTube channel found for this artist")
            
            # Verbose output
            if verbose:
                click.echo(f"\n📝 Raw Data:")
                click.echo(json.dumps(result, indent=2, default=str))
        
        else:
            click.echo("❌ Analysis failed!")
            for error in result.get('errors', []):
                click.echo(f"   Error: {error}")
        
        # Restore original method if it was disabled
        if not include_youtube and original_method:
            pipeline._get_youtube_data = original_method
                
    except Exception as e:
        click.echo(f"❌ Analysis failed: {e}")

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--batch-size', default=10, help='Batch size for processing')
@click.option('--delay', default=1, help='Delay between batches (seconds)')
@click.option('--include-youtube/--no-youtube', default=True, help='Include YouTube data collection')
def bulk(file_path, batch_size, delay, include_youtube):
    """Analyze ISRCs from CSV/TXT file with YouTube integration"""
    pipeline = LeadAggregationPipeline(rate_limiter)
    
    # Read ISRCs from file
    isrcs = []
    try:
        with open(file_path, 'r') as f:
            if file_path.endswith('.csv'):
                reader = csv.reader(f)
                for row in reader:
                    for cell in row:
                        if len(cell.strip()) == 12 and cell.strip().isalnum():
                            isrcs.append(cell.strip().upper())
                            break
            else:
                for line in f:
                    line = line.strip().upper()
                    if len(line) == 12 and line.isalnum():
                        isrcs.append(line)
    except Exception as e:
        click.echo(f"❌ Failed to read file: {e}")
        return
    
    if not isrcs:
        click.echo("❌ No valid ISRCs found in file")
        return
    
    click.echo(f"📁 Found {len(isrcs)} ISRCs to process")
    if not include_youtube:
        click.echo("⚠️  YouTube integration disabled for bulk processing")
    
    # Temporarily disable YouTube if requested
    original_method = None
    if not include_youtube:
        original_method = pipeline._get_youtube_data
        pipeline._get_youtube_data = lambda x: None
    
    # Process in batches
    with click.progressbar(length=len(isrcs), label='Processing ISRCs') as bar:
        result = pipeline.process_bulk(isrcs, batch_size=batch_size)
        bar.update(len(isrcs))
    
    # Restore original method if it was disabled
    if not include_youtube and original_method:
        pipeline._get_youtube_data = original_method
    
    # Display summary
    click.echo(f"\n📊 Processing Summary:")
    click.echo(f"   Total processed: {result['total_processed']}")
    click.echo(f"   Successful: {result['successful']}")
    click.echo(f"   Failed: {result['failed']}")
    click.echo(f"   Success rate: {result['success_rate']:.1f}%")
    click.echo(f"   Total time: {result['total_time']}s")
    
    # NEW: YouTube statistics if enabled
    if include_youtube and 'youtube_statistics' in result:
        youtube_stats = result['youtube_statistics']
        click.echo(f"\n🎥 YouTube Statistics:")
        click.echo(f"   Artists with YouTube: {youtube_stats['artists_with_youtube']}")
        click.echo(f"   YouTube data collected: {youtube_stats['youtube_data_collected']}")
        click.echo(f"   Total subscribers: {youtube_stats['total_youtube_subscribers']:,}")

@cli.command()
@click.option('--tier', help='Filter by lead tier (A, B, C, D)')
@click.option('--region', help='Filter by region')
@click.option('--min-score', type=int, help='Minimum score')
@click.option('--youtube-filter', help='YouTube filter: has_channel, no_channel, high_potential, underperforming')
@click.option('--limit', default=20, help='Number of results to show')
@click.option('--export', help='Export to CSV file')
def leads(tier, region, min_score, youtube_filter, limit, export):
    """List and filter leads with YouTube filtering options"""
    db_manager = DatabaseManager()
    
    try:
        # Get leads with YouTube filtering
        leads = db_manager.get_leads(
            tier=tier, 
            region=region, 
            youtube_filter=youtube_filter,
            limit=limit
        )
        
        if not leads:
            click.echo("No leads found matching criteria")
            return
        
        # Prepare table data including YouTube info
        table_data = []
        for artist in leads:
            youtube_info = "No Channel"
            if artist.youtube_channel_id:
                subs = artist.youtube_subscribers or 0
                potential = artist.youtube_growth_potential or "unknown"
                youtube_info = f"{subs:,} subs ({potential})"
            
            table_data.append([
                artist.name,
                artist.country or 'Unknown',
                artist.lead_tier,
                f"{artist.total_score:.1f}",
                artist.monthly_listeners or 0,
                youtube_info,
                artist.outreach_status or 'not_contacted',
                artist.contact_email or 'No email'
            ])
        
        # Display table
        headers = ['Artist', 'Country', 'Tier', 'Score', 'Listeners', 'YouTube', 'Status', 'Email']
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        # Export if requested
        if export:
            with open(export, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(table_data)
            click.echo(f"📁 Exported {len(leads)} leads to {export}")
            
    except Exception as e:
        click.echo(f"❌ Failed to fetch leads: {e}")

@cli.command()
def stats():
    """Show database statistics including YouTube metrics"""
    db_manager = DatabaseManager()
    
    try:
        # Get basic counts
        total_artists = db_manager.session.query(Artist).count()
        total_tracks = db_manager.session.query(Track).count()
        
        # Get tier distribution
        tier_stats = {}
        for tier in ['A', 'B', 'C', 'D']:
            count = db_manager.session.query(Artist).filter_by(lead_tier=tier).count()
            tier_stats[tier] = count
        
        # Get region distribution
        from sqlalchemy import func
        region_query = db_manager.session.query(
            Artist.region, func.count(Artist.id)
        ).group_by(Artist.region).all()
        
        # Get recent activity
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_artists = db_manager.session.query(Artist).filter(
            Artist.created_at >= week_ago
        ).count()
        
        # NEW: YouTube statistics
        youtube_artists = db_manager.session.query(Artist).filter(
            Artist.youtube_channel_id.isnot(None)
        ).count()
        
        total_youtube_subs = db_manager.session.query(
            func.sum(Artist.youtube_subscribers)
        ).scalar() or 0
        
        avg_youtube_subs = db_manager.session.query(
            func.avg(Artist.youtube_subscribers)
        ).filter(Artist.youtube_subscribers > 0).scalar() or 0
        
        high_potential = db_manager.session.query(Artist).filter_by(
            youtube_growth_potential='high_potential'
        ).count()
        
        # Display stats
        click.echo("📊 Database Statistics")
        click.echo("=" * 30)
        click.echo(f"Total Artists: {total_artists}")
        click.echo(f"Total Tracks: {total_tracks}")
        click.echo(f"Added This Week: {recent_artists}")
        
        click.echo(f"\n🏆 Lead Tiers:")
        for tier, count in tier_stats.items():
            percentage = (count / max(total_artists, 1)) * 100
            click.echo(f"   Tier {tier}: {count} ({percentage:.1f}%)")
        
        click.echo(f"\n🌍 Regions:")
        for region, count in region_query:
            if region:
                percentage = (count / max(total_artists, 1)) * 100
                click.echo(f"   {region.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
        
        # NEW: YouTube statistics
        click.echo(f"\n🎥 YouTube Integration:")
        youtube_coverage = (youtube_artists / max(total_artists, 1)) * 100
        click.echo(f"   Artists with YouTube: {youtube_artists} ({youtube_coverage:.1f}%)")
        click.echo(f"   Total Subscribers: {total_youtube_subs:,}")
        click.echo(f"   Average Subscribers: {avg_youtube_subs:,.0f}")
        click.echo(f"   High Potential Channels: {high_potential}")
                
    except Exception as e:
        click.echo(f"❌ Failed to fetch statistics: {e}")

@cli.command()
def status():
    """Show system status including YouTube API and rate limits"""
    click.echo("🔧 System Status")
    click.echo("=" * 30)
    
    # API rate limits
    rate_status = rate_limiter.get_rate_limit_status()
    
    for api, status in rate_status.items():
        api_icon = "🎥" if api == "youtube" else "📡"
        click.echo(f"\n{api_icon} {api.title()} API:")
        click.echo(f"   Requests this minute: {status['requests_this_minute']}/{status['minute_limit']}")
        if status.get('daily_limit'):
            click.echo(f"   Requests today: {status['requests_today']}/{status['daily_limit']}")
        
        # Special handling for YouTube
        if api == 'youtube':
            api_key = settings.apis['youtube'].api_key
            if api_key:
                click.echo(f"   API Key: Configured (...{api_key[-4:]})")
            else:
                click.echo(f"   API Key: ❌ Not configured")
    
    # Database status
    try:
        db_manager = DatabaseManager()
        artist_count = db_manager.session.query(Artist).count()
        click.echo(f"\n💾 Database: Connected ({artist_count} artists)")
        
        # Check YouTube migration status
        from config.database import check_youtube_migration_needed
        if check_youtube_migration_needed():
            click.echo(f"⚠️  YouTube migration needed - run: precise-digital migrate-youtube")
        else:
            click.echo(f"✅ YouTube schema up to date")
    except Exception as e:
        click.echo(f"\n💾 Database: Error - {e}")

@cli.command()
@click.argument('artist_id', type=int)
def contacts(artist_id):
    """Discover contacts for a specific artist including YouTube"""
    db_manager = DatabaseManager()
    contact_service = ContactDiscoveryService()
    
    try:
        artist = db_manager.session.query(Artist).filter_by(id=artist_id).first()
        if not artist:
            click.echo(f"❌ Artist with ID {artist_id} not found")
            return
        
        click.echo(f"🔍 Discovering contacts for: {artist.name}")
        
        # Prepare artist data including YouTube info
        artist_data = {
            'name': artist.name,
            'website': artist.website,
            'social_handles': artist.social_handles or {},
            'musicbrainz_data': {
                'artist': {
                    'urls': {}  # Would need to fetch from MB again
                }
            },
            'spotify_data': {
                'external_urls': {}  # Would need to fetch from Spotify again
            },
            # NEW: Include YouTube data
            'youtube_data': {}
        }
        
        # Add YouTube data if available
        if artist.youtube_channel_id:
            artist_data['youtube_data'] = {
                'channel': {
                    'channel_id': artist.youtube_channel_id,
                    'title': f"{artist.name} (from DB)",
                    'statistics': {
                        'subscriber_count': artist.youtube_subscribers or 0
                    }
                }
            }
        
        contacts = contact_service.discover_contacts(artist_data)
        
        if contacts:
            click.echo(f"\n📞 Found {len(contacts)} contact methods:")
            
            table_data = []
            for contact in contacts:
                platform_icon = "🎥" if contact.get('platform') == 'youtube' else "📱"
                table_data.append([
                    platform_icon + " " + contact['type'].title(),
                    contact.get('platform', '').title(),
                    contact['value'],
                    f"{contact['confidence']}%",
                    contact['source']
                ])
            
            headers = ['Type', 'Platform', 'Value', 'Confidence', 'Source']
            click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        else:
            click.echo("❌ No contacts found")
            
    except Exception as e:
        click.echo(f"❌ Contact discovery failed: {e}")

# NEW: YouTube-specific commands

@cli.command()
@click.argument('artist_name')
def test_youtube(artist_name):
    """Test YouTube API integration for a specific artist"""
    from src.integrations.youtube import youtube_client
    
    click.echo(f"🎥 Testing YouTube integration for: {artist_name}")
    click.echo("=" * 50)
    
    try:
        # Test 1: Channel search
        click.echo("1. Searching for artist channel...")
        channel_data = youtube_client.search_artist_channel(artist_name)
        
        if not channel_data:
            click.echo("❌ No YouTube channel found")
            return
        
        click.echo(f"✅ Found channel: {channel_data['title']}")
        click.echo(f"   Channel ID: {channel_data['channel_id']}")
        click.echo(f"   Subscribers: {channel_data.get('statistics', {}).get('subscriber_count', 'N/A'):,}")
        click.echo(f"   Total Views: {channel_data.get('statistics', {}).get('view_count', 'N/A'):,}")
        
        # Test 2: Channel analytics
        click.echo("\n2. Getting channel analytics...")
        analytics = youtube_client.get_channel_analytics(channel_data['channel_id'])
        
        if analytics:
            click.echo(f"✅ Analytics retrieved:")
            click.echo(f"   Upload Frequency: {analytics.get('recent_activity', {}).get('upload_frequency', 'unknown')}")
            click.echo(f"   Growth Potential: {analytics.get('growth_potential', 'unknown')}")
            click.echo(f"   Videos (30 days): {analytics.get('recent_activity', {}).get('videos_last_30_days', 0)}")
        else:
            click.echo("⚠️ Could not retrieve detailed analytics")
        
        # Test 3: Video search
        click.echo("\n3. Searching for artist videos...")
        videos = youtube_client.search_artist_videos(artist_name, max_results=5)
        
        if videos:
            click.echo(f"✅ Found {len(videos)} videos:")
            for i, video in enumerate(videos[:3], 1):
                title = video.get('title', 'Unknown')[:50]
                views = video.get('statistics', {}).get('view_count', 0)
                click.echo(f"   {i}. {title}... ({views:,} views)")
        else:
            click.echo("⚠️ No videos found")
        
        click.echo(f"\n🎉 YouTube integration test completed successfully!")
        
    except Exception as e:
        click.echo(f"❌ YouTube integration test failed: {e}")

@cli.command()
def youtube_status():
    """Check YouTube API configuration and status"""
    from src.integrations.youtube import youtube_client
    from config.settings import settings
    
    click.echo("🎥 YouTube Integration Status")
    click.echo("=" * 40)
    
    # Check API key configuration
    api_key = settings.apis['youtube'].api_key
    if api_key:
        click.echo(f"✅ API Key: Configured (...{api_key[-4:]})")
    else:
        click.echo("❌ API Key: Not configured")
        click.echo("   Set YOUTUBE_API_KEY environment variable")
        return
    
    # Check rate limits
    rate_status = rate_limiter.get_rate_limit_status()
    youtube_status = rate_status.get('youtube', {})
    
    click.echo(f"\n📊 Rate Limits:")
    click.echo(f"   Requests this minute: {youtube_status.get('requests_this_minute', 0)}/{youtube_status.get('minute_limit', 100)}")
    click.echo(f"   Requests today: {youtube_status.get('requests_today', 0)}/{youtube_status.get('daily_limit', 10000)}")
    
    # Test basic API connectivity
    click.echo(f"\n🔧 API Connectivity Test:")
    try:
        # Try a simple search to test connectivity
        test_result = youtube_client.search_artist_channel("test artist")
        click.echo("✅ YouTube API is accessible")
    except Exception as e:
        click.echo(f"❌ YouTube API test failed: {e}")

@cli.command()
def migrate_youtube():
    """Run database migration to add YouTube fields"""
    click.echo("🔄 Running YouTube schema migration...")
    
    try:
        migrate_youtube_fields()
        click.echo("✅ YouTube schema migration completed")
    except Exception as e:
        click.echo(f"❌ Migration failed: {e}")

@cli.command()
@click.argument('artist_id', type=int)
def refresh_youtube_data(artist_id):
    """Refresh YouTube data for a specific artist"""
    db_manager = DatabaseManager()
    
    try:
        artist = db_manager.session.query(Artist).filter_by(id=artist_id).first()
        if not artist:
            click.echo(f"❌ Artist with ID {artist_id} not found")
            return
        
        click.echo(f"🔄 Refreshing YouTube data for: {artist.name}")
        
        from src.integrations.youtube import youtube_client
        
        # Get fresh YouTube data
        channel_data = youtube_client.search_artist_channel(artist.name)
        
        if channel_data:
            # Prepare update data
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
                        'growth_potential': analytics.get('growth_potential')
                    })
            
            # Update database
            success = db_manager.update_youtube_data(artist_id, youtube_update_data)
            
            if success:
                click.echo(f"✅ YouTube data updated:")
                click.echo(f"   Channel: {channel_data.get('title')}")
                click.echo(f"   Subscribers: {youtube_update_data['subscribers']:,}")
                click.echo(f"   Total Views: {youtube_update_data['total_views']:,}")
            else:
                click.echo("❌ Failed to update database")
        else:
            click.echo("❌ No YouTube channel found for this artist")
            
    except Exception as e:
        click.echo(f"❌ Failed to refresh YouTube data: {e}")

@cli.command()
@click.option('--limit', default=10, help='Number of opportunities to show')
def youtube_opportunities(limit):
    """Show artists with YouTube opportunities"""
    db_manager = DatabaseManager()
    
    try:
        opportunities = db_manager.get_youtube_opportunities(limit=limit)
        
        # Show artists with no YouTube presence
        no_youtube = opportunities.get('no_youtube_presence', [])
        if no_youtube:
            click.echo("🎥 Artists with NO YouTube presence but good Spotify following:")
            click.echo("=" * 60)
            
            table_data = []
            for artist in no_youtube:
                table_data.append([
                    artist.name,
                    artist.country or 'Unknown',
                    f"{artist.monthly_listeners:,}" if artist.monthly_listeners else '0',
                    artist.lead_tier,
                    f"{artist.total_score:.1f}"
                ])
            
            headers = ['Artist', 'Country', 'Spotify Followers', 'Tier', 'Score']
            click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        # Show artists with underperforming YouTube
        underperforming = opportunities.get('underperforming_youtube', [])
        if underperforming:
            click.echo("\n🎥 Artists with UNDERPERFORMING YouTube channels:")
            click.echo("=" * 60)
            
            table_data = []
            for artist in underperforming:
                youtube_ratio = (artist.youtube_subscribers / max(artist.monthly_listeners, 1)) * 100
                table_data.append([
                    artist.name,
                    f"{artist.monthly_listeners:,}" if artist.monthly_listeners else '0',
                    f"{artist.youtube_subscribers:,}" if artist.youtube_subscribers else '0',
                    f"{youtube_ratio:.1f}%",
                    artist.lead_tier
                ])
            
            headers = ['Artist', 'Spotify Followers', 'YouTube Subs', 'YT/Spotify %', 'Tier']
            click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        if not no_youtube and not underperforming:
            click.echo("✅ No significant YouTube opportunities found")
            
    except Exception as e:
        click.echo(f"❌ Failed to fetch YouTube opportunities: {e}")

@cli.command()
@click.argument('artist_name')
def test_scoring(artist_name):
    """Test scoring algorithm with sample data including YouTube scenarios"""
    scoring_engine = LeadScoringEngine()
    
    # Create test scenarios with YouTube integration
    scenarios = [
        {
            'name': 'Self-Released NZ Artist with No YouTube',
            'data': {
                'track_data': {'label': 'Self-Released'},
                'spotify_data': {'followers': 25000, 'popularity': 40},
                'musicbrainz_data': {'artist': {'country': 'NZ'}},
                'youtube_data': {}  # No YouTube presence
            }
        },
        {
            'name': 'Self-Released NZ Artist with Underperforming YouTube',
            'data': {
                'track_data': {'label': 'Self-Released'},
                'spotify_data': {'followers': 25000, 'popularity': 40},
                'musicbrainz_data': {'artist': {'country': 'NZ'}},
                'youtube_data': {
                    'channel': {'statistics': {'subscriber_count': 3000}},  # Much lower than Spotify
                    'analytics': {'recent_activity': {'upload_frequency': 'low'}}
                }
            }
        },
        {
            'name': 'Self-Released NZ Artist with Optimized YouTube',
            'data': {
                'track_data': {'label': 'Self-Released'},
                'spotify_data': {'followers': 25000, 'popularity': 40},
                'musicbrainz_data': {'artist': {'country': 'NZ'}},
                'youtube_data': {
                    'channel': {'statistics': {'subscriber_count': 20000}},
                    'analytics': {
                        'recent_activity': {'upload_frequency': 'active'},
                        'growth_potential': 'moderate_potential'
                    }
                }
            }
        }
    ]
    
    click.echo(f"🧪 Testing Scoring Algorithm with YouTube Integration")
    click.echo("=" * 60)
    
    for scenario in scenarios:
        scores = scoring_engine.calculate_scores(scenario['data'])
        
        click.echo(f"\n📊 {scenario['name']}:")
        click.echo(f"   Total Score: {scores['total_score']} (Tier {scores['tier']})")
        click.echo(f"   Independence: {scores['independence_score']}")
        click.echo(f"   Opportunity: {scores['opportunity_score']} (includes YouTube assessment)")
        click.echo(f"   Geographic: {scores['geographic_score']}")
        click.echo(f"   Confidence: {scores['confidence']}%")
        
        # Show YouTube-specific factors
        opportunity_factors = scores['scoring_breakdown']['opportunity']['factors']
        youtube_factors = [f for f in opportunity_factors if 'youtube' in f.lower()]
        if youtube_factors:
            click.echo(f"   🎥 YouTube Factors: {', '.join(youtube_factors)}")

@cli.command()
def serve():
    """Start the web server with YouTube integration"""
    click.echo("🚀 Starting Precise Digital Lead Generation Tool with YouTube integration...")
    
    # Check YouTube configuration
    if settings.apis['youtube'].api_key:
        click.echo("🎥 YouTube integration: ENABLED")
    else:
        click.echo("⚠️  YouTube integration: DISABLED (no API key)")
    
    # Import and run the Flask app
    from run import main
    main()

if __name__ == '__main__':
    cli()