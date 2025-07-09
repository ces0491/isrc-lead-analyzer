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
    """Database operations manager"""
    
    def __init__(self):
        self.session = SessionLocal()
    
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
            
            self.session.commit()
            return artist_id
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def _create_artist(self, data: dict) -> int:
        """Create new artist record"""
        artist = Artist(
            name=data.get('name'),
            musicbrainz_id=data.get('musicbrainz_id'),
            spotify_id=data.get('spotify_id'),
            country=data.get('country'),
            region=data.get('region'),
            genre=data.get('genre'),
            independence_score=data.get('scores', {}).get('independence_score', 0),
            opportunity_score=data.get('scores', {}).get('opportunity_score', 0),
            geographic_score=data.get('scores', {}).get('geographic_score', 0),
            total_score=data.get('scores', {}).get('total_score', 0),
            lead_tier=data.get('scores', {}).get('tier', 'D'),
            monthly_listeners=data.get('monthly_listeners', 0),
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
    
    def _save_track_data(self, artist_id: int, track_data: dict):
        """Save track information"""
        isrc = track_data.get('isrc')
        if not isrc:
            return
        
        # Check if track already exists
        existing_track = self.session.query(Track).filter_by(isrc=isrc).first()
        
        if existing_track:
            existing_track.updated_at = datetime.utcnow()
        else:
            track = Track(
                isrc=isrc,
                title=track_data.get('title'),
                artist_id=artist_id,
                spotify_track_id=track_data.get('spotify_track_id'),
                musicbrainz_recording_id=track_data.get('musicbrainz_recording_id'),
                release_date=track_data.get('release_date'),
                label=track_data.get('label'),
                duration_ms=track_data.get('duration_ms'),
                spotify_popularity=track_data.get('spotify_popularity'),
                platforms_available=track_data.get('platforms_available', []),
                missing_platforms=track_data.get('missing_platforms', [])
            )
            self.session.add(track)
    
    def _save_contacts(self, artist_id: int, contacts: list):
        """Save contact discovery results"""
        for contact in contacts:
            contact_attempt = ContactAttempt(
                artist_id=artist_id,
                contact_method=contact.get('type'),
                contact_value=contact.get('value'),
                confidence_score=contact.get('confidence', 50),
                source=contact.get('source')
            )
            self.session.add(contact_attempt)
    
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
    
    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()

if __name__ == "__main__":
    # Initialize database if run directly
    init_db()