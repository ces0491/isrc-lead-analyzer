# cli.py - Command Line Interface
"""
Command Line Interface for Precise Digital Lead Generation Tool
Provides admin tools and testing capabilities
"""
import click
import csv
import json
from datetime import datetime, timedelta
from tabulate import tabulate

from src.core.pipeline import LeadAggregationPipeline
from src.core.rate_limiter import rate_limiter
from src.core.scoring import LeadScoringEngine
from config.database import DatabaseManager, Artist, Track, init_db, reset_db
from src.services.contact_discovery import ContactDiscoveryService
from config.settings import settings

@click.group()
def cli():
    """Precise Digital Lead Generation Tool CLI"""
    pass

@cli.command()
def init():
    """Initialize the database"""
    try:
        init_db()
        click.echo("✅ Database initialized successfully!")
    except Exception as e:
        click.echo(f"❌ Database initialization failed: {e}")

@cli.command()
@click.confirmation_option(prompt='Are you sure you want to reset the database? This will delete all data.')
def reset():
    """Reset the database (WARNING: Deletes all data)"""
    try:
        reset_db()
        click.echo("✅ Database reset successfully!")
    except Exception as e:
        click.echo(f"❌ Database reset failed: {e}")

@cli.command()
@click.argument('isrc')
@click.option('--save/--no-save', default=True, help='Save results to database')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def analyze(isrc, save, verbose):
    """Analyze a single ISRC"""
    pipeline = LeadAggregationPipeline(rate_limiter)
    
    click.echo(f"🔍 Analyzing ISRC: {isrc}")
    
    try:
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
            
            # Verbose output
            if verbose:
                click.echo(f"\n📝 Raw Data:")
                click.echo(json.dumps(result, indent=2, default=str))
                
        else:
            click.echo("❌ Analysis failed!")
            for error in result.get('errors', []):
                click.echo(f"   Error: {error}")
                
    except Exception as e:
        click.echo(f"❌ Analysis failed: {e}")

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--batch-size', default=10, help='Batch size for processing')
@click.option('--delay', default=1, help='Delay between batches (seconds)')
def bulk(file_path, batch_size, delay):
    """Analyze ISRCs from CSV/TXT file"""
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
    
    # Process in batches
    with click.progressbar(length=len(isrcs), label='Processing ISRCs') as bar:
        result = pipeline.process_bulk(isrcs, batch_size=batch_size)
        bar.update(len(isrcs))
    
    # Display summary
    click.echo(f"\n📊 Processing Summary:")
    click.echo(f"   Total processed: {result['total_processed']}")
    click.echo(f"   Successful: {result['successful']}")
    click.echo(f"   Failed: {result['failed']}")
    click.echo(f"   Success rate: {result['success_rate']:.1f}%")
    click.echo(f"   Total time: {result['total_time']}s")

