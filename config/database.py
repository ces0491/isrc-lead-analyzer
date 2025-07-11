"""
Database configuration and models for Precise Digital Lead Generation Tool with YouTube Integration
COMPLETE VERSION - Includes all YouTube fields and migration support
"""
import os
from datetime import datetime
from typing import Optional, Dict, List, Any, Union, cast
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.types import JSON
from config.settings import settings

# Database setup
engine = create_engine(settings.database.url, echo=settings.database.echo)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Artist(Base):
    """Artist model with complete YouTube integration"""
    __tablename__ = "artists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    musicbrainz_id = Column(String(100), unique=True, index=True)
    spotify_id = Column(String(100), unique=True, index=True)
    country = Column(String(50))
    region = Column(String(100))
    genre = Column(String(100))
    subgenre = Column(String(100))
    independence_score = Column(Integer, default=0)
    opportunity_score = Column(Integer, default=0)
    geographic_score = Column(Integer, default=0)
    total_score = Column(Float, default=0.0)
    lead_tier = Column(String(1))
    contact_email = Column(String(255))
    website = Column(String(500))
    social_handles = Column(JSON)
    management_contact = Column(String(255))
    monthly_listeners = Column(Integer, default=0)
    follower_count = Column(Integer, default=0)
    release_count = Column(Integer, default=0)
    last_release_date = Column(DateTime)
    
    # NEW: YouTube-specific fields
    youtube_channel_id = Column(String(100))
    youtube_channel_url = Column(String(500))
    youtube_subscribers = Column(Integer, default=0)
    youtube_total_views = Column(Integer, default=0)
    youtube_video_count = Column(Integer, default=0)
    youtube_upload_frequency = Column(String(20))  # 'very_active', 'active', 'moderate', 'low', 'inactive'
    youtube_engagement_rate = Column(Float, default=0.0)
    youtube_growth_potential = Column(String(20))  # 'high_potential', 'moderate_potential', 'low_potential'
    youtube_last_upload = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped = Column(DateTime)
    outreach_status = Column(String(50), default='not_contacted')
    
    tracks = relationship("Track", back_populates="artist")
    contacts = relationship("ContactAttempt", back_populates="artist")
    outreach_logs = relationship("OutreachLog", back_populates="artist")

class Track(Base):
    """Track model"""
    __tablename__ = "tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    isrc = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    artist_id = Column(Integer, ForeignKey("artists.id"))
    spotify_track_id = Column(String(100))
    youtube_video_id = Column(String(100))
    apple_music_id = Column(String(100))
    musicbrainz_recording_id = Column(String(100))
    release_date = Column(DateTime)
    label = Column(String(255))
    duration_ms = Column(Integer)
    explicit = Column(Boolean, default=False)
    spotify_popularity = Column(Integer)
    spotify_play_count = Column(Integer)
    youtube_view_count = Column(Integer)
    lastfm_play_count = Column(Integer)
    platforms_available = Column(JSON)
    missing_platforms = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    artist = relationship("Artist", back_populates="tracks")

class ContactAttempt(Base):
    """Contact discovery attempts and results"""
    __tablename__ = "contact_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    artist_id = Column(Integer, ForeignKey("artists.id"))
    contact_method = Column(String(50))
    contact_value = Column(String(500))
    confidence_score = Column(Integer)
    source = Column(String(100))
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    artist = relationship("Artist", back_populates="contacts")

class OutreachLog(Base):
    """Track outreach attempts and responses"""
    __tablename__ = "outreach_log"
    
    id = Column(Integer, primary_key=True, index=True)
    artist_id = Column(Integer, ForeignKey("artists.id"))
    contact_date = Column(DateTime)
    method = Column(String(50))
    message_template = Column(String(100))
    response_received = Column(Boolean, default=False)
    response_date = Column(DateTime)
    conversion_status = Column(String(50))
    follow_up_scheduled = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    artist = relationship("Artist", back_populates="outreach_logs")

