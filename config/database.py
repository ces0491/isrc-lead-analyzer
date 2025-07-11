"""
Database configuration and models for Precise Digital Lead Generation Tool
"""
import os
import sqlite3
from datetime import datetime
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
    """Artist model"""
    __tablename__ = "artists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    
    # External IDs
    musicbrainz_id = Column(String(100), unique=True, index=True)
    spotify_id = Column(String(100), unique=True, index=True)
    
    # Geographic info
    country = Column(String(50))
    region = Column(String(100))
    
    # Genre and metadata
    genre = Column(String(100))
    subgenre = Column(String(100))
    
    # Scoring
    independence_score = Column(Integer, default=0)
    opportunity_score = Column(Integer, default=0)
    geographic_score = Column(Integer, default=0)
    total_score = Column(Float, default=0.0)
    lead_tier = Column(String(1))  # A, B, C, D
    
    # Contact information
    contact_email = Column(String(255))
    website = Column(String(500))
    social_handles = Column(JSON)  # Store as JSON: {"instagram": "handle", "twitter": "handle"}
    management_contact = Column(String(255))
    
    # Metrics from platforms
    monthly_listeners = Column(Integer, default=0)
    follower_count = Column(Integer, default=0)
    release_count = Column(Integer, default=0)
    last_release_date = Column(DateTime)
    
    # System fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped = Column(DateTime)
    outreach_status = Column(String(50), default='not_contacted')
    
    # Relationships
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
    
    # External IDs
    spotify_track_id = Column(String(100))
    youtube_video_id = Column(String(100))
    apple_music_id = Column(String(100))
    musicbrainz_recording_id = Column(String(100))
    
    # Metadata
    release_date = Column(DateTime)
    label = Column(String(255))
    duration_ms = Column(Integer)
    explicit = Column(Boolean, default=False)
    
    # Metrics
    spotify_popularity = Column(Integer)
    spotify_play_count = Column(Integer)
    youtube_view_count = Column(Integer)
    lastfm_play_count = Column(Integer)
    
    # Distribution analysis
    platforms_available = Column(JSON)  # List of platforms where track is available
    missing_platforms = Column(JSON)    # List of major platforms where track is missing
    
    # System fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    artist = relationship("Artist", back_populates="tracks")

class ContactAttempt(Base):
    """Contact discovery attempts and results"""
    __tablename__ = "contact_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    artist_id = Column(Integer, ForeignKey("artists.id"))
    
    contact_method = Column(String(50))  # email, social, website_form
    contact_value = Column(String(500))  # The actual contact info found
    confidence_score = Column(Integer)   # 1-100 confidence in accuracy
    source = Column(String(100))         # Which API/method found it
    verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    artist = relationship("Artist", back_populates="contacts")

class OutreachLog(Base):
    """Track outreach attempts and responses"""
    __tablename__ = "outreach_log"
    
    id = Column(Integer, primary_key=True, index=True)
    artist_id = Column(Integer, ForeignKey("artists.id"))
    
    contact_date = Column(DateTime)
    method = Column(String(50))  # email, social_dm, etc
    message_template = Column(String(100))
    
    response_received = Column(Boolean, default=False)
    response_date = Column(DateTime)
    conversion_status = Column(String(50))  # interested, not_interested, no_response
    
    follow_up_scheduled = Column(DateTime)
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    artist = relationship("Artist", back_populates="outreach_logs")

class ProcessingQueue(Base):
    """Queue for batch processing of ISRCs"""
    __tablename__ = "processing_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    isrc = Column(String(20), nullable=False, index=True)
    status = Column(String(20), default='pending')  # pending, processing, completed, failed
    priority = Column(Integer, default=1)  # 1=low, 5=high
    
    # Results
    result_data = Column(JSON)  # Store the processing result
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

# Database utility functions
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database and create tables"""
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

def reset_db():
    """Reset database - DROP ALL TABLES and recreate"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database reset completed!")