@cli.command()
@click.option('--tier', help='Filter by lead tier (A, B, C, D)')
@click.option('--region', help='Filter by region')
@click.option('--min-score', type=int, help='Minimum score')
@click.option('--limit', default=20, help='Number of results to show')
@click.option('--export', help='Export to CSV file')
def leads(tier, region, min_score, limit, export):
    """List and filter leads"""
    db_manager = DatabaseManager()
    
    try:
        # Build query
        query = db_manager.session.query(Artist)
        
        if tier:
            query = query.filter(Artist.lead_tier == tier.upper())
        if region:
            query = query.filter(Artist.region == region)
        if min_score:
            query = query.filter(Artist.total_score >= min_score)
        
        # Get results
        artists = query.order_by(Artist.total_score.desc()).limit(limit).all()
        
        if not artists:
            click.echo("No leads found matching criteria")
            return
        
        # Prepare table data
        table_data = []
        for artist in artists:
            table_data.append([
                artist.name,
                artist.country or 'Unknown',
                artist.lead_tier,
                f"{artist.total_score:.1f}",
                artist.monthly_listeners or 0,
                artist.outreach_status or 'not_contacted',
                artist.contact_email or 'No email'
            ])
        
        # Display table
        headers = ['Artist', 'Country', 'Tier', 'Score', 'Listeners', 'Status', 'Email']
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        # Export if requested
        if export:
            with open(export, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(table_data)
            click.echo(f"📁 Exported {len(artists)} leads to {export}")
            
    except Exception as e:
        click.echo(f"❌ Failed to fetch leads: {e}")

@cli.command()
def stats():
    """Show database statistics"""
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
                
    except Exception as e:
        click.echo(f"❌ Failed to fetch statistics: {e}")

@cli.command()
def status():
    """Show system status and API rate limits"""
    click.echo("🔧 System Status")
    click.echo("=" * 30)
    
    # API rate limits
    rate_status = rate_limiter.get_rate_limit_status()
    
    for api, status in rate_status.items():
        click.echo(f"\n📡 {api.title()} API:")
        click.echo(f"   Requests this minute: {status['requests_this_minute']}/{status['minute_limit']}")
        if status['daily_limit']:
            click.echo(f"   Requests today: {status['requests_today']}/{status['daily_limit']}")
    
    # Database status
    try:
        db_manager = DatabaseManager()
        artist_count = db_manager.session.query(Artist).count()
        click.echo(f"\n💾 Database: Connected ({artist_count} artists)")
    except Exception as e:
        click.echo(f"\n💾 Database: Error - {e}")

@cli.command()
@click.argument('artist_id', type=int)
def contacts(artist_id):
    """Discover contacts for a specific artist"""
    db_manager = DatabaseManager()
    contact_service = ContactDiscoveryService()
    
    try:
        artist = db_manager.session.query(Artist).filter_by(id=artist_id).first()
        if not artist:
            click.echo(f"❌ Artist with ID {artist_id} not found")
            return
        
        click.echo(f"🔍 Discovering contacts for: {artist.name}")
        
        # Prepare artist data
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
            }
        }
        
        contacts = contact_service.discover_contacts(artist_data)
        
        if contacts:
            click.echo(f"\n📞 Found {len(contacts)} contact methods:")
            
            table_data = []
            for contact in contacts:
                table_data.append([
                    contact['type'].title(),
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

@cli.command()
@click.argument('artist_name')
def test_scoring(artist_name):
    """Test scoring algorithm with sample data"""
    scoring_engine = LeadScoringEngine()
    
    # Create test scenarios
    scenarios = [
        {
            'name': 'Self-Released NZ Artist',
            'data': {
                'track_data': {'label': 'Self-Released'},
                'spotify_data': {'followers': 25000, 'popularity': 40},
                'musicbrainz_data': {'artist': {'country': 'NZ'}}
            }
        },
        {
            'name': 'Indie Label AU Artist',
            'data': {
                'track_data': {'label': 'Small Indie Records'},
                'spotify_data': {'followers': 15000, 'popularity': 35},
                'musicbrainz_data': {'artist': {'country': 'AU'}}
            }
        },
        {
            'name': 'Major Label US Artist',
            'data': {
                'track_data': {'label': 'Universal Music Group'},
                'spotify_data': {'followers': 100000, 'popularity': 60},
                'musicbrainz_data': {'artist': {'country': 'US'}}
            }
        }
    ]
    
    click.echo(f"🧪 Testing Scoring Algorithm")
    click.echo("=" * 40)
    
    for scenario in scenarios:
        scores = scoring_engine.calculate_scores(scenario['data'])
        
        click.echo(f"\n📊 {scenario['name']}:")
        click.echo(f"   Total Score: {scores['total_score']} (Tier {scores['tier']})")
        click.echo(f"   Independence: {scores['independence_score']}")
        click.echo(f"   Opportunity: {scores['opportunity_score']}")
        click.echo(f"   Geographic: {scores['geographic_score']}")
        click.echo(f"   Confidence: {scores['confidence']}%")

@cli.command()
def serve():
    """Start the web server"""
    click.echo("🚀 Starting Precise Digital Lead Generation Tool...")
    
    # Import and run the Flask app
    from run import main
    main()

if __name__ == '__main__':
    cli()