class ProcessingQueue(Base):
    """Queue for batch processing of ISRCs"""
    __tablename__ = "processing_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    isrc = Column(String(20), nullable=False, index=True)
    status = Column(String(20), default='pending')
    priority = Column(Integer, default=1)
    result_data = Column(JSON)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database and create tables"""
    os.makedirs('data', exist_ok=True)
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

def reset_db():
    """Reset database - DROP ALL TABLES and recreate"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database reset completed!")

def migrate_youtube_fields():
    """Add YouTube fields to existing database - MIGRATION FUNCTION"""
    from sqlalchemy import text
    
    migration_sql = [
        "ALTER TABLE artists ADD COLUMN youtube_channel_id VARCHAR(100);",
        "ALTER TABLE artists ADD COLUMN youtube_channel_url VARCHAR(500);",
        "ALTER TABLE artists ADD COLUMN youtube_subscribers INTEGER DEFAULT 0;",
        "ALTER TABLE artists ADD COLUMN youtube_total_views INTEGER DEFAULT 0;",
        "ALTER TABLE artists ADD COLUMN youtube_video_count INTEGER DEFAULT 0;",
        "ALTER TABLE artists ADD COLUMN youtube_upload_frequency VARCHAR(20);",
        "ALTER TABLE artists ADD COLUMN youtube_engagement_rate FLOAT DEFAULT 0.0;",
        "ALTER TABLE artists ADD COLUMN youtube_growth_potential VARCHAR(20);",
        "ALTER TABLE artists ADD COLUMN youtube_last_upload DATETIME;"
    ]
    
    try:
        with engine.connect() as conn:
            for sql in migration_sql:
                try:
                    conn.execute(text(sql))
                    print(f"✅ Executed: {sql}")
                except Exception as e:
                    if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                        print(f"⚠️ Column already exists, skipping: {sql}")
                    else:
                        print(f"❌ Error executing {sql}: {e}")
                        raise e
            conn.commit()
        print("✅ YouTube fields migration completed successfully!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")