class DatabaseManager:
    """Database operations manager with proper session handling"""
    
    def __init__(self):
        self._session = None
    
    @property
    def session(self):
        """Get or create database session"""
        if self._session is None:
            self._session = SessionLocal()
        return self._session
    
    def close(self):
        """Close database session"""
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
        """Save processed artist data to database"""
        try:
            # Check if artist already exists
            existing_artist = self.session.query(Artist).filter_by(
                name=artist_data.get('name')
            ).first()
            
            if existing_artist:
                # Update existing artist
                self._update_artist(existing_artist, artist_data)
                artist_id = existing_artist.id
            else:
                # Create new artist
                artist_id = self._create_artist(artist_data)
            
            # Save track data if provided
            if artist_data.get('track_data'):
                self._save_track_data(artist_id, artist_data['track_data'])
            
            # Save contact attempts if provided
            if artist_data.get('contacts'):
                self._save_contacts(artist_id, artist_data['contacts'])
            
            return artist_id
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def _create_artist(self, data: dict) -> int:
        """Create new artist record"""
        scores = data.get('scores', {})
        
        # Safely extract string values with defaults
        name = data.get('name') or "Unknown Artist"
        musicbrainz_id = data.get('musicbrainz_id') or None
        spotify_id = data.get('spotify_id') or None
        country = data.get('country') or None
        region = data.get('region') or "unknown"
        genre = data.get('genre') or None
        
        # Safely extract numeric values
        monthly_listeners = self._safe_int(data.get('monthly_listeners', 0))
        
        artist = Artist(
            name=name,
            musicbrainz_id=musicbrainz_id,
            spotify_id=spotify_id,
            country=country,
            region=region,
            genre=genre,
            independence_score=scores.get('independence_score', 0),
            opportunity_score=scores.get('opportunity_score', 0),
            geographic_score=scores.get('geographic_score', 0),
            total_score=scores.get('total_score', 0.0),
            lead_tier=scores.get('tier', 'D'),
            monthly_listeners=monthly_listeners,
            last_scraped=datetime.utcnow()
        )
        
        self.session.add(artist)
        self.session.flush()  # Get the ID
        return artist.id
    
    def _update_artist(self, artist: Artist, data: dict):
        """Update existing artist record"""
        artist.updated_at = datetime.utcnow()
        artist.last_scraped = datetime.utcnow()
        
        # Update scores if provided
        if data.get('scores'):
            scores = data['scores']
            artist.independence_score = scores.get('independence_score', artist.independence_score)
            artist.opportunity_score = scores.get('opportunity_score', artist.opportunity_score)
            artist.geographic_score = scores.get('geographic_score', artist.geographic_score)
            artist.total_score = scores.get('total_score', artist.total_score)
            artist.lead_tier = scores.get('tier', artist.lead_tier)
        
        # Update metrics if provided
        if data.get('monthly_listeners'):
            artist.monthly_listeners = data['monthly_listeners']
        
        # Update other fields
        if data.get('country'):
            artist.country = data['country']
        if data.get('region'):
            artist.region = data['region']
        if data.get('genre'):
            artist.genre = data['genre']
    
    def _save_track_data(self, artist_id: int, track_data: dict):
        """Save track information"""
        isrc = track_data.get('isrc')
        if not isrc:
            return
        
        # Clean and validate required fields
        title = track_data.get('title') or "Unknown Track"
        
        # Check if track already exists
        existing_track = self.session.query(Track).filter_by(isrc=isrc).first()
        
        if existing_track:
            existing_track.updated_at = datetime.utcnow()
            if track_data.get('title'):
                existing_track.title = str(track_data['title'])
            if track_data.get('spotify_track_id'):
                existing_track.spotify_track_id = str(track_data['spotify_track_id'])
            if track_data.get('spotify_popularity'):
                existing_track.spotify_popularity = self._safe_int(track_data['spotify_popularity'])
        else:
            track = Track(
                isrc=str(isrc),
                title=title,
                artist_id=artist_id,
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
    
    def _safe_int(self, value) -> int:
        """Safely convert value to integer, return 0 if not possible"""
        if value is None:
            return 0
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0
    
    def _save_contacts(self, artist_id: int, contacts: list):
        """Save contact discovery results"""
        for contact in contacts:
            # Check if contact already exists
            existing_contact = self.session.query(ContactAttempt).filter_by(
                artist_id=artist_id,
                contact_method=contact.get('type'),
                contact_value=contact.get('value')
            ).first()
            
            if not existing_contact:
                contact_attempt = ContactAttempt(
                    artist_id=artist_id,
                    contact_method=contact.get('type'),
                    contact_value=contact.get('value'),
                    confidence_score=contact.get('confidence', 50),
                    source=contact.get('source')
                )
                self.session.add(contact_attempt)
    
    def _parse_datetime(self, date_str):
        """Parse datetime string safely"""
        if not date_str:
            return None
        
        try:
            # Try common formats
            formats = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m', '%Y']
            for fmt in formats:
                try:
                    return datetime.strptime(str(date_str), fmt)
                except ValueError:
                    continue
        except Exception:
            pass
        
        return None
    
    def get_leads(self, tier=None, region=None, limit=50, offset=0):
        """Get filtered lead list"""
        query = self.session.query(Artist)
        
        if tier:
            query = query.filter(Artist.lead_tier == tier)
        if region:
            query = query.filter(Artist.region == region)
        
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
            artist.outreach_status = status
            artist.updated_at = datetime.utcnow()
            self.session.commit()
    
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        try:
            from sqlalchemy import func
            
            total_artists = self.session.query(Artist).count()
            
            # Get tier distribution
            tier_counts = {}
            for tier in ['A', 'B', 'C', 'D']:
                count = self.session.query(Artist).filter_by(lead_tier=tier).count()
                tier_counts[tier] = count
            
            # Get region distribution
            region_query = self.session.query(
                Artist.region, func.count(Artist.id)
            ).group_by(Artist.region).all()
            
            region_counts = {region: count for region, count in region_query if region}
            
            return {
                'total_artists': total_artists,
                'tier_distribution': tier_counts,
                'region_distribution': region_counts
            }
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {
                'total_artists': 0,
                'tier_distribution': {},
                'region_distribution': {}
            }
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()

if __name__ == "__main__":
    # Initialize database if run directly
    init_db()