class DatabaseManager:
    """Database operations manager with YouTube integration - COMPLETE VERSION"""
    
    def __init__(self):
        self._session = None
    
    @property
    def session(self):
        if self._session is None:
            self._session = SessionLocal()
        return self._session
    
    def close(self):
        if self._session:
            self._session.close()
            self._session = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()
        self.close()
    
    def save_artist_data(self, artist_data: dict) -> int:
        """Save processed artist data to database with YouTube integration"""
        try:
            existing_artist = self.session.query(Artist).filter_by(
                name=artist_data.get('name')
            ).first()
            
            if existing_artist:
                final_artist_id = self._update_artist_safe(existing_artist, artist_data)
            else:
                final_artist_id = self._create_artist_safe(artist_data)
            
            # These calls are now guaranteed to use pure int types
            if artist_data.get('track_data'):
                self._save_track_data_safe(final_artist_id, artist_data['track_data'])
            
            if artist_data.get('contacts'):
                self._save_contacts_safe(final_artist_id, artist_data['contacts'])
            
            return final_artist_id
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def _create_artist_safe(self, data: dict) -> int:
        """Create new artist with YouTube data"""
        scores = data.get('scores', {})
        
        artist = Artist(
            name=data.get('name') or "Unknown Artist",
            musicbrainz_id=data.get('musicbrainz_id'),
            spotify_id=data.get('spotify_id'),
            country=data.get('country'),
            region=data.get('region') or "unknown",
            genre=data.get('genre'),
            independence_score=scores.get('independence_score', 0),
            opportunity_score=scores.get('opportunity_score', 0),
            geographic_score=scores.get('geographic_score', 0),
            total_score=float(scores.get('total_score', 0.0)),
            lead_tier=scores.get('tier', 'D'),
            monthly_listeners=self._safe_int(data.get('monthly_listeners', 0)),
            
            # NEW: YouTube fields
            youtube_channel_id=data.get('youtube_channel_id'),
            youtube_channel_url=data.get('youtube_channel_url'),
            youtube_subscribers=self._safe_int(data.get('youtube_subscribers', 0)),
            youtube_total_views=self._safe_int(data.get('youtube_total_views', 0)),
            youtube_video_count=self._safe_int(data.get('youtube_video_count', 0)),
            youtube_upload_frequency=data.get('youtube_upload_frequency'),
            youtube_engagement_rate=self._safe_float(data.get('youtube_engagement_rate', 0.0)),
            youtube_growth_potential=data.get('youtube_growth_potential'),
            youtube_last_upload=self._parse_datetime(data.get('youtube_last_upload')),
            
            last_scraped=datetime.utcnow()
        )
        
        self.session.add(artist)
        self.session.flush()
        
        # Explicitly cast to int to satisfy type checker
        return cast(int, artist.id)
    
    def _update_artist_safe(self, artist: Artist, data: dict) -> int:
        """Update existing artist with YouTube data"""
        # Direct assignment works fine for updates
        artist.updated_at = datetime.utcnow()  # type: ignore
        artist.last_scraped = datetime.utcnow()  # type: ignore
        
        if data.get('scores'):
            scores = data['scores']
            artist.independence_score = scores.get('independence_score', artist.independence_score)  # type: ignore
            artist.opportunity_score = scores.get('opportunity_score', artist.opportunity_score)  # type: ignore
            artist.geographic_score = scores.get('geographic_score', artist.geographic_score)  # type: ignore
            artist.total_score = scores.get('total_score', artist.total_score)  # type: ignore
            artist.lead_tier = scores.get('tier', artist.lead_tier)  # type: ignore
        
        if data.get('monthly_listeners'):
            artist.monthly_listeners = data['monthly_listeners']  # type: ignore
        if data.get('country'):
            artist.country = data['country']  # type: ignore
        if data.get('region'):
            artist.region = data['region']  # type: ignore
        if data.get('genre'):
            artist.genre = data['genre']  # type: ignore
        
        # NEW: Update YouTube fields if present
        if data.get('youtube_channel_id'):
            artist.youtube_channel_id = data['youtube_channel_id']  # type: ignore
        if data.get('youtube_channel_url'):
            artist.youtube_channel_url = data['youtube_channel_url']  # type: ignore
        if data.get('youtube_subscribers') is not None:
            artist.youtube_subscribers = self._safe_int(data['youtube_subscribers'])  # type: ignore
        if data.get('youtube_total_views') is not None:
            artist.youtube_total_views = self._safe_int(data['youtube_total_views'])  # type: ignore
        if data.get('youtube_video_count') is not None:
            artist.youtube_video_count = self._safe_int(data['youtube_video_count'])  # type: ignore
        if data.get('youtube_upload_frequency'):
            artist.youtube_upload_frequency = data['youtube_upload_frequency']  # type: ignore
        if data.get('youtube_engagement_rate') is not None:
            artist.youtube_engagement_rate = self._safe_float(data['youtube_engagement_rate'])  # type: ignore
        if data.get('youtube_growth_potential'):
            artist.youtube_growth_potential = data['youtube_growth_potential']  # type: ignore
        if data.get('youtube_last_upload'):
            artist.youtube_last_upload = self._parse_datetime(data['youtube_last_upload'])  # type: ignore
        
        # Explicitly cast to int to satisfy type checker
        return cast(int, artist.id)
    
    def _save_track_data_safe(self, artist_id_int: int, track_data: dict) -> None:
        """Save track data - artist_id_int is guaranteed to be int"""
        isrc = track_data.get('isrc')
        if not isrc:
            return
        
        existing_track = self.session.query(Track).filter_by(isrc=isrc).first()
        
        if existing_track:
            existing_track.updated_at = datetime.utcnow()  # type: ignore
            if track_data.get('title'):
                existing_track.title = str(track_data['title'])  # type: ignore
            if track_data.get('spotify_track_id'):
                existing_track.spotify_track_id = str(track_data['spotify_track_id'])  # type: ignore
            if track_data.get('spotify_popularity'):
                existing_track.spotify_popularity = self._safe_int(track_data['spotify_popularity'])  # type: ignore
        else:
            track = Track(
                isrc=str(isrc),
                title=track_data.get('title') or "Unknown Track",
                artist_id=artist_id_int,  # This is guaranteed to be int
                spotify_track_id=track_data.get('spotify_track_id'),
                musicbrainz_recording_id=track_data.get('musicbrainz_recording_id'),
                release_date=self._parse_datetime(track_data.get('release_date')),
                label=track_data.get('label'),
                duration_ms=self._safe_int(track_data.get('duration_ms')),
                spotify_popularity=self._safe_int(track_data.get('spotify_popularity')),
                platforms_available=track_data.get('platforms_available', []),
                missing_platforms=track_data.get('missing_platforms', [])
            )
            self.session.add(track)
    
    def _save_contacts_safe(self, artist_id_int: int, contacts: list) -> None:
        """Save contacts - artist_id_int is guaranteed to be int"""
        for contact in contacts:
            existing_contact = self.session.query(ContactAttempt).filter_by(
                artist_id=artist_id_int,  # This is guaranteed to be int
                contact_method=contact.get('type'),
                contact_value=contact.get('value')
            ).first()
            
            if not existing_contact:
                contact_attempt = ContactAttempt(
                    artist_id=artist_id_int,  # This is guaranteed to be int
                    contact_method=contact.get('type'),
                    contact_value=contact.get('value'),
                    confidence_score=contact.get('confidence', 50),
                    source=contact.get('source')
                )
                self.session.add(contact_attempt)
    
    def _safe_int(self, value) -> int:
        """Safely convert value to integer"""
        if value is None:
            return 0
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0
    
    def _safe_float(self, value) -> float:
        """Safely convert value to float"""
        if value is None:
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _parse_datetime(self, date_str):
        """Parse datetime string safely"""
        if not date_str:
            return None
        try:
            formats = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m', '%Y']
            for fmt in formats:
                try:
                    return datetime.strptime(str(date_str), fmt)
                except ValueError:
                    continue
        except Exception:
            pass
        return None
    
    def get_leads(self, tier=None, region=None, youtube_filter=None, limit=50, offset=0):
        """Get filtered lead list with YouTube filtering options"""
        query = self.session.query(Artist)
        if tier:
            query = query.filter(Artist.lead_tier == tier)
        if region:
            query = query.filter(Artist.region == region)
        
        # NEW: YouTube filtering options
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
        
        query = query.order_by(Artist.total_score.desc())
        query = query.offset(offset).limit(limit)
        return query.all()
    
    def get_artist_by_id(self, artist_id: int):
        """Get artist by ID"""
        return self.session.query(Artist).filter_by(id=artist_id).first()
    
    def get_tracks_by_artist(self, artist_id: int):
        """Get tracks for an artist"""
        return self.session.query(Track).filter_by(artist_id=artist_id).all()
    
    def get_contacts_by_artist(self, artist_id: int):
        """Get contacts for an artist"""
        return self.session.query(ContactAttempt).filter_by(artist_id=artist_id).all()
    
    def update_outreach_status(self, artist_id: int, status: str):
        """Update outreach status for an artist"""
        artist = self.session.query(Artist).filter_by(id=artist_id).first()
        if artist:
            artist.outreach_status = status  # type: ignore
            artist.updated_at = datetime.utcnow()  # type: ignore
            self.session.commit()
    
    def get_dashboard_stats(self):
        """Get dashboard statistics including YouTube metrics"""
        try:
            from sqlalchemy import func
            total_artists = self.session.query(Artist).count()
            tier_counts = {}
            for tier in ['A', 'B', 'C', 'D']:
                count = self.session.query(Artist).filter_by(lead_tier=tier).count()
                tier_counts[tier] = count
            region_query = self.session.query(
                Artist.region, func.count(Artist.id)
            ).group_by(Artist.region).all()
            region_counts = {region: count for region, count in region_query if region}
            
            # NEW: YouTube statistics
            youtube_stats = {
                'artists_with_youtube': self.session.query(Artist).filter(Artist.youtube_channel_id.isnot(None)).count(),
                'total_youtube_subscribers': self.session.query(func.sum(Artist.youtube_subscribers)).scalar() or 0,
                'avg_youtube_subscribers': self.session.query(func.avg(Artist.youtube_subscribers)).filter(Artist.youtube_subscribers > 0).scalar() or 0,
                'high_potential_channels': self.session.query(Artist).filter_by(youtube_growth_potential='high_potential').count()
            }
            
            return {
                'total_artists': total_artists,
                'tier_distribution': tier_counts,
                'region_distribution': region_counts,
                'youtube_statistics': youtube_stats
            }
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {
                'total_artists': 0,
                'tier_distribution': {},
                'region_distribution': {},
                'youtube_statistics': {}
            }
    
    def get_youtube_opportunities(self, limit=20):
        """Get artists with YouTube opportunities for targeted outreach"""
        try:
            # Artists with no YouTube presence but good Spotify following
            no_youtube = self.session.query(Artist).filter(
                Artist.youtube_channel_id.is_(None),
                Artist.monthly_listeners > 5000
            ).order_by(Artist.monthly_listeners.desc()).limit(limit//2).all()
            
            # Artists with underperforming YouTube relative to Spotify
            underperforming = self.session.query(Artist).filter(
                Artist.youtube_channel_id.isnot(None),
                Artist.monthly_listeners > 10000,
                Artist.youtube_subscribers < Artist.monthly_listeners * 0.3
            ).order_by(Artist.total_score.desc()).limit(limit//2).all()
            
            return {
                'no_youtube_presence': no_youtube,
                'underperforming_youtube': underperforming
            }
        except Exception as e:
            print(f"Error getting YouTube opportunities: {e}")
            return {'no_youtube_presence': [], 'underperforming_youtube': []}
    
    def update_youtube_data(self, artist_id: int, youtube_data: dict):
        """Update YouTube data for a specific artist"""
        try:
            artist = self.session.query(Artist).filter_by(id=artist_id).first()
            if not artist:
                return False
            
            # Update YouTube fields
            artist.youtube_channel_id = youtube_data.get('channel_id')  # type: ignore
            artist.youtube_channel_url = youtube_data.get('channel_url')  # type: ignore
            artist.youtube_subscribers = self._safe_int(youtube_data.get('subscribers', 0))  # type: ignore
            artist.youtube_total_views = self._safe_int(youtube_data.get('total_views', 0))  # type: ignore
            artist.youtube_video_count = self._safe_int(youtube_data.get('video_count', 0))  # type: ignore
            artist.youtube_upload_frequency = youtube_data.get('upload_frequency')  # type: ignore
            artist.youtube_engagement_rate = self._safe_float(youtube_data.get('engagement_rate', 0.0))  # type: ignore
            artist.youtube_growth_potential = youtube_data.get('growth_potential')  # type: ignore
            artist.youtube_last_upload = self._parse_datetime(youtube_data.get('last_upload'))  # type: ignore
            artist.updated_at = datetime.utcnow()  # type: ignore
            
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error updating YouTube data: {e}")
            self.session.rollback()
            return False
    
    def __del__(self):
        self.close()

# Database setup and migration functions
def check_youtube_migration_needed():
    """Check if YouTube migration is needed"""
    try:
        with engine.connect() as conn:
            # Try to select a YouTube column
            result = conn.execute(text("SELECT youtube_channel_id FROM artists LIMIT 1"))
            return False  # Migration already done
    except Exception:
        return True  # Migration needed

def run_youtube_migration_if_needed():
    """Run YouTube migration only if needed"""
    if check_youtube_migration_needed():
        print("YouTube migration needed, running...")
        migrate_youtube_fields()
    else:
        print("YouTube fields already exist, skipping migration")

if __name__ == "__main__":
    # Check if we need to run migration
    if check_youtube_migration_needed():
        print("YouTube migration required!")
        migrate_youtube_fields()
    else:
        print("Database schema up to date")
    
    # Initialize database
    init_